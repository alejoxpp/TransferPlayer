#!/usr/bin/env python
"""Migra datos de SQLite (transferencias.db) → PostgreSQL (Neon)."""
import asyncio
import sqlite3
import sys
from decimal import Decimal
from datetime import datetime
from pathlib import Path

# Añadir path del proyecto
sys.path.append(str(Path(__file__).parent.parent))

from transferplayer.db.session import init_db, close_db
from transferplayer.db.repository import get_transfer_repo
from transferplayer.models.domain import TransferCreate
from transferplayer.config import settings


SQLITE_DB = Path(__file__).parent.parent / "transferencias.db"


def read_sqlite() -> list[dict]:
    """Lee todos los traspasos de SQLite."""
    if not SQLITE_DB.exists():
        print(f"❌ No se encuentra {SQLITE_DB}")
        return []

    conn = sqlite3.connect(SQLITE_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT jugador, edad, posicion, liga, club_origen, club_destino, valor, tipo
        FROM transfers
    """)
    rows = cursor.fetchall()
    conn.close()

    transfers = []
    for row in rows:
        transfers.append({
            "jugador": row["jugador"],
            "edad": row["edad"],
            "posicion": row["posicion"],
            "liga": row["liga"],
            "club_origen": row["club_origen"],
            "club_destino": row["club_destino"],
            "valor": Decimal(str(row["valor"])),
            "tipo": row["tipo"],
        })

    print(f"📥 Leídos {len(transfers)} traspasos de SQLite")
    return transfers


async def migrate_to_postgres(transfers: list[dict]) -> tuple[int, int]:
    """Migra a PostgreSQL usando upsert."""
    await init_db()

    inserted = 0
    updated = 0

    async with get_transfer_repo() as repo:
        for t_data in transfers:
            try:
                data = TransferCreate(**t_data)
                _, created = await repo.upsert_from_api(data)
                if created:
                    inserted += 1
                else:
                    updated += 1
            except Exception as e:
                print(f"⚠️ Error migrando {t_data['jugador']}: {e}")

    await close_db()
    return inserted, updated


async def main():
    print("🔄 Iniciando migración SQLite → PostgreSQL")
    print(f"   SQLite: {SQLITE_DB}")
    print(f"   PostgreSQL: {settings.neon_database_url.host}/{settings.db_name}")

    # 1. Leer SQLite
    transfers = read_sqlite()
    if not transfers:
        print("❌ No hay datos para migrar")
        return

    # 2. Migrar a PostgreSQL
    print("📤 Migrando a PostgreSQL...")
    inserted, updated = await migrate_to_postgres(transfers)

    print("\n✅ Migración completada")
    print(f"   Insertados: {inserted}")
    print(f"   Actualizados: {updated}")
    print(f"   Total procesados: {len(transfers)}")


if __name__ == "__main__":
    asyncio.run(main())