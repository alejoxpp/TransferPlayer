"""Repository pattern para acceso a datos tipado."""
from collections.abc import Sequence
from contextlib import asynccontextmanager
from typing import Generic, TypeVar

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from transferplayer.db.session import get_session
from transferplayer.models.domain import TransferCreate, TransferFilter
from transferplayer.models.orm import Base, SyncLog, Transfer

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Repository base genérico."""

    def __init__(self, model: type[T], session: AsyncSession | None = None):
        self.model = model
        self._session = session

    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            raise RuntimeError("Session no inyectada. Usar async with repo:")
        return self._session

    async def get_by_id(self, id: int) -> T | None:
        return await self.session.get(self.model, id)

    async def list_all(self, limit: int = 100, offset: int = 0) -> Sequence[T]:
        stmt = select(self.model).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count(self) -> int:
        stmt = select(func.count()).select_from(self.model)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def create(self, **kwargs) -> T:
        obj = self.model(**kwargs)
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update(self, id: int, **kwargs) -> T | None:
        obj = await self.get_by_id(id)
        if obj is None:
            return None
        for k, v in kwargs.items():
            if v is not None:
                setattr(obj, k, v)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete(self, id: int) -> bool:
        obj = await self.get_by_id(id)
        if obj is None:
            return False
        await self.session.delete(obj)
        await self.session.flush()
        return True


class TransferRepository(BaseRepository[Transfer]):
    """Repository especializado para traspasos."""

    def __init__(self, session: AsyncSession | None = None):
        super().__init__(Transfer, session)

    def _build_filter_stmt(self, filters: TransferFilter) -> Select:
        stmt = select(Transfer)
        conditions = []

        if filters.liga:
            conditions.append(Transfer.liga == filters.liga)
        if filters.posicion:
            conditions.append(Transfer.posicion == filters.posicion)
        if filters.tipo:
            conditions.append(Transfer.tipo == filters.tipo)
        if filters.club_origen:
            conditions.append(Transfer.club_origen.ilike(f"%{filters.club_origen}%"))
        if filters.club_destino:
            conditions.append(Transfer.club_destino.ilike(f"%{filters.club_destino}%"))
        if filters.valor_min is not None:
            conditions.append(Transfer.valor >= filters.valor_min)
        if filters.valor_max is not None:
            conditions.append(Transfer.valor <= filters.valor_max)
        if filters.edad_min is not None:
            conditions.append(Transfer.edad >= filters.edad_min)
        if filters.edad_max is not None:
            conditions.append(Transfer.edad <= filters.edad_max)
        if filters.search:
            q = f"%{filters.search.lower()}%"
            conditions.append(
                or_(
                    Transfer.jugador.ilike(q),
                    Transfer.club_origen.ilike(q),
                    Transfer.club_destino.ilike(q),
                )
            )

        if conditions:
            stmt = stmt.where(*conditions)

        stmt = stmt.order_by(Transfer.fecha.desc()).limit(filters.limit).offset(filters.offset)
        return stmt

    async def list_filtered(self, filters: TransferFilter) -> Sequence[Transfer]:
        stmt = self._build_filter_stmt(filters)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_filtered(self, filters: TransferFilter) -> int:
        stmt = select(func.count()).select_from(Transfer)
        conditions = []

        if filters.liga:
            conditions.append(Transfer.liga == filters.liga)
        if filters.posicion:
            conditions.append(Transfer.posicion == filters.posicion)
        if filters.tipo:
            conditions.append(Transfer.tipo == filters.tipo)
        if filters.club_origen:
            conditions.append(Transfer.club_origen.ilike(f"%{filters.club_origen}%"))
        if filters.club_destino:
            conditions.append(Transfer.club_destino.ilike(f"%{filters.club_destino}%"))
        if filters.valor_min is not None:
            conditions.append(Transfer.valor >= filters.valor_min)
        if filters.valor_max is not None:
            conditions.append(Transfer.valor <= filters.valor_max)
        if filters.edad_min is not None:
            conditions.append(Transfer.edad >= filters.edad_min)
        if filters.edad_max is not None:
            conditions.append(Transfer.edad <= filters.edad_max)
        if filters.search:
            q = f"%{filters.search.lower()}%"
            conditions.append(
                or_(
                    Transfer.jugador.ilike(q),
                    Transfer.club_origen.ilike(q),
                    Transfer.club_destino.ilike(q),
                )
            )

        if conditions:
            stmt = stmt.where(*conditions)

        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_stats(self) -> dict:
        """Estadísticas agregadas para dashboard."""
        async with get_session() as session:
            total = await session.execute(select(func.count()).select_from(Transfer))
            total_valor = await session.execute(select(func.coalesce(func.sum(Transfer.valor), 0)).select_from(Transfer))
            avg_valor = await session.execute(select(func.coalesce(func.avg(Transfer.valor), 0)).select_from(Transfer))
            max_valor = await session.execute(select(func.coalesce(func.max(Transfer.valor), 0)).select_from(Transfer))

            # Por liga
            liga_stats = await session.execute(
                select(Transfer.liga, func.sum(Transfer.valor), func.count())
                .group_by(Transfer.liga)
                .order_by(func.sum(Transfer.valor).desc())
            )
            # Por posición
            pos_stats = await session.execute(
                select(Transfer.posicion, func.count())
                .group_by(Transfer.posicion)
                .order_by(func.count().desc())
            )
            # Top clubes destino
            club_stats = await session.execute(
                select(Transfer.club_destino, func.sum(Transfer.valor))
                .group_by(Transfer.club_destino)
                .order_by(func.sum(Transfer.valor).desc())
                .limit(10)
            )

            return {
                "total_transfers": total.scalar_one(),
                "total_valor": float(total_valor.scalar_one()),
                "avg_valor": float(avg_valor.scalar_one()),
                "max_valor": float(max_valor.scalar_one()),
                "by_liga": [
                    {"liga": r[0], "total_valor": float(r[1]), "count": r[2]}
                    for r in liga_stats.all()
                ],
                "by_posicion": [
                    {"posicion": r[0], "count": r[1]} for r in pos_stats.all()
                ],
                "top_clubs": [
                    {"club": r[0], "total_valor": float(r[1])} for r in club_stats.all()
                ],
            }

    async def upsert_from_api(self, data: TransferCreate) -> tuple[Transfer, bool]:
        """
        Inserta o actualiza por jugador + club_destino + fecha (aprox).
        Returns: (transfer, created)
        """
        stmt = select(Transfer).where(
            Transfer.jugador == data.jugador,
            Transfer.club_destino == data.club_destino,
        )
        result = await self.session.execute(stmt)
        existing = result.scalars().first()

        if existing:
            # Update
            for field, value in data.model_dump().items():
                setattr(existing, field, value)
            await self.session.flush()
            await self.session.refresh(existing)
            return existing, False
        else:
            # Create
            new = Transfer(**data.model_dump())
            self.session.add(new)
            await self.session.flush()
            await self.session.refresh(new)
            return new, True


class SyncLogRepository(BaseRepository[SyncLog]):
    """Repository para logs de sync."""

    def __init__(self, session: AsyncSession | None = None):
        super().__init__(SyncLog, session)

    async def create_log(
        self,
        source: str,
        endpoint: str,
        status: str,
        records_fetched: int = 0,
        records_inserted: int = 0,
        records_updated: int = 0,
        error_message: str | None = None,
        duration_ms: int = 0,
    ) -> SyncLog:
        return await self.create(
            source=source,
            endpoint=endpoint,
            status=status,
            records_fetched=records_fetched,
            records_inserted=records_inserted,
            records_updated=records_updated,
            error_message=error_message,
            duration_ms=duration_ms,
        )

    async def get_recent(self, limit: int = 20) -> Sequence[SyncLog]:
        stmt = select(SyncLog).order_by(SyncLog.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()


@asynccontextmanager
async def get_transfer_repo() -> TransferRepository:
    """Context manager para TransferRepository con sesión automática."""
    async with get_session() as session:
        yield TransferRepository(session)


@asynccontextmanager
async def get_sync_log_repo() -> SyncLogRepository:
    async with get_session() as session:
        yield SyncLogRepository(session)
