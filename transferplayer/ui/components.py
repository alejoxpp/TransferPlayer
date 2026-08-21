"""Componentes UI reutilizables para Streamlit."""
from decimal import Decimal

import pandas as pd
import streamlit as st

from transferplayer.models.domain import TransferFilter, TransferRead


def render_kpi_card(label: str, value: str, delta: str | None = None, delta_color: str = "normal") -> None:
    """Renderiza una tarjeta KPI."""
    st.metric(label, value, delta=delta, delta_color=delta_color)


def render_transfer_card(transfer: TransferRead) -> None:
    """Renderiza una tarjeta de traspaso individual."""
    st.markdown(f"""
    <div style="
        background: white;
        padding: 18px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        border-left: 5px solid #2ca02c;
    ">
        <h4 style="margin: 0 0 8px 0;">{transfer.jugador}</h4>
        <p style="margin: 4px 0;"><b>Posición:</b> {transfer.posicion} | <b>Edad:</b> {transfer.edad} años</p>
        <p style="margin: 4px 0;"><b>De:</b> {transfer.club_origen} ➔ <b>A:</b> {transfer.club_destino}</p>
        <p style="margin: 4px 0;">
            <span style="background:#e2e8f0; color:#1e293b; padding:3px 8px; border-radius:6px; font-size:12px; font-weight:600;">{transfer.liga}</span>
            &nbsp; <b style="color:#1f77b4;">{transfer.valor_eur}</b> ({transfer.tipo})
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_filter_sidebar(df: pd.DataFrame) -> TransferFilter:
    """Renderiza sidebar con filtros y retorna objeto TransferFilter."""
    with st.sidebar:
        st.markdown("---")
        st.subheader("🔍 Filtros")

        ligas = ["Todas"] + sorted(df["liga"].unique().tolist()) if not df.empty else ["Todas"]
        liga_sel = st.selectbox("Liga", ligas)

        posiciones = ["Todas"] + sorted(df["posicion"].unique().tolist()) if not df.empty else ["Todas"]
        pos_sel = st.selectbox("Posición", posiciones)

        tipos = ["Todos"] + sorted(df["tipo"].unique().tolist()) if not df.empty else ["Todos"]
        tipo_sel = st.selectbox("Tipo", tipos)

        clubes_origen = ["Todos"] + sorted(df["club_origen"].unique().tolist()) if not df.empty else ["Todos"]
        club_origen_sel = st.selectbox("Club Origen", clubes_origen)

        clubes_destino = ["Todos"] + sorted(df["club_destino"].unique().tolist()) if not df.empty else ["Todos"]
        club_destino_sel = st.selectbox("Club Destino", clubes_destino)

        min_v = float(df["valor"].min()) if not df.empty else 0.0
        max_v = float(df["valor"].max()) if not df.empty else 200.0
        if min_v == max_v:
            max_v = min_v + 1.0
        rango_valor = st.slider("Valor (€M)", min_v, max_v, (min_v, max_v), step=0.5)

        min_e = int(df["edad"].min()) if not df.empty else 15
        max_e = int(df["edad"].max()) if not df.empty else 45
        if min_e == max_e:
            max_e = min_e + 1
        rango_edad = st.slider("Edad", min_e, max_e, (min_e, max_e))

        search = st.text_input("🔎 Buscar (jugador/club)", "")

    return TransferFilter(
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


def render_dataframe(transfers: list[TransferRead]) -> None:
    """Renderiza tabla interactiva con pandas."""
    if not transfers:
        st.info("No hay traspasos que coincidan con los filtros.")
        return

    df = pd.DataFrame([t.model_dump() for t in transfers])
    # Reordenar y renombrar columnas
    cols_order = ["jugador", "edad", "posicion", "liga", "club_origen", "club_destino", "valor", "tipo", "fecha"]
    col_names = {
        "jugador": "Jugador",
        "edad": "Edad",
        "posicion": "Posición",
        "liga": "Liga",
        "club_origen": "Club Origen",
        "club_destino": "Club Destino",
        "valor": "Valor (€M)",
        "tipo": "Tipo",
        "fecha": "Fecha",
    }
    df_display = df[cols_order].rename(columns=col_names)
    st.dataframe(df_display, width="stretch", hide_index=True)


def render_cards_grid(transfers: list[TransferRead], cols: int = 3) -> None:
    """Renderiza grid de tarjetas."""
    if not transfers:
        st.info("No hay traspasos que coincidan con los filtros.")
        return

    columns = st.columns(cols)
    for idx, transfer in enumerate(transfers):
        with columns[idx % cols]:
            render_transfer_card(transfer)


def render_download_button(transfers: list[TransferRead], filename: str = "transferencias.csv") -> None:
    """Botón de descarga CSV."""
    if not transfers:
        return
    df = pd.DataFrame([t.model_dump() for t in transfers])
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Descargar CSV",
        data=csv,
        file_name=filename,
        mime="text/csv",
        use_container_width=True,
    )


def render_sync_logs(logs: list) -> None:
    """Renderiza historial de sincronizaciones."""
    if not logs:
        st.info("No hay logs de sincronización.")
        return

    for log in logs:
        status_icon = {"success": "✅", "error": "❌", "partial": "⚠️"}.get(log.status, "ℹ️")
        with st.expander(f"{status_icon} {log.source} - {log.endpoint} - {log.created_at.strftime('%Y-%m-%d %H:%M')}"):
            st.write(f"**Estado:** {log.status}")
            st.write(f"**Registros:** {log.records_fetched} obtenidos, {log.records_inserted} insertados, {log.records_updated} actualizados")
            st.write(f"**Duración:** {log.duration_ms}ms")
            if log.error_message:
                st.error(log.error_message)
