"""Página: Explorador de Traspasos."""
import asyncio

import streamlit as st

from transferplayer.models.domain import TransferRead
from transferplayer.services.transfer_service import transfer_service
from transferplayer.ui.components import (
    render_cards_grid,
    render_dataframe,
    render_download_button,
)

st.set_page_config(page_title="Explorador", page_icon="🔍", layout="wide")

st.markdown("# 🔍 Explorador de Traspasos")
st.markdown("### Filtra, busca y analiza traspasos de las 5 grandes ligas")
st.markdown("---")


@st.cache_data(ttl=300, show_spinner="Cargando traspasos...")
def load_transfers_cached(filters_dict: dict) -> tuple[list[TransferRead], int]:
    """Carga traspasos con cache (convertimos filtros a dict para cache)."""
    from transferplayer.models.domain import TransferFilter
    filters = TransferFilter(**filters_dict)
    transfers = asyncio.run(transfer_service.list_transfers(filters))
    total = asyncio.run(transfer_service.count_transfers(filters))
    return transfers, total


# Obtener valores únicos para filtros (sin cache para que se actualicen)
@st.cache_data(ttl=600)
def get_unique_values_cached() -> dict:
    return asyncio.run(transfer_service.get_unique_values())


# Cargar valores únicos
unique_vals = get_unique_values_cached()

# Sidebar con filtros
with st.sidebar:
    st.markdown("---")
    st.subheader("🔍 Filtros Avanzados")

    ligas = ["Todas"] + unique_vals.get("ligas", [])
    liga_sel = st.selectbox("Liga", ligas, key="explorer_liga")

    posiciones = ["Todas"] + unique_vals.get("posiciones", [])
    pos_sel = st.selectbox("Posición", posiciones, key="explorer_pos")

    tipos = ["Todos"] + unique_vals.get("tipos", [])
    tipo_sel = st.selectbox("Tipo", tipos, key="explorer_tipo")

    # Para clubs necesitamos query aparte o usar transfer_service
    search = st.text_input("🔎 Buscar (jugador/club)", "", key="explorer_search")

    # Rangos - necesitamos min/max de la BD
    from sqlalchemy import func, select

    from transferplayer.db.session import get_session
    from transferplayer.models.orm import Transfer

    @st.cache_data(ttl=600)
    def get_ranges():
        async def _get():
            async with get_session() as session:
                result = await session.execute(
                    select(
                        func.min(Transfer.valor), func.max(Transfer.valor),
                        func.min(Transfer.edad), func.max(Transfer.edad)
                    )
                )
                return result.first()
        return asyncio.run(_get())

    min_v, max_v, min_e, max_e = get_ranges() or (0, 200, 15, 45)
    if min_v == max_v: max_v = min_v + 1
    if min_e == max_e: max_e = min_e + 1

    rango_valor = st.slider("Valor (€M)", float(min_v), float(max_v), (float(min_v), float(max_v)), step=0.5)
    rango_edad = st.slider("Edad", min_e, max_e, (min_e, max_e))

    # Clubes (query aparte para no cargar todo)
    club_origen_sel = "Todos"
    club_destino_sel = "Todos"

# Construir filtros
from decimal import Decimal

from transferplayer.models.domain import TransferFilter

filters = TransferFilter(
    liga=None if liga_sel == "Todas" else liga_sel,
    posicion=None if pos_sel == "Todas" else pos_sel,
    tipo=None if tipo_sel == "Todos" else tipo_sel,
    club_origen=None if club_origen_sel == "Todos" else club_origen_sel,
    club_destino=None if club_destino_sel == "Todos" else club_destino_sel,
    valor_min=Decimal(str(rango_valor[0])),
    valor_max=Decimal(str(rango_valor[1])),
    edad_min=rango_edad[0],
    edad_max=rango_edad[1],
    search=search if search else None,
    limit=200,
    offset=0,
)

# Cargar datos (con cache key basado en filtros)
filters_dict = filters.model_dump()
transfers, total = load_transfers_cached(filters_dict)

# Resumen
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Encontrados", f"{len(transfers)} / {total}")
with col2:
    total_valor = sum(t.valor for t in transfers)
    st.metric("Valor Total", f"€{total_valor:,.1f}M")
with col3:
    avg_edad = sum(t.edad for t in transfers) / len(transfers) if transfers else 0
    st.metric("Edad Promedio", f"{avg_edad:.1f} años")
with col4:
    max_valor = max((t.valor for t in transfers), default=0)
    st.metric("Máximo", f"€{max_valor:,.1f}M")

st.markdown("---")

# Selector de vista
view_mode = st.radio("Vista", ["📊 Tabla", "🃏 Tarjetas"], horizontal=True, key="explorer_view")

if view_mode == "📊 Tabla":
    render_dataframe(transfers)
else:
    render_cards_grid(transfers)

st.markdown("---")
render_download_button(transfers, "transferencias_filtradas.csv")
