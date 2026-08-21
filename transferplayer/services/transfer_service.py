"""Servicio de lógica de negocio para traspasos."""
from collections.abc import Sequence

from transferplayer.db.repository import TransferRepository, get_transfer_repo
from transferplayer.models.domain import TransferCreate, TransferFilter, TransferUpdate
from transferplayer.models.orm import Transfer


class TransferService:
    """Capa de servicio para operaciones de traspasos."""

    def __init__(self, repo: TransferRepository | None = None):
        self._repo = repo

    async def _get_repo(self) -> TransferRepository:
        if self._repo:
            return self._repo
        # Si no hay repo inyectado, crear uno nuevo (para uso directo)
        # Nota: en uso real, inyectar repo via context manager
        raise RuntimeError("Usar TransferService dentro de async with get_transfer_repo()")

    async def list_transfers(self, filters: TransferFilter) -> Sequence[Transfer]:
        async with get_transfer_repo() as repo:
            return await repo.list_filtered(filters)

    async def count_transfers(self, filters: TransferFilter) -> int:
        async with get_transfer_repo() as repo:
            return await repo.count_filtered(filters)

    async def get_transfer(self, transfer_id: int) -> Transfer | None:
        async with get_transfer_repo() as repo:
            return await repo.get_by_id(transfer_id)

    async def create_transfer(self, data: TransferCreate) -> Transfer:
        async with get_transfer_repo() as repo:
            transfer, _ = await repo.upsert_from_api(data)
            return transfer

    async def update_transfer(self, transfer_id: int, data: TransferUpdate) -> Transfer | None:
        async with get_transfer_repo() as repo:
            return await repo.update(transfer_id, **data.model_dump(exclude_unset=True))

    async def delete_transfer(self, transfer_id: int) -> bool:
        async with get_transfer_repo() as repo:
            return await repo.delete(transfer_id)

    async def get_dashboard_stats(self) -> dict:
        async with get_transfer_repo() as repo:
            return await repo.get_stats()

    async def get_unique_values(self) -> dict:
        """Obtiene valores únicos para filtros dropdown."""
        from sqlalchemy import distinct, select

        from transferplayer.db.session import get_session
        from transferplayer.models.orm import Transfer

        async with get_session() as session:
            ligas = await session.execute(select(distinct(Transfer.liga)).order_by(Transfer.liga))
            posiciones = await session.execute(select(distinct(Transfer.posicion)).order_by(Transfer.posicion))
            tipos = await session.execute(select(distinct(Transfer.tipo)).order_by(Transfer.tipo))

            return {
                "ligas": [r[0] for r in ligas.all()],
                "posiciones": [r[0] for r in posiciones.all()],
                "tipos": [r[0] for r in tipos.all()],
            }


# Instancia singleton para uso en UI
transfer_service = TransferService()
