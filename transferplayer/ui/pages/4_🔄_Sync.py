"""Página: Centro de Sincronización."""
import asyncio
import time
from datetime import datetime

import streamlit as st

from transferplayer.services.sync_service import sync_service
from transferplayer.ui.components import render_sync_logs

st.set_page_config(page_title="Sync Center", page_icon="🔄", layout="wide")

st.markdown("# 🔄 Centro de Sincronización")
st.markdown("### Sincroniza traspasos desde API-Football (RapidAPI)")
st.markdown("---")

# Status de configuración
col1, col2, col3 = st.columns(3)
with col1:
    from transferplayer.config import settings
    st.metric("API Configurada", "✅" if settings.football_api_key else "❌")
with col2:
    st.metric("Rate Limit", "100 req/día (Free)")
with col3:
    st.metric("Ligas objetivo", "5 (Top 5)")

st.markdown("---")

# Parámetros de sync
col_a, col_b = st.columns(2)
with col_a:
    season = st.number_input("Temporada", min_value=2010, max_value=2030, value=datetime.now().year)
with col_b:
    dry_run = st.checkbox("Dry Run (solo prueba, no guarda)", value=False)

# Botón de sincronización manual
if st.button("🚀 Iniciar Sincronización Manual", type="primary", use_container_width=True):
    if not settings.football_api_key:
        st.error("❌ FOOTBALL_API_KEY no configurada en Secrets/.env")
    else:
        with st.spinner("Sincronizando... Esto puede tardar varios minutos (rate limit 100 req/día)"):
            start = time.time()
            try:
                stats = asyncio.run(sync_service.sync_all_leagues(season=season))
                elapsed = time.time() - start

                st.success(f"✅ Sync completado en {elapsed:.1f}s")

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Estado", stats["status"])
                with col2:
                    st.metric("Obtenidos", stats["records_fetched"])
                with col3:
                    st.metric("Insertados", stats["records_inserted"])
                with col4:
                    st.metric("Actualizados", stats["records_updated"])

                if stats["errors"]:
                    st.warning(f"⚠️ {len(stats['errors'])} errores/warnings:")
                    for err in stats["errors"][:10]:
                        st.text(f"  • {err}")

            except Exception as e:
                st.error(f"❌ Error fatal: {e}")

st.markdown("---")

# Historial de sincronizaciones
st.subheader("📜 Historial de Sincronizaciones")

@st.cache_data(ttl=60)
def load_sync_history():
    return asyncio.run(sync_service.get_sync_history(20))

logs = load_sync_history()
render_sync_logs(logs)

# Auto-refresh
if st.button("🔄 Refrescar historial"):
    st.rerun()

st.markdown("---")
st.info("""
**ℹ️ Notas:**
- El plan gratuito de API-Football permite **100 peticiones/día**
- La sincronización completa de 5 ligas consume ~50-80 peticiones
- Se ejecuta automáticamente cada día a las 03:00 UTC via GitHub Actions
- Usa "Dry Run" para probar sin consumir cuota ni modificar la BD
""")
