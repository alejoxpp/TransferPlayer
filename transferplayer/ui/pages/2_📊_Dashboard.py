"""Página: Dashboard Estadístico."""
import asyncio

import pandas as pd
import plotly.express as px
import streamlit as st

from transferplayer.services.transfer_service import transfer_service

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.markdown("# 📊 Dashboard Ejecutivo de Mercado")
st.markdown("### Análisis visual del mercado de fichajes - 5 Grandes Ligas")
st.markdown("---")


@st.cache_data(ttl=300, show_spinner="Calculando estadísticas...")
def load_stats_cached() -> dict:
    return asyncio.run(transfer_service.get_dashboard_stats())


@st.cache_data(ttl=300)
def load_all_transfers_cached() -> list:
    from transferplayer.models.domain import TransferFilter
    filters = TransferFilter(limit=1000)
    return asyncio.run(transfer_service.list_transfers(filters))


# Cargar datos
stats = load_stats_cached()
transfers = load_all_transfers_cached()

if not transfers:
    st.warning("No hay datos disponibles. Ejecuta una sincronización o seed inicial.")
    st.stop()

# KPIs principales
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Fichajes", stats["total_transfers"])
with col2:
    st.metric("Inversión Global", f"€{stats['total_valor']:,.1f}M")
with col3:
    st.metric("Valor Promedio", f"€{stats['avg_valor']:,.1f}M")
with col4:
    st.metric("Traspaso Récord", f"€{stats['max_valor']:,.1f}M")

st.markdown("---")

# Gráficos
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("💰 Inversión Total por Liga")
    df_liga = pd.DataFrame(stats["by_liga"])
    if not df_liga.empty:
        fig_liga = px.bar(
            df_liga, x="liga", y="total_valor", color="liga",
            text_auto=".1fM", labels={"liga": "Liga", "total_valor": "Inversión (€M)"},
            title="Gasto Acumulado por Liga"
        )
        fig_liga.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_liga, width="stretch")

with col_b:
    st.subheader("⚽ Distribución por Posición")
    df_pos = pd.DataFrame(stats["by_posicion"])
    if not df_pos.empty:
        fig_pos = px.pie(
            df_pos, names="posicion", values="count", hole=0.4,
            title="Proporción de Fichajes por Posición"
        )
        fig_pos.update_traces(textposition="inside", textinfo="percent+label")
        fig_pos.update_layout(height=400)
        st.plotly_chart(fig_pos, width="stretch")

col_c, col_d = st.columns(2)

with col_c:
    st.subheader("🏆 Top 10 Clubs Inversores (Destino)")
    df_clubs = pd.DataFrame(stats["top_clubs"])
    if not df_clubs.empty:
        fig_clubs = px.bar(
            df_clubs.head(10), x="club", y="total_valor", color="club",
            labels={"club": "Club", "total_valor": "Inversión (€M)"},
            title="Clubes que Más Invierten"
        )
        fig_clubs.update_layout(showlegend=False, height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig_clubs, width="stretch")

with col_d:
    st.subheader("📈 Relación Edad vs Valor de Mercado")
    df_scatter = pd.DataFrame([{
        "jugador": t.jugador, "edad": t.edad, "valor": float(t.valor),
        "liga": t.liga, "club_destino": t.club_destino, "posicion": t.posicion
    } for t in transfers])
    if not df_scatter.empty:
        fig_scatter = px.scatter(
            df_scatter, x="edad", y="valor", color="liga",
            hover_data=["jugador", "club_destino", "posicion"],
            labels={"edad": "Edad", "valor": "Valor (€M)"},
            title="Edad vs Valor de Mercado por Liga"
        )
        fig_scatter.update_layout(height=400)
        st.plotly_chart(fig_scatter, width="stretch")

# Tabla detallada expandible
with st.expander("📋 Ver datos completos", expanded=False):
    df_full = pd.DataFrame([{
        "Jugador": t.jugador, "Edad": t.edad, "Posición": t.posicion,
        "Liga": t.liga, "Origen": t.club_origen, "Destino": t.club_destino,
        "Valor (€M)": t.valor, "Tipo": t.tipo, "Fecha": t.fecha.strftime("%Y-%m-%d")
    } for t in transfers])
    st.dataframe(df_full, width="stretch", hide_index=True)
