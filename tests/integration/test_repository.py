"""Tests de integración para repository y services."""
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from transferplayer.db.repository import SyncLogRepository, TransferRepository
from transferplayer.models.domain import TransferCreate, TransferFilter

TEST_COUNT = 3
TEST_COUNT_TWO = 2
TEST_EDAD_UPDATED = 23


@pytest.mark.integration
class TestTransferRepository:
    """Tests de integración para TransferRepository."""

    async def _create_test_data(
        self, repo: TransferRepository, count: int = TEST_COUNT, liga: str = "La Liga",
    ) -> list:
        """Helper para crear datos de prueba."""
        created = []
        for i in range(count):
            t = await repo.create(
                jugador=f"Player {i}",
                edad=20 + i,
                posicion="Delantero",
                liga=liga,
                club_origen=f"Origin {i}",
                club_destino=f"Dest {i}",
                valor=Decimal(f"{10 * (i+1)}"),
                tipo="Traspaso Definitivo",
            )
            created.append(t)
        return created

    async def test_create_and_get(self, test_session: AsyncSession):
        repo = TransferRepository(test_session)

        transfer = await repo.create(
            jugador="Integration Test",
            edad=23,
            posicion="Centrocampista",
            liga="Bundesliga",
            club_origen="Club X",
            club_destino="Club Y",
            valor=Decimal("25.0"),
            tipo="Traspaso Definitivo",
        )

        assert transfer.id is not None
        assert transfer.jugador == "Integration Test"

        # Get by ID
        found = await repo.get_by_id(transfer.id)
        assert found is not None
        assert found.jugador == "Integration Test"

    async def test_list_filtered(self, test_session: AsyncSession):
        repo = TransferRepository(test_session)
        await self._create_test_data(repo, TEST_COUNT, "La Liga")

        # Filtrar por liga
        filters = TransferFilter(liga="La Liga", limit=10)
        results = await repo.list_filtered(filters)
        assert len(results) == TEST_COUNT

        # Filtrar por valor min
        filters = TransferFilter(valor_min=Decimal("15"), limit=10)
        results = await repo.list_filtered(filters)
        assert len(results) == TEST_COUNT_TWO

        # Filtrar por search
        filters = TransferFilter(search="Player 1", limit=10)
        results = await repo.list_filtered(filters)
        assert len(results) == 1

    async def test_count_filtered(self, test_session: AsyncSession):
        repo = TransferRepository(test_session)
        await self._create_test_data(repo, TEST_COUNT, "La Liga")

        filters = TransferFilter(liga="La Liga")
        count = await repo.count_filtered(filters)
        assert count == TEST_COUNT

    async def test_update(self, test_session: AsyncSession):
        repo = TransferRepository(test_session)

        transfer = await repo.create(
            jugador="To Update",
            edad=22,
            posicion="Defensa",
            liga="Serie A",
            club_origen="A",
            club_destino="B",
            valor=Decimal("15.0"),
            tipo="Traspaso Definitivo",
        )

        updated = await repo.update(transfer.id, edad=23, valor=Decimal("20.0"))
        assert updated is not None
        assert updated.edad == TEST_EDAD_UPDATED
        assert updated.valor == Decimal("20.0")
        assert updated.posicion == "Defensa"  # Sin cambiar

    async def test_delete(self, test_session: AsyncSession):
        repo = TransferRepository(test_session)

        transfer = await repo.create(
            jugador="To Delete",
            edad=24,
            posicion="Portero",
            liga="Ligue 1",
            club_origen="X",
            club_destino="Y",
            valor=Decimal("5.0"),
            tipo="Traspaso Libre",
        )

        deleted = await repo.delete(transfer.id)
        assert deleted is True

        found = await repo.get_by_id(transfer.id)
        assert found is None

    async def test_upsert_from_api(self, test_session: AsyncSession):
        repo = TransferRepository(test_session)

        data = TransferCreate(
            jugador="Upsert Test",
            edad=21,
            posicion="Centrocampista",
            liga="Premier League",
            club_origen="Club 1",
            club_destino="Club 2",
            valor=Decimal("30.0"),
            tipo="Cesión",
        )

        # Primera vez -> created
        transfer1, created1 = await repo.upsert_from_api(data)
        assert created1 is True
        assert transfer1.id is not None

        # Segunda vez con mismo jugador+destino -> updated
        data2 = TransferCreate(
            jugador="Upsert Test",
            edad=22,
            posicion="Centrocampista",
            liga="Premier League",
            club_origen="Club 1",
            club_destino="Club 2",
            valor=Decimal("35.0"),
            tipo="Traspaso Definitivo",
        )
        transfer2, created2 = await repo.upsert_from_api(data2)
        assert created2 is False
        assert transfer2.id == transfer1.id
        assert transfer2.valor == Decimal("35.0")
        assert transfer2.tipo == "Traspaso Definitivo"


@pytest.mark.integration
class TestSyncLogRepository:
    """Tests para SyncLogRepository."""

    async def test_create_log(self, test_session: AsyncSession):
        repo = SyncLogRepository(test_session)

        log = await repo.create_log(
            source="test-api",
            endpoint="/transfers",
            status="success",
            records_fetched=100,
            records_inserted=10,
            records_updated=5,
            duration_ms=1500,
        )

        assert log.id is not None
        assert log.source == "test-api"
        assert log.status == "success"

    async def test_get_recent(self, test_session: AsyncSession):
        repo = SyncLogRepository(test_session)

        for i in range(3):
            await repo.create_log(
                source=f"source-{i}",
                endpoint=f"/endpoint-{i}",
                status="success",
            )

        logs = await repo.get_recent(TEST_COUNT_TWO)
        assert len(logs) == TEST_COUNT_TWO
        # Ordenados por created_at desc
        assert logs[0].source == "source-2"
