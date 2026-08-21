"""Inicialización de BD y seed data."""
import asyncio
from decimal import Decimal

from transferplayer.db.session import close_db, init_db
from transferplayer.models.domain import TransferCreate

INITIAL_TRANSFERS = [
    TransferCreate(
        jugador="Kylian Mbappé",
        edad=25,
        posicion="Delantero",
        liga="La Liga",
        club_origen="Paris SG",
        club_destino="Real Madrid",
        valor=Decimal("180.0"),
        tipo="Traspaso Libre",
    ),
    TransferCreate(
        jugador="Harry Kane",
        edad=30,
        posicion="Delantero",
        liga="Bundesliga",
        club_origen="Tottenham",
        club_destino="Bayern Múnich",
        valor=Decimal("95.0"),
        tipo="Traspaso Definitivo",
    ),
    TransferCreate(
        jugador="Declan Rice",
        edad=25,
        posicion="Centrocampista",
        liga="Premier League",
        club_origen="West Ham",
        club_destino="Arsenal",
        valor=Decimal("116.6"),
        tipo="Traspaso Definitivo",
    ),
    TransferCreate(
        jugador="Jude Bellingham",
        edad=20,
        posicion="Centrocampista",
        liga="La Liga",
        club_origen="Borussia Dortmund",
        club_destino="Real Madrid",
        valor=Decimal("103.0"),
        tipo="Traspaso Definitivo",
    ),
    TransferCreate(
        jugador="Moises Caicedo",
        edad=22,
        posicion="Centrocampista",
        liga="Premier League",
        club_origen="Brighton",
        club_destino="Chelsea",
        valor=Decimal("116.0"),
        tipo="Traspaso Definitivo",
    ),
    TransferCreate(
        jugador="Rasmus Højlund",
        edad=21,
        posicion="Delantero",
        liga="Premier League",
        club_origen="Atalanta",
        club_destino="Manchester United",
        valor=Decimal("73.9"),
        tipo="Traspaso Definitivo",
    ),
    TransferCreate(
        jugador="Kim Min-jae",
        edad=27,
        posicion="Defensa",
        liga="Bundesliga",
        club_origen="Napoli",
        club_destino="Bayern Múnich",
        valor=Decimal("50.0"),
        tipo="Traspaso Definitivo",
    ),
    TransferCreate(
        jugador="Benjamin Pavard",
        edad=28,
        posicion="Defensa",
        liga="Serie A",
        club_origen="Bayern Múnich",
        club_destino="Inter de Milán",
        valor=Decimal("30.0"),
        tipo="Traspaso Definitivo",
    ),
    TransferCreate(
        jugador="Ousmane Dembélé",
        edad=26,
        posicion="Delantero",
        liga="Ligue 1",
        club_origen="Barcelona",
        club_destino="Paris SG",
        valor=Decimal("50.0"),
        tipo="Traspaso Definitivo",
    ),
    TransferCreate(
        jugador="Sandro Tonali",
        edad=23,
        posicion="Centrocampista",
        liga="Premier League",
        club_origen="AC Milan",
        club_destino="Newcastle United",
        valor=Decimal("64.0"),
        tipo="Traspaso Definitivo",
    ),
    TransferCreate(
        jugador="Marcus Thuram",
        edad=26,
        posicion="Delantero",
        liga="Serie A",
        club_origen="Borussia M'gladbach",
        club_destino="Inter de Milán",
        valor=Decimal("0.0"),
        tipo="Traspaso Libre",
    ),
    TransferCreate(
        jugador="Randal Kolo Muani",
        edad=25,
        posicion="Delantero",
        liga="Ligue 1",
        club_origen="Eintracht Frankfurt",
        club_destino="Paris SG",
        valor=Decimal("95.0"),
        tipo="Traspaso Definitivo",
    ),
    TransferCreate(
        jugador="Josko Gvardiol",
        edad=22,
        posicion="Defensa",
        liga="Premier League",
        club_origen="RB Leipzig",
        club_destino="Manchester City",
        valor=Decimal("90.0"),
        tipo="Traspaso Definitivo",
    ),
    TransferCreate(
        jugador="Christian Pulisic",
        edad=25,
        posicion="Delantero",
        liga="Serie A",
        club_origen="Chelsea",
        club_destino="AC Milan",
        valor=Decimal("20.0"),
        tipo="Traspaso Definitivo",
    ),
    TransferCreate(
        jugador="João Félix",
        edad=24,
        posicion="Delantero",
        liga="La Liga",
        club_origen="Atlético de Madrid",
        club_destino="FC Barcelona",
        valor=Decimal("0.0"),
        tipo="Cesión",
    ),
]


async def seed_database() -> None:
    """Crea tablas e inserta datos iniciales si la BD está vacía."""
    await init_db()

    async with get_transfer_repo() as repo:
        count = await repo.count()
        if count == 0:
            print("BD vacía - insertando datos iniciales...")
            for transfer in INITIAL_TRANSFERS:
                await repo.upsert_from_api(transfer)
            print(f"Insertados {len(INITIAL_TRANSFERS)} traspasos iniciales")
        else:
            print(f"BD ya tiene {count} traspasos - saltando seed")

    await close_db()


async def reset_database() -> None:
    """Elimina y recrea todas las tablas (solo desarrollo)."""
    from transferplayer.db.session import get_engine
    from transferplayer.models.orm import Base

    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("BD reseteada")

    await seed_database()


if __name__ == "__main__":
    asyncio.run(seed_database())
