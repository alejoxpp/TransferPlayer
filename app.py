import streamlit as st
import pandas as pd
import plotly.express as px
from database import init_db, get_transfers_df, add_transfer, update_transfer, delete_transfer

st.set_page_config(
    page_title="Prototipo Traspasos - 5 Grandes Ligas",
    page_icon="⚽",
    layout="wide",
)

# Inicializar base de datos SQLite
init_db()

# --- CSS PERSONALIZADO ---
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .kpi-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        text-align: center;
        border-top: 4px solid #1f77b4;
    }
    .player-card {
        background: white;
        padding: 18px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        border-left: 5px solid #2ca02c;
    }
    .badge-liga {
        background-color: #e2e8f0;
        color: #1e293b;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

df = get_transfers_df()

# --- ENCABEZADO PRINCIPAL ---
st.markdown("# ⚽ Prototipo Profesional de Traspasos (SQLite)")
st.markdown("### *Las 5 Grandes Ligas del Fútbol Europeo*")
st.markdown("---")

# Barra lateral para navegación y filtros globales
st.sidebar.image("https://images.unsplash.com/photo-1508098682722-e99c43a406b2?auto=format&fit=crop&w=600&q=80", use_container_width=True)
st.sidebar.title("Menú de Navegación")
menu = st.sidebar.radio("Ir a:", ["Explorador de Fichajes", "Dashboard Estadístico", "Gestión CRUD de Traspasos"])

# ----------------------------------------------------
# PESTAÑA 1: EXPLORADOR DE FICHAJES
# ----------------------------------------------------
if menu == "Explorador de Fichajes":
    st.header("🔍 Explorador Avanzado de Traspasos")
    
    with st.sidebar:
        st.markdown("---")
        st.subheader("Filtros Interactivos")
        
        ligas_disponibles = ["Todas"] + list(df["Liga"].unique()) if not df.empty else ["Todas"]
        liga_sel = st.selectbox("Liga", ligas_disponibles)
        
        posiciones_disponibles = ["Todas"] + list(df["Posición"].unique()) if not df.empty else ["Todas"]
        pos_sel = st.selectbox("Posición", posiciones_disponibles)
        
        tipos_disponibles = ["Todos"] + list(df["Tipo"].unique()) if not df.empty else ["Todos"]
        tipo_sel = st.selectbox("Tipo de Traspaso", tipos_disponibles)
        
        min_v = float(df["Valor (€M)"].min()) if not df.empty else 0.0
        max_v = float(df["Valor (€M)"].max()) if not df.empty else 200.0
        if min_v == max_v:
            max_v = min_v + 1.0
        rango_valor = st.slider("Rango de Valor (€M)", min_v, max_v, (min_v, max_v))
        
        min_e = int(df["Edad"].min()) if not df.empty else 15
        max_e = int(df["Edad"].max()) if not df.empty else 45
        if min_e == max_e:
            max_e = min_e + 1
        rango_edad = st.slider("Rango de Edad", min_e, max_e, (min_e, max_e))
        
        search_query = st.text_input("Búsqueda rápida (Jugador/Club)", "")

    # Aplicar filtros
    filtrado_df = df.copy()
    if not filtrado_df.empty:
        if liga_sel != "Todas":
            filtrado_df = filtrado_df[filtrado_df["Liga"] == liga_sel]
        if pos_sel != "Todas":
            filtrado_df = filtrado_df[filtrado_df["Posición"] == pos_sel]
        if tipo_sel != "Todos":
            filtrado_df = filtrado_df[filtrado_df["Tipo"] == tipo_sel]
            
        filtrado_df = filtrado_df[
            (filtrado_df["Valor (€M)"].between(rango_valor[0], rango_valor[1])) &
            (filtrado_df["Edad"].between(rango_edad[0], rango_edad[1]))
        ]
        
        if search_query:
            q = search_query.lower()
            filtrado_df = filtrado_df[
                filtrado_df["Jugador"].str.lower().str.contains(q) |
                filtrado_df["Club Origen"].str.lower().str.contains(q) |
                filtrado_df["Club Destino"].str.lower().str.contains(q)
            ]

    # Resumen de resultados filtrados
    col_res1, col_res2, col_res3 = st.columns(3)
    with col_res1:
        st.metric("Traspasos Encontrados", len(filtrado_df))
    with col_res2:
        st.metric("Inversión Filtrada", f"€{filtrado_df['Valor (€M)'].sum():,.1f}M" if not filtrado_df.empty else "€0M")
    with col_res3:
        st.metric("Promedio de Edad", f"{filtrado_df['Edad'].mean():.1f} años" if not filtrado_df.empty else "N/A")

    st.markdown("---")

    # Selector de Vista: Tabla o Tarjetas
    view_mode = st.radio("Formato de visualización", ["📊 Tabla Interactiva", "🃏 Vista de Tarjetas"], horizontal=True)

    if view_mode == "📊 Tabla Interactiva":
        st.dataframe(filtrado_df.drop(columns=["id"], errors="ignore"), width="stretch", hide_index=True)
    else:
        if filtrado_df.empty:
            st.info("No hay jugadores que coincidan con los filtros seleccionados.")
        else:
            cols = st.columns(3)
            for idx, row in enumerate(filtrado_df.iterrows()):
                data = row[1]
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="player-card">
                        <h4>{data['Jugador']}</h4>
                        <p><b>Posición:</b> {data['Posición']} | <b>Edad:</b> {data['Edad']} años</p>
                        <p><b>De:</b> {data['Club Origen']} ➔ <b>A:</b> {data['Club Destino']}</p>
                        <p><span class="badge-liga">{data['Liga']}</span> &nbsp; <b>€{data['Valor (€M)']}M</b> ({data['Tipo']})</p>
                    </div>
                    """, unsafe_allow_html=True)

    # Descargar datos
    csv = filtrado_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar datos filtrados (CSV)",
        data=csv,
        file_name='transferencias_filtradas.csv',
        mime='text/csv',
    )

# ----------------------------------------------------
# PESTAÑA 2: DASHBOARD ESTADÍSTICO
# ----------------------------------------------------
elif menu == "Dashboard Estadístico":
    st.header("📊 Dashboard Ejecutivo de Mercado")
    
    if df.empty:
        st.info("No hay datos suficientes para mostrar estadísticas.")
    else:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Fichajes Registrados", len(df))
        with col2:
            gasto_total = df["Valor (€M)"].sum()
            st.metric("Inversión Global", f"€{gasto_total:,.1f}M")
        with col3:
            promedio_valor = df["Valor (€M)"].mean()
            st.metric("Valor Promedio", f"€{promedio_valor:,.1f}M")
        with col4:
            max_valor = df["Valor (€M)"].max()
            st.metric("Traspaso Récord", f"€{max_valor:,.1f}M")

        st.markdown("---")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.subheader("Inversión Total por Liga")
            gasto_liga = df.groupby("Liga")["Valor (€M)"].sum().reset_index()
            fig_liga = px.bar(gasto_liga, x="Liga", y="Valor (€M)", color="Liga", text_auto='.1fM', title="Gasto Acumulado por Liga (€M)")
            st.plotly_chart(fig_liga, width="stretch")
            
        with col_b:
            st.subheader("Distribución de Fichajes por Posición")
            pos_counts = df["Posición"].value_counts().reset_index()
            pos_counts.columns = ["Posición", "Cantidad"]
            fig_pos = px.pie(pos_counts, names="Posición", values="Cantidad", hole=0.4, title="Proporción por Posición")
            st.plotly_chart(fig_pos, width="stretch")

        col_c, col_d = st.columns(2)
        
        with col_c:
            st.subheader("Top Clubs Inversores (Destino)")
            top_destinos = df.groupby("Club Destino")["Valor (€M)"].sum().reset_index().sort_values(by="Valor (€M)", ascending=False).head(5)
            fig_dest = px.bar(top_destinos, x="Club Destino", y="Valor (€M)", color="Club Destino", title="Clubes que Más Invierten")
            st.plotly_chart(fig_dest, width="stretch")

        with col_d:
            st.subheader("Relación Edad vs. Valor de Mercado")
            fig_scatter = px.scatter(df, x="Edad", y="Valor (€M)", color="Liga", hover_data=["Jugador", "Club Destino"], title="Edad vs Valor (€M)")
            st.plotly_chart(fig_scatter, width="stretch")

# ----------------------------------------------------
# PESTAÑA 3: GESTIÓN CRUD DE TRASPASOS
# ----------------------------------------------------
elif menu == "Gestión CRUD de Traspasos":
    st.header("⚙️ Panel de Gestión y Control (CRUD - SQLite)")
    
    tab_add, tab_edit, tab_delete = st.tabs(["➕ Registrar Nuevo Traspaso", "✏️ Modificar Registro", "🗑️ Eliminar Registro"])
    
    with tab_add:
        st.subheader("Ingresar nuevo traspaso a la base de datos")
        with st.form("form_add"):
            c1, c2 = st.columns(2)
            with c1:
                new_jugador = st.text_input("Nombre del Jugador")
                new_edad = st.number_input("Edad", min_value=15, max_value=45, value=22)
                new_pos = st.selectbox("Posición", ["Delantero", "Centrocampista", "Defensa", "Portero"])
                new_liga = st.selectbox("Liga Destino", ["Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1"])
            with c2:
                new_origen = st.text_input("Club Origen")
                new_destino = st.text_input("Club Destino")
                new_valor = st.number_input("Valor de Traspaso (€M)", min_value=0.0, max_value=300.0, value=30.0, step=0.5)
                new_tipo = st.selectbox("Tipo de Traspaso", ["Traspaso Definitivo", "Cesión", "Traspaso Libre"])
                
            submitted = st.form_submit_button("Guardar en Base de Datos")
            if submitted:
                if new_jugador and new_origen and new_destino:
                    add_transfer(new_jugador, new_edad, new_pos, new_liga, new_origen, new_destino, new_valor, new_tipo)
                    st.toast(f"¡Traspaso de {new_jugador} guardado en SQLite!", icon="✅")
                    st.success(f"¡Traspaso de {new_jugador} registrado con éxito en la base de datos!")
                    st.rerun()
                else:
                    st.error("Por favor completa los campos obligatorios.")

    with tab_edit:
        st.subheader("Modificar un registro existente")
        if df.empty:
            st.info("No hay registros disponibles para editar.")
        else:
            jugador_a_editar = st.selectbox("Selecciona el jugador a editar", df["Jugador"].tolist())
            fila_sel = df[df["Jugador"] == jugador_a_editar].iloc[0]
            t_id = int(fila_sel["id"])
            
            with st.form("form_edit"):
                c1, c2 = st.columns(2)
                with c1:
                    edit_edad = st.number_input("Edad", min_value=15, max_value=45, value=int(fila_sel["Edad"]))
                    edit_pos = st.selectbox("Posición", ["Delantero", "Centrocampista", "Defensa", "Portero"], index=["Delantero", "Centrocampista", "Defensa", "Portero"].index(fila_sel["Posición"]))
                    edit_liga = st.selectbox("Liga Destino", ["Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1"], index=["Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1"].index(fila_sel["Liga"]))
                with c2:
                    edit_origen = st.text_input("Club Origen", value=fila_sel["Club Origen"])
                    edit_destino = st.text_input("Club Destino", value=fila_sel["Club Destino"])
                    edit_valor = st.number_input("Valor de Traspaso (€M)", min_value=0.0, max_value=300.0, value=float(fila_sel["Valor (€M)"]), step=0.5)
                    edit_tipo = st.selectbox("Tipo de Traspaso", ["Traspaso Definitivo", "Cesión", "Traspaso Libre"], index=["Traspaso Definitivo", "Cesión", "Traspaso Libre"].index(fila_sel["Tipo"]))
                
                edit_submitted = st.form_submit_button("Actualizar en Base de Datos")
                if edit_submitted:
                    update_transfer(t_id, edit_edad, edit_pos, edit_liga, edit_origen, edit_destino, edit_valor, edit_tipo)
                    st.toast(f"¡Registro de {jugador_a_editar} actualizado!", icon="✏️")
                    st.success(f"¡Registro de {jugador_a_editar} actualizado correctamente en SQLite!")
                    st.rerun()

    with tab_delete:
        st.subheader("Eliminar un registro")
        if df.empty:
            st.info("No hay registros disponibles para eliminar.")
        else:
            jugador_a_borrar = st.selectbox("Selecciona el jugador a eliminar", df["Jugador"].tolist(), key="del_select")
            fila_del = df[df["Jugador"] == jugador_a_borrar].iloc[0]
            t_id_del = int(fila_del["id"])
            
            if st.button("Eliminar Permanentemente de la Base de Datos", type="primary"):
                delete_transfer(t_id_del)
                st.toast(f"Traspaso de {jugador_a_borrar} eliminado.", icon="🗑️")
                st.success(f"Traspaso de {jugador_a_borrar} eliminado exitosamente de SQLite.")
                st.rerun()
