"""Servicio de sincronización con APIs externas."""

import asyncio
import time
from collections.abc import Sequence
from datetime import datetime
from decimal import Decimal
from typing import TypedDict

from transferplayer.api.football_data import FootballAPIError, football_client
from transferplayer.db.repository import get_sync_log_repo, get_transfer_repo
from transferplayer.models.domain import TransferCreate
from transferplayer.models.orm import SyncLog


class SyncStats(TypedDict):
    """Estadísticas de una sincronización con API externa."""

    source: str
    endpoint: str
    season: int
    status: str
    dry_run: bool
    leagues_processed: int
    teams_processed: int
    records_fetched: int
    records_inserted: int
    records_updated: int
    duration_ms: int
    errors: list[str]


class SyncService:
    """Orquesta la sincronización de datos externos."""

    def __init__(self) -> None:
        self.client = football_client

    async def sync_all_leagues(self, season: int | None = None, dry_run: bool = False) -> SyncStats:
        """
        Sincroniza traspasos de las 5 grandes ligas en un único pase.

        Obtiene equipos y traspasos de la API una sola vez y realiza el
        upsert en BD. Si ``dry_run`` es True sólo cuenta lo que se habría
        procesado, sin tocar la BD ni registrar logs.

        Returns: dict con estadísticas del sync.
        """
        start_time = time.perf_counter()
        season = season or datetime.now().year

        stats: SyncStats = {
            "source": "api-football",
            "endpoint": "/transfers (top 5 leagues)",
            "season": season,
            "status": "success",
            "dry_run": dry_run,
            "leagues_processed": 0,
            "teams_processed": 0,
            "records_fetched": 0,
            "records_inserted": 0,
            "records_updated": 0,
            "duration_ms": 0,
            "errors": [],
        }

        try:
            # Un único pase: teams + transfers + upsert por liga/equipo
            for league_id, league_name in self.client.TOP_5_LEAGUES.items():
                try:
                    teams = await self.client.get_teams(league_id, season)
                    stats["leagues_processed"] += 1

                    for team in teams:
                        try:
                            raw_transfers = await self.client.get_transfers(team.id, season)
                            stats["teams_processed"] += 1

                            for raw in raw_transfers:
                                stats["records_fetched"] += 1
                                transfer_data = self._parse_transfer(raw, league_name, team.name)
                                if transfer_data is None:
                                    continue

                                if dry_run:
                                    continue

                                async with get_transfer_repo() as repo:
                                    _, created = await repo.upsert_from_api(transfer_data)
                                    if created:
                                        stats["records_inserted"] += 1
                                    else:
                                        stats["records_updated"] += 1

                            await asyncio.sleep(0.05)  # Rate limit courteous

                        except FootballAPIError as e:
                            stats["errors"].append(f"Team {team.name}: {e}")
                            continue

                except FootballAPIError as e:
                    stats["errors"].append(f"League {league_name}: {e}")
                    continue

            if stats["errors"]:
                stats["status"] = "partial"

        except FootballAPIError as e:
            stats["status"] = "error"
            stats["errors"].append(str(e))
        except Exception as e:
            stats["status"] = "error"
            stats["errors"].append(f"Unexpected: {e}")
        finally:
            stats["duration_ms"] = int((time.perf_counter() - start_time) * 1000)
            if not dry_run:
                await self._log_sync(stats)

        return stats

    def _parse_transfer(self, raw: dict, league: str, team_name: str) -> TransferCreate | None:
        """
        Parsea respuesta de API-Football a TransferCreate.
        Estructura típica de /transfers:
        {
          "player": {"id": 123, "name": "Player Name", "age": 25, "position": "Forward", ...},
          "transfers": [
            {
              "date": "2024-07-01",
              "type": "Transfer",
              "teams": {"in": {"id": 456, "name": "New Club"}, "out": {"id": 789, "name": "Old Club"}},
              "fee": "€50.00M"
            }
          ]
        }
        """
        try:
            player = raw.get("player", {})
            transfers = raw.get("transfers", [])
            if not transfers:
                return None

            # Tomar el último traspaso (más reciente)
            latest = transfers[-1]
            teams = latest.get("teams", {})
            team_in = teams.get("in", {})
            team_out = teams.get("out", {})

            # Parsear fee
            fee_str = latest.get("fee", "€0M")
            valor = self._parse_fee(fee_str)

            # Mapear posición
            position_map = {
                "Goalkeeper": "Portero",
                "Defender": "Defensa",
                "Midfielder": "Centrocampista",
                "Attacker": "Delantero",
            }
            posicion = position_map.get(player.get("position", "Midfielder"), "Centrocampista")

            # Mapear tipo
            type_map = {
                "Transfer": "Traspaso Definitivo",
                "Loan": "Cesión",
                "Free": "Traspaso Libre",
            }
            tipo = type_map.get(latest.get("type", "Transfer"), "Traspaso Definitivo")

            return TransferCreate(
                jugador=player.get("name", "Unknown"),
                edad=player.get("age", 25),
                posicion=posicion,
                liga=league,
                club_origen=team_out.get("name", "Unknown"),
                club_destino=team_in.get("name", team_name),
                valor=valor,
                tipo=tipo,
            )
        except Exception:
            return None

    def _parse_fee(self, fee_str: str) -> Decimal:
        """Parsea '€50.00M' -> Decimal('50.00')."""
        try:
            cleaned = fee_str.replace("€", "").replace("M", "").replace(",", "").strip()
            if cleaned in ("", "-", "?"):
                return Decimal("0")
            return Decimal(cleaned)
        except Exception:
            return Decimal("0")

    async def _log_sync(self, stats: SyncStats) -> None:
        """Guarda log de sincronización en BD."""
        async with get_sync_log_repo() as repo:
            await repo.create_log(
                source=stats["source"],
                endpoint=stats["endpoint"],
                status=stats["status"],
                records_fetched=stats["records_fetched"],
                records_inserted=stats["records_inserted"],
                records_updated=stats["records_updated"],
                error_message="; ".join(stats["errors"]) if stats["errors"] else None,
                duration_ms=stats["duration_ms"],
            )

    async def get_sync_history(self, limit: int = 20) -> Sequence[SyncLog]:
        async with get_sync_log_repo() as repo:
            return await repo.get_recent(limit)


sync_service = SyncService()
