"""Cliente para API-Football (RapidAPI)."""
import asyncio
from datetime import date, datetime

import httpx
from pydantic import BaseModel

from transferplayer.config import settings


class RateLimiter:
    """Rate limiter simple para 100 req/día (API-Football free)."""

    def __init__(self, max_per_day: int = 100):
        self.max_per_day = max_per_day
        self.requests_today = 0
        self.last_reset = date.today()

    async def acquire(self) -> None:
        today = date.today()
        if today != self.last_reset:
            self.requests_today = 0
            self.last_reset = today

        if self.requests_today >= self.max_per_day:
            raise RuntimeError(
                f"Rate limit diario alcanzado ({self.max_per_day} req/día). "
                f"Reset a medianoche UTC."
            )

        self.requests_today += 1


rate_limiter = RateLimiter(max_per_day=100)


class FootballAPIError(Exception):
    """Error de API-Football."""
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class Competition(BaseModel):
    id: int
    name: str
    code: str
    type: str
    emblem: str | None = None


class Team(BaseModel):
    id: int
    name: str
    logo: str | None = None


class TransferResponse(BaseModel):
    """Respuesta de transferencias de API-Football."""
    player: dict
    transfers: list[dict]


class FootballDataClient:
    """Cliente async para API-Football v3."""

    BASE_URL = "https://v3.football.api-sports.io"

    # IDs de las 5 grandes ligas en API-Football
    TOP_5_LEAGUES = {
        39: "Premier League",
        140: "La Liga",
        135: "Serie A",
        78: "Bundesliga",
        61: "Ligue 1",
    }

    def __init__(self, api_key: str | None = None, host: str | None = None):
        self.api_key = api_key or settings.football_api_key
        self.host = host or settings.football_api_host
        if not self.api_key:
            raise ValueError("FOOTBALL_API_KEY requerido")

        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                headers={
                    "X-RapidAPI-Key": self.api_key,
                    "X-RapidAPI-Host": self.host,
                },
                timeout=30.0,
            )
        return self._client

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _request(self, endpoint: str, params: dict | None = None) -> dict:
        """Request con rate limiting y retry."""
        await rate_limiter.acquire()

        max_retries = 3
        for attempt in range(max_retries):
            try:
                resp = await self.client.get(endpoint, params=params)
                if resp.status_code == 429:
                    # Rate limited - wait and retry
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                    continue
                resp.raise_for_status()
                data = resp.json()
                if data.get("errors"):
                    raise FootballAPIError(str(data["errors"]), resp.status_code)
                return data
            except httpx.HTTPStatusError as e:
                if attempt == max_retries - 1:
                    raise FootballAPIError(f"HTTP {e.response.status_code}: {e.response.text}", e.response.status_code)
                await asyncio.sleep(2 ** attempt)
            except httpx.RequestError as e:
                if attempt == max_retries - 1:
                    raise FootballAPIError(f"Request error: {e}")
                await asyncio.sleep(2 ** attempt)

        raise FootballAPIError("Max retries exceeded")

    async def get_competitions(self) -> list[Competition]:
        """Obtiene competiciones disponibles."""
        data = await self._request("/leagues")
        return [Competition(**c["league"]) for c in data.get("response", [])]

    async def get_teams(self, league_id: int, season: int) -> list[Team]:
        """Obtiene equipos de una liga/temporada."""
        data = await self._request("/teams", params={"league": league_id, "season": season})
        return [Team(**t["team"]) for t in data.get("response", [])]

    async def get_transfers(self, team_id: int, season: int) -> list[dict]:
        """Obtiene traspasos de un equipo en una temporada."""
        data = await self._request("/transfers", params={"team": team_id, "season": season})
        return data.get("response", [])

    async def get_players(self, team_id: int, season: int) -> list[dict]:
        """Obtiene plantilla de un equipo."""
        data = await self._request("/players", params={"team": team_id, "season": season})
        return data.get("response", [])

    async def sync_top5_leagues_transfers(self, season: int | None = None) -> dict:
        """
        Sincroniza traspasos de las 5 grandes ligas.
        Returns: stats dict
        """
        season = season or datetime.now().year
        stats = {
            "leagues_processed": 0,
            "teams_processed": 0,
            "transfers_fetched": 0,
            "errors": [],
        }

        for league_id, league_name in self.TOP_5_LEAGUES.items():
            try:
                teams = await self.get_teams(league_id, season)
                stats["leagues_processed"] += 1

                for team in teams:
                    try:
                        transfers = await self.get_transfers(team.id, season)
                        stats["transfers_fetched"] += len(transfers)
                        stats["teams_processed"] += 1

                        # Rate limit: small delay entre equipos
                        await asyncio.sleep(0.1)

                    except FootballAPIError as e:
                        stats["errors"].append(f"Team {team.name}: {e}")
                        continue

            except FootballAPIError as e:
                stats["errors"].append(f"League {league_name}: {e}")
                continue

        return stats


# Instancia singleton
football_client = FootballDataClient()
