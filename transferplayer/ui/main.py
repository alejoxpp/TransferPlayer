"""Entry point principal para Streamlit."""
import streamlit as st

# Configuración de página global
st.set_page_config(
    page_title="TransferPlayer - Traspasos Fútbol",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS global
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .kpi-card {
        background: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center;
        border-top: 4px solid #1f77b4;
    }
    .player-card {
        background: white; padding: 18px; border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 15px;
        border-left: 5px solid #2ca02c;
    }
    .badge-liga {
        background-color: #e2e8f0; color: #1e293b; padding: 3px 8px;
        border-radius: 6px; font-size: 12px; font-weight: 600;
    }
    section[data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e2e8f0; }
    .stMetric { background: white; padding: 16px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
</style>
""", unsafe_allow_html=True)

# Sidebar global
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1508098682722-e99c43a406b2?auto=format&fit=crop&w=600&q=80", use_container_width=True)
    st.markdown("## ⚽ TransferPlayer")
    st.caption("Prototipo profesional - 5 Grandes Ligas")
    st.markdown("---")

    # Navigation hint
    st.markdown("""
    **Navegación:**
    - 🔍 **Explorador** - Filtra y busca traspasos
    - 📊 **Dashboard** - Estadísticas y gráficos
    - ⚙️ **CRUD** - Gestión completa (Crear/Editar/Eliminar)
    - 🔄 **Sync Center** - Sincroniza con API-Football
    - ⚙️ **Configuración** - Estado y diagnóstico
    """)

    st.markdown("---")
    st.caption(f"v0.1.0 | {st.secrets.get('APP_ENV', 'dev')}")

# El contenido real se renderiza en cada page (Streamlit multipage)
st.markdown("# ⚽ TransferPlayer")
st.markdown("### Prototipo Profesional de Traspasos - Las 5 Grandes Ligas")
st.markdown("---")

col1, col2, col3 = st.columns(3)
with col1:
    st.info("👈 **Usa el menú lateral** para navegar entre páginas")
with col2:
    st.markdown("""
    **Funcionalidades:**
    - 🔍 Explorador con filtros avanzados
    - 📊 Dashboard ejecutivo con Plotly
    - ⚙️ CRUD completo sobre PostgreSQL
    - 🔄 Sync automático desde API-Football
    - 🐳 Docker + GitHub Actions CI/CD
    """)
with col3:
    st.markdown("""
    **Stack Tecnológico:**
    - Python 3.11 + Streamlit
    - SQLAlchemy 2.0 (async) + Alembic
    - PostgreSQL (Neon Serverless)
    - Pydantic v2 + Pydantic Settings
    - Plotly + Pandas
    """)

st.markdown("---")
st.caption("Desarrollado por alejoxpp | MIT License")
