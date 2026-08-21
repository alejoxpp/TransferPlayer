"""Configuración global de pytest."""
import asyncio
import contextlib
import tempfile
from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from transferplayer.models.orm import Base


@pytest.fixture(scope="session")
def event_loop():
    """Event loop para tests async."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Engine de prueba (SQLite en archivo temporal para persistencia)."""
    # Usar archivo temporal para que persista entre conexiones
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    engine = create_async_engine(
        f"sqlite+aiosqlite:///{db_path}",
        echo=False,
        poolclass=StaticPool,  # Mantiene una sola conexión
        connect_args={"check_same_thread": False},
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()
    # Limpiar archivo temporal
    with contextlib.suppress(OSError):
        Path(db_path).unlink()


@pytest.fixture
async def test_session(test_engine: AsyncEngine) -> AsyncSession:
    """Sesión de BD para cada test."""
    factory = async_sessionmaker(bind=test_engine, expire_on_commit=False)
    async with factory() as session:
        yield session


@pytest.fixture(autouse=True)
async def cleanup_db(test_session: AsyncSession):
    """Limpia BD después de cada test."""
    yield
    # Rollback cualquier cambio
    await test_session.rollback()
