#!/usr/bin/env python
"""Script CLI para sincronizar datos desde API-Football."""

import argparse
import asyncio
import sys
from datetime import datetime

from transferplayer.services.sync_service import sync_service

MAX_ERRORS_PRINTED = 5


async def main():
    parser = argparse.ArgumentParser(description="Sincroniza traspasos desde API-Football")
    parser.add_argument(
        "--season",
        type=int,
        default=datetime.now().year,
        help="Temporada a sincronizar (default: año actual)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Ejecuta sin guardar en BD")
    parser.add_argument(
        "--leagues",
        nargs="+",
        type=int,
        default=[39, 140, 135, 78, 61],
        help="IDs de ligas (default: 5 grandes ligas)",
    )

    args = parser.parse_args()

    print(f"🔄 Iniciando sync para temporada {args.season}")
    print(f"   Dry run: {args.dry_run}")
    print(f"   Ligas: {args.leagues}")

    if args.dry_run:
        print("⚠️  MODO DRY-RUN: No se guardará en BD ni se registrará log")

    if args.leagues != [39, 140, 135, 78, 61]:
        print("ℹ️  --leagues aún no filtra: el sync cubre las 5 grandes ligas")

    try:
        stats = await sync_service.sync_all_leagues(season=args.season, dry_run=args.dry_run)

        print("\n📊 Resultado del sync:")
        print(f"   Estado: {stats['status']}")
        print(f"   Registros obtenidos: {stats['records_fetched']}")
        print(f"   Insertados: {stats['records_inserted']}")
        print(f"   Actualizados: {stats['records_updated']}")
        print(f"   Duración: {stats['duration_ms']}ms")

        if stats["errors"]:
            print(f"   ⚠️ Errores ({len(stats['errors'])}):")
            for err in stats["errors"][:MAX_ERRORS_PRINTED]:
                print(f"      - {err}")
            if len(stats["errors"]) > MAX_ERRORS_PRINTED:
                print(f"      ... y {len(stats['errors']) - MAX_ERRORS_PRINTED} más")

        if stats["status"] == "error":
            sys.exit(1)
        elif stats["dry_run"]:
            print("ℹ️  Dry run completado: no se modificó la BD")

    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
