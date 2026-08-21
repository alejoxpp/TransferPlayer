"""Página: Gestión CRUD de Traspasos."""
import asyncio
from decimal import Decimal

import streamlit as st

from transferplayer.models.domain import TransferCreate, TransferRead, TransferUpdate
from transferplayer.services.transfer_service import transfer_service
from transferplayer.ui.components import render_transfer_card

st.set_page_config(page_title="Gestión CRUD", page_icon="⚙️", layout="wide")

st.markdown("# ⚙️ Panel de Gestión (CRUD)")
st.markdown("### Crear, leer, actualizar y eliminar traspasos en PostgreSQL")
st.markdown("---")

tab_add, tab_edit, tab_delete, tab_view = st.tabs([
    "➕ Crear", "✏️ Editar", "🗑️ Eliminar", "👁️ Ver Detalle"
])

# --- CREAR ---
with tab_add:
    st.subheader("Registrar nuevo traspaso")

    with st.form("form_create", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            jugador = st.text_input("Jugador *", placeholder="Ej: Kylian Mbappé")
            edad = st.number_input("Edad *", min_value=15, max_value=45, value=22)
            posicion = st.selectbox("Posición *", ["Delantero", "Centrocampista", "Defensa", "Portero"])
            liga = st.selectbox("Liga Destino *", ["Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1"])
        with c2:
            club_origen = st.text_input("Club Origen *", placeholder="Ej: Paris SG")
            club_destino = st.text_input("Club Destino *", placeholder="Ej: Real Madrid")
            valor = st.number_input("Valor (€M) *", min_value=0.0, max_value=500.0, value=30.0, step=0.5)
            tipo = st.selectbox("Tipo *", ["Traspaso Definitivo", "Cesión", "Traspaso Libre"])

        submitted = st.form_submit_button("💾 Guardar en PostgreSQL", type="primary", use_container_width=True)

        if submitted:
            if not all([jugador.strip(), club_origen.strip(), club_destino.strip()]):
                st.error("❌ Completa todos los campos obligatorios (*)")
            elif club_origen.strip().lower() == club_destino.strip().lower():
                st.error("❌ Club origen y destino deben ser diferentes")
            else:
                try:
                    data = TransferCreate(
                        jugador=jugador.strip(),
                        edad=edad,
                        posicion=posicion,
                        liga=liga,
                        club_origen=club_origen.strip(),
                        club_destino=club_destino.strip(),
                        valor=Decimal(str(valor)),
                        tipo=tipo,
                    )
                    result = asyncio.run(transfer_service.create_transfer(data))
                    st.success(f"✅ Traspaso de **{result.jugador}** guardado (ID: {result.id})")
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")

# --- EDITAR ---
with tab_edit:
    st.subheader("Modificar traspaso existente")

    @st.cache_data(ttl=60, show_spinner="Cargando lista...")
    def load_all_for_edit():
        from transferplayer.models.domain import TransferFilter
        return asyncio.run(transfer_service.list_transfers(TransferFilter(limit=500)))

    all_transfers = load_all_for_edit()

    if not all_transfers:
        st.info("No hay traspasos registrados.")
    else:
        # Selector
        options = {f"{t.jugador} → {t.club_destino} (€{t.valor}M)": t for t in all_transfers}
        selected_key = st.selectbox("Selecciona traspaso", list(options.keys()))
        selected: TransferRead = options[selected_key]

        with st.form(f"form_edit_{selected.id}"):
            c1, c2 = st.columns(2)
            with c1:
                edit_edad = st.number_input("Edad", min_value=15, max_value=45, value=selected.edad)
                edit_pos = st.selectbox("Posición", ["Delantero", "Centrocampista", "Defensa", "Portero"],
                                        index=["Delantero", "Centrocampista", "Defensa", "Portero"].index(selected.posicion))
                edit_liga = st.selectbox("Liga", ["Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1"],
                                         index=["Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1"].index(selected.liga))
            with c2:
                edit_origen = st.text_input("Club Origen", value=selected.club_origen)
                edit_destino = st.text_input("Club Destino", value=selected.club_destino)
                edit_valor = st.number_input("Valor (€M)", min_value=0.0, max_value=500.0, value=float(selected.valor), step=0.5)
                edit_tipo = st.selectbox("Tipo", ["Traspaso Definitivo", "Cesión", "Traspaso Libre"],
                                         index=["Traspaso Definitivo", "Cesión", "Traspaso Libre"].index(selected.tipo))

            update_submitted = st.form_submit_button("🔄 Actualizar", type="primary", use_container_width=True)

            if update_submitted:
                if not all([edit_origen.strip(), edit_destino.strip()]):
                    st.error("❌ Clubes obligatorios")
                elif edit_origen.strip().lower() == edit_destino.strip().lower():
                    st.error("❌ Clubes deben ser diferentes")
                else:
                    try:
                        update_data = TransferUpdate(
                            edad=edit_edad,
                            posicion=edit_pos,
                            liga=edit_liga,
                            club_origen=edit_origen.strip(),
                            club_destino=edit_destino.strip(),
                            valor=Decimal(str(edit_valor)),
                            tipo=edit_tipo,
                        )
                        result = asyncio.run(transfer_service.update_transfer(selected.id, update_data))
                        if result:
                            st.success(f"✅ **{result.jugador}** actualizado correctamente")
                            st.rerun()
                        else:
                            st.error("❌ No se encontró el registro")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")

# --- ELIMINAR ---
with tab_delete:
    st.subheader("Eliminar traspaso permanentemente")
    st.warning("⚠️ Esta acción no se puede deshacer")

    if not all_transfers:
        st.info("No hay traspasos para eliminar.")
    else:
        del_options = {f"{t.jugador} → {t.club_destino} (€{t.valor}M)": t for t in all_transfers}
        del_key = st.selectbox("Selecciona para eliminar", list(del_options.keys()), key="del_select")
        to_delete: TransferRead = del_options[del_key]

        st.markdown(f"""
        **Confirmar eliminación:**
        - **Jugador:** {to_delete.jugador}
        - **De:** {to_delete.club_origen} → **A:** {to_delete.club_destino}
        - **Valor:** €{to_delete.valor}M ({to_delete.tipo})
        - **ID:** {to_delete.id}
        """)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ ELIMINAR PERMANENTEMENTE", type="primary", use_container_width=True):
                try:
                    success = asyncio.run(transfer_service.delete_transfer(to_delete.id))
                    if success:
                        st.success(f"✅ Traspaso de **{to_delete.jugador}** eliminado")
                        st.rerun()
                    else:
                        st.error("❌ No se encontró el registro")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        with col2:
            if st.button("Cancelar", use_container_width=True):
                st.rerun()

# --- VER DETALLE ---
with tab_view:
    st.subheader("Detalle de traspaso")

    if not all_transfers:
        st.info("No hay traspasos.")
    else:
        view_options = {f"{t.jugador} → {t.club_destino}": t for t in all_transfers}
        view_key = st.selectbox("Selecciona", list(view_options.keys()), key="view_select")
        view_transfer: TransferRead = view_options[view_key]

        render_transfer_card(view_transfer)

        st.markdown("---")
        st.markdown("**Metadatos:**")
        st.json({
            "id": view_transfer.id,
            "fecha": view_transfer.fecha.isoformat(),
            "created_at": view_transfer.created_at.isoformat(),
            "updated_at": view_transfer.updated_at.isoformat(),
        })
