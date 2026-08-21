"""Página: Configuración y Ajustes."""
import asyncio

import streamlit as st

from transferplayer.config import settings
from transferplayer.db.init_db import reset_database, seed_database
from transferplayer.db.session import close_db, init_db

st.set_page_config(page_title="Configuración", page_icon="⚙️", layout="wide")

st.markdown("# ⚙️ Configuración y Diagnóstico")
st.markdown("---")

# Estado de conexión
st.subheader("🔌 Estado de Conexión")

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Base de Datos (Neon PostgreSQL)**")
    st.code(f"Host: {settings.neon_database_url.host}")
    st.code(f"DB: {settings.neon_database_url.path[1:] if settings.neon_database_url.path else 'N/A'}")
    st.code(f"SSL: {'Requerido' if 'sslmode=require' in str(settings.neon_database_url) else 'No'}")

with col2:
    st.markdown("**API Externa**")
    st.code(f"API-Football: {'✅ Configurada' if settings.football_api_key else '❌ No configurada'}")
    st.code(f"Host: {settings.football_api_host}")
    st.code(f"Neon API: {'✅ Configurada' if settings.neon_api_key else '❌ No configurada'}")

# Test de conexión
if st.button("🔍 Probar Conexión a BD", type="secondary"):
    with st.spinner("Probando conexión..."):
        try:
            asyncio.run(init_db())
            asyncio.run(close_db())
            st.success("✅ Conexión exitosa a PostgreSQL")
        except Exception as e:
            st.error(f"❌ Error de conexión: {e}")

st.markdown("---")

# Gestión de Base de Datos
st.subheader("🗄️ Gestión de Base de Datos")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🌱 Seed Inicial (15 traspasos)", use_container_width=True):
        with st.spinner("Insertando datos iniciales..."):
            try:
                asyncio.run(seed_database())
                st.success("✅ Seed completado")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {e}")

with col2:
    if st.button("🔄 Reset Completo (⚠️ Borra todo)", use_container_width=True, type="secondary"):
        if st.checkbox("Confirmo que quiero borrar TODOS los datos", key="confirm_reset"):
            with st.spinner("Reseteando base de datos..."):
                try:
                    asyncio.run(reset_database())
                    st.success("✅ BD reseteada y seed ejecutado")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")

with col3:
    if st.button("📊 Ejecutar Migraciones (Alembic)", use_container_width=True):
        with st.spinner("Ejecutando migraciones..."):
            import subprocess
            result = subprocess.run(["alembic", "upgrade", "head"], capture_output=True, text=True)
            if result.returncode == 0:
                st.success("✅ Migraciones aplicadas")
                st.code(result.stdout)
            else:
                st.error(f"❌ Error: {result.stderr}")

st.markdown("---")

# Variables de entorno
st.subheader("🔐 Variables de Entorno (Solo lectura)")

env_vars = {
    "APP_ENV": settings.app_env,
    "DB_NAME": settings.db_name,
    "NEON_DATABASE_URL": f"{settings.neon_database_url.host}/*****" if settings.neon_database_url else "No configurada",
    "FOOTBALL_API_KEY": "***" if settings.football_api_key else "No configurada",
    "FOOTBALL_API_HOST": settings.football_api_host,
    "NEON_API_KEY": "***" if settings.neon_api_key else "No configurada",
}

for key, value in env_vars.items():
    st.text_input(key, value=value, disabled=True)

st.markdown("---")

# Info de la app
st.subheader("ℹ️ Información de la Aplicación")

st.markdown("""
- **Versión:** 0.1.0
- **Framework:** Streamlit + SQLAlchemy 2.0 (async) + PostgreSQL (Neon)
- **API Datos:** API-Football (RapidAPI) - Free tier 100 req/día
- **Deploy:** Streamlit Cloud / Docker / GitHub Codespaces
- **Repo:** https://github.com/alejoxpp/TransferPlayer
- **Licencia:** MIT
""")

# Logs recientes
with st.expander("📋 Logs Recientes de Sync", expanded=False):
    from transferplayer.services.sync_service import sync_service
    logs = asyncio.run(sync_service.get_sync_history(10))
    for log in logs:
        status_icon = {"success": "✅", "error": "❌", "partial": "⚠️"}.get(log.status, "ℹ️")
        st.text(f"{status_icon} {log.created_at.strftime('%Y-%m-%d %H:%M')} | {log.source} | {log.status} | {log.records_fetched} fetched | {log.duration_ms}ms")
