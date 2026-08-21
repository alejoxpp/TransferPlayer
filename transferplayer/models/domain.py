"""Pydantic domain models (validación, serialización, API)."""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TransferBase(BaseModel):
    """Campos base de un traspaso."""
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    jugador: str = Field(..., min_length=1, max_length=120, description="Nombre del jugador")
    edad: int = Field(..., ge=15, le=45, description="Edad del jugador")
    posicion: str = Field(..., pattern=r"^(Delantero|Centrocampista|Defensa|Portero)$")
    liga: str = Field(..., pattern=r"^(Premier League|La Liga|Serie A|Bundesliga|Ligue 1)$")
    club_origen: str = Field(..., min_length=1, max_length=120)
    club_destino: str = Field(..., min_length=1, max_length=120)
    valor: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2, description="Valor en millones EUR")
    tipo: str = Field(..., pattern=r"^(Traspaso Definitivo|Cesión|Traspaso Libre)$")

    @field_validator("club_destino")
    @classmethod
    def club_destino_different_from_origen(cls, v: str, info) -> str:
        if info.data.get("club_origen") and v.lower() == info.data["club_origen"].lower():
            raise ValueError("Club destino debe ser diferente al club origen")
        return v


class TransferCreate(TransferBase):
    """Para crear nuevo traspaso."""


class TransferUpdate(BaseModel):
    """Para actualizar traspaso (todos opcionales)."""
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    edad: int | None = Field(None, ge=15, le=45)
    posicion: str | None = Field(None, pattern=r"^(Delantero|Centrocampista|Defensa|Portero)$")
    liga: str | None = Field(None, pattern=r"^(Premier League|La Liga|Serie A|Bundesliga|Ligue 1)$")
    club_origen: str | None = Field(None, min_length=1, max_length=120)
    club_destino: str | None = Field(None, min_length=1, max_length=120)
    valor: Decimal | None = Field(None, ge=0, max_digits=10, decimal_places=2)
    tipo: str | None = Field(None, pattern=r"^(Traspaso Definitivo|Cesión|Traspaso Libre)$")


class TransferRead(TransferBase):
    """Para lectura/serialización."""
    id: int
    fecha: datetime
    created_at: datetime
    updated_at: datetime

    @property
    def valor_eur(self) -> str:
        return f"€{self.valor:,.2f}M"


class TransferFilter(BaseModel):
    """Filtros para listado/búsqueda."""
    liga: str | None = None
    posicion: str | None = None
    tipo: str | None = None
    club_origen: str | None = None
    club_destino: str | None = None
    valor_min: Decimal | None = Field(None, ge=0)
    valor_max: Decimal | None = Field(None, ge=0)
    edad_min: int | None = Field(None, ge=15)
    edad_max: int | None = Field(None, le=45)
    search: str | None = Field(None, description="Búsqueda en jugador/club_origen/club_destino")
    limit: int = Field(50, ge=1, le=200)
    offset: int = Field(0, ge=0)


class SyncLogRead(BaseModel):
    """Log de sincronización."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    source: str
    endpoint: str
    status: str
    records_fetched: int
    records_inserted: int
    records_updated: int
    error_message: str | None
    duration_ms: int
    created_at: datetime
