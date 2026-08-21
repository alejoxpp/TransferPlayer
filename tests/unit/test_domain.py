"""Tests unitarios para domain models."""
from decimal import Decimal

import pytest
from pydantic import ValidationError

from transferplayer.models.domain import (
    TransferCreate,
    TransferFilter,
    TransferRead,
    TransferUpdate,
)


class TestTransferCreate:
    """Tests para TransferCreate."""

    def test_valid_transfer(self):
        transfer = TransferCreate(
            jugador="Test Player",
            edad=25,
            posicion="Delantero",
            liga="Premier League",
            club_origen="Club A",
            club_destino="Club B",
            valor=Decimal("50.0"),
            tipo="Traspaso Definitivo",
        )
        assert transfer.jugador == "Test Player"
        assert transfer.valor == Decimal("50.0")

    def test_invalid_edad_too_young(self):
        with pytest.raises(ValidationError):
            TransferCreate(
                jugador="Test",
                edad=14,
                posicion="Delantero",
                liga="Premier League",
                club_origen="A",
                club_destino="B",
                valor=Decimal("10"),
                tipo="Traspaso Definitivo",
            )

    def test_invalid_edad_too_old(self):
        with pytest.raises(ValidationError):
            TransferCreate(
                jugador="Test",
                edad=46,
                posicion="Delantero",
                liga="Premier League",
                club_origen="A",
                club_destino="B",
                valor=Decimal("10"),
                tipo="Traspaso Definitivo",
            )

    def test_invalid_posicion(self):
        with pytest.raises(ValidationError):
            TransferCreate(
                jugador="Test", edad=25, posicion="InvalidPos", liga="Premier League",
                club_origen="A", club_destino="B", valor=Decimal("10"), tipo="Traspaso Definitivo"
            )

    def test_invalid_liga(self):
        with pytest.raises(ValidationError):
            TransferCreate(
                jugador="Test", edad=25, posicion="Delantero", liga="Invalid Liga",
                club_origen="A", club_destino="B", valor=Decimal("10"), tipo="Traspaso Definitivo"
            )

    def test_same_club_origen_destino(self):
        with pytest.raises(ValidationError):
            TransferCreate(
                jugador="Test", edad=25, posicion="Delantero", liga="Premier League",
                club_origen="Same Club", club_destino="Same Club",
                valor=Decimal("10"), tipo="Traspaso Definitivo"
            )

    def test_valor_negative(self):
        with pytest.raises(ValidationError):
            TransferCreate(
                jugador="Test", edad=25, posicion="Delantero", liga="Premier League",
                club_origen="A", club_destino="B", valor=Decimal("-1"), tipo="Traspaso Definitivo"
            )

    def test_tipo_invalid(self):
        with pytest.raises(ValidationError):
            TransferCreate(
                jugador="Test", edad=25, posicion="Delantero", liga="Premier League",
                club_origen="A", club_destino="B", valor=Decimal("10"), tipo="Invalid Tipo"
            )

    def test_whitespace_stripped(self):
        transfer = TransferCreate(
            jugador="  Test Player  ",
            edad=25,
            posicion="Delantero",
            liga="Premier League",
            club_origen="  Club A  ",
            club_destino="  Club B  ",
            valor=Decimal("10"),
            tipo="Traspaso Definitivo",
        )
        assert transfer.jugador == "Test Player"
        assert transfer.club_origen == "Club A"
        assert transfer.club_destino == "Club B"


class TestTransferUpdate:
    """Tests para TransferUpdate (campos opcionales)."""

    def test_partial_update(self):
        update = TransferUpdate(edad=26, valor=Decimal("60.0"))
        assert update.edad == 26
        assert update.valor == Decimal("60.0")
        assert update.posicion is None

    def test_empty_update(self):
        update = TransferUpdate()
        assert update.edad is None
        assert update.valor is None


class TestTransferFilter:
    """Tests para TransferFilter."""

    def test_default_values(self):
        f = TransferFilter()
        assert f.limit == 50
        assert f.offset == 0
        assert f.liga is None

    def test_custom_values(self):
        f = TransferFilter(liga="La Liga", valor_min=Decimal("10"), limit=100)
        assert f.liga == "La Liga"
        assert f.valor_min == Decimal("10")
        assert f.limit == 100


class TestTransferRead:
    """Tests para TransferRead."""

    def test_valor_eur_property(self):
        from datetime import datetime
        transfer = TransferRead(
            id=1,
            jugador="Test",
            edad=25,
            posicion="Delantero",
            liga="Premier League",
            club_origen="A",
            club_destino="B",
            valor=Decimal("50.5"),
            tipo="Traspaso Definitivo",
            fecha=datetime.now(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert transfer.valor_eur == "€50.50M"
