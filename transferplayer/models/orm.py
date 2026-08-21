"""SQLAlchemy 2.0 ORM models."""
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all models."""


class Transfer(Base):
    """Modelo de traspaso de jugador."""

    __tablename__ = "transfers"
    __table_args__ = (
        Index("ix_transfers_liga", "liga"),
        Index("ix_transfers_posicion", "posicion"),
        Index("ix_transfers_club_destino", "club_destino"),
        Index("ix_transfers_valor", "valor"),
        Index("ix_transfers_fecha", "fecha"),
        UniqueConstraint(
            "jugador", "club_destino", "fecha", name="uq_transfer_jugador_destino_fecha"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    jugador: Mapped[str] = mapped_column(String(120), nullable=False)
    edad: Mapped[int] = mapped_column(Integer, nullable=False)
    posicion: Mapped[str] = mapped_column(String(30), nullable=False)
    liga: Mapped[str] = mapped_column(String(30), nullable=False)
    club_origen: Mapped[str] = mapped_column(String(120), nullable=False)
    club_destino: Mapped[str] = mapped_column(String(120), nullable=False)
    valor: Mapped[float] = mapped_column(Float, nullable=False)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    fecha: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Transfer(id={self.id}, jugador='{self.jugador}', club_destino='{self.club_destino}', valor={self.valor})>"


class SyncLog(Base):
    """Log de sincronizaciones con API externa."""

    __tablename__ = "sync_logs"
    __table_args__ = (
        Index("ix_sync_logs_status", "status"),
        Index("ix_sync_logs_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False)  # api-football, football-data
    endpoint: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # success, error, partial
    records_fetched: Mapped[int] = mapped_column(Integer, default=0)
    records_inserted: Mapped[int] = mapped_column(Integer, default=0)
    records_updated: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<SyncLog(id={self.id}, source='{self.source}', status='{self.status}')>"
