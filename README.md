# ⚽ TransferPlayer

> **Prototipo de gestion de traspasos de fútbol** - Las 5 Grandes Ligas Europeas  
> Construido con **Streamlit**, **PostgreSQL (Neon)**, **SQLAlchemy 2.0**, **Alembic**, **API-Football**

[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://python.org)
[![License](https://img.shields.io/github/license/alejoxpp/TransferPlayer)](LICENSE)
[![CI](https://github.com/alejoxpp/TransferPlayer/actions/workflows/ci.yml/badge.svg)](https://github.com/alejoxpp/TransferPlayer/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/alejoxpp/TransferPlayer/branch/main/graph/badge.svg)](https://codecov.io/gh/alejoxpp/TransferPlayer)

---

## 🎯 Características

| Módulo | Descripción |
|--------|-------------|
| 🔍 **Explorador** | Filtros avanzados (liga, posición, tipo, club, valor, edad, búsqueda), vista tabla/tarjetas, export CSV |
| 📊 **Dashboard** | KPIs ejecutivos, gráficos Plotly interactivos (inversión por liga, distribución por posición, top clubs, edad vs valor) |
| ⚙️ **CRUD** | Crear, leer, actualizar, eliminar traspasos con validación Pydantic |
| 🔄 **Sync Center** | Sincronización manual/automática desde **API-Football (RapidAPI)** - 5 grandes ligas |
| ⚙️ **Configuración** | Test de conexión, seed/reset BD, migraciones Alembic, variables de entorno |

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                      STREAMLIT UI (Pages)                   │
│  Explorer │ Dashboard │ CRUD │ Sync │ Settings              │
├─────────────────────────────────────────────────────────────┤
│                       SERVICES LAYER                         │
│  TransferService  │  SyncService                            │
├─────────────────────────────────────────────────────────────┤
│                        DATA LAYER                            │
│  SQLAlchemy 2.0 Async  │  Repository Pattern  │  Alembic   │
│  PostgreSQL (Neon)     │  Pydantic Models                   │
├─────────────────────────────────────────────────────────────┤
│                      EXTERNAL APIs                           │
│  API-Football (RapidAPI)  │  Rate Limited (100 req/día)     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quickstart

### Opción A: Local con Docker (recomendado)

```bash
# 1. Clonar
git clone https://github.com/alejoxpp/TransferPlayer.git
cd TransferPlayer

# 2. Configurar .env
cp .env.example .env
# Edita .env con tus claves (NEON_DATABASE_URL, FOOTBALL_API_KEY)

# 3. Levantar todo (PostgreSQL + pgAdmin + App)
docker-compose up --build

# 4. Abrir http://localhost:8501
```

### Opción B: GitHub Codespaces (0 setup)

1. Abre el repo en GitHub
2. **Code → Codespaces → Create codespace on main**
3. Espera a que termine `postCreateCommand`
4. Puerto 8501 se abre automáticamente → ¡Listo!

### Opción C: Local nativo

```bash
# Requisitos: Python 3.11+, PostgreSQL 16
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env  # Configura NEON_DATABASE_URL
alembic upgrade head
python -m transferplayer.db.init_db
streamlit run transferplayer/ui/main.py
```

<details>
<summary>🪟 Variante PowerShell (Windows)</summary>

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
Copy-Item .env.example .env  # Configura NEON_DATABASE_URL
alembic upgrade head
streamlit run transferplayer/ui/main.py
```
</details>

---

## 🔧 Configuración

### Variables de entorno (`.env`)

```bash
# Database (Neon PostgreSQL - usa Pooled connection string)
NEON_DATABASE_URL=postgresql://user:pass@ep-xxx.pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require
DB_NAME=transferplayer

# Neon API (opcional - para branch management via GitHub Actions)
NEON_API_KEY=napi_xxxxxxxxxxxx

# Football API (API-Football via RapidAPI)
FOOTBALL_API_KEY=tu_rapidapi_key
FOOTBALL_API_HOST=v3.football.api-sports.io

# App
APP_ENV=development
STREAMLIT_SERVER_PORT=8501
```

### Obtener claves API

| Servicio | URL | Plan Gratis |
|----------|-----|-------------|
| **Neon PostgreSQL** | https://console.neon.tech | 3 GB, 190h compute/mes |
| **API-Football** | https://rapidapi.com/api-sports-api/api/api-football | 100 req/día |

---

## 🧪 Testing

```bash
# Tests unitarios + integración + coverage
pytest -q --cov=transferplayer --cov-report=term-missing

# Solo unitarios
pytest tests/unit -q

# Solo integración (requiere BD)
pytest tests/integration -q
```

---

## ☁️ Deploy en Render (producción)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/alejoxpp/TransferPlayer)

El repo incluye un **Blueprint** (`render.yaml`) que aprovisiona el web service Docker automáticamente:

1. Pulsa el botón de arriba (o desde [dashboard.render.com](https://dashboard.render.com) → **New → Blueprint** → selecciona este repo)
2. Render lee `render.yaml` y te pide los secretos:
   - `NEON_DATABASE_URL` → cadena de conexión **pooled** de Neon (obligatoria)
   - `FOOTBALL_API_KEY` → clave de RapidAPI (opcional; solo la página Sync la usa)
3. **Apply** → build Docker + `alembic upgrade head` automático en cada arranque
4. URL pública tipo `https://transferplayer-xxxx.onrender.com` (health check: `/_stcore/health`)

> 💡 El contenedor escucha en `$PORT` (Render/Railway lo inyectan; en local cae a 8501), por lo que **el mismo Dockerfile funciona en Render y Railway** sin cambios.
>
> ⚠️ **Plan free de Render:** la app se duerme tras ~15 min sin tráfico (cold start ~1 min). Para 24/7 sin sleeps usa el plan Starter.

---

## 🐳 Docker

```bash
# Build
docker build -t transferplayer .

# Run (requiere BD externa o docker-compose)
docker run -p 8501:8501 \
  -e NEON_DATABASE_URL="postgresql://..." \
  -e FOOTBALL_API_KEY="..." \
  transferplayer
```

---

## 📦 Estructura del Proyecto

```
TransferPlayer/
├── .github/workflows/     # CI/CD (ci, sync-data)
├── .devcontainer/         # GitHub Codespaces config
├── alembic/               # Migraciones BD
├── scripts/               # CLI scripts (migración, sync)
├── tests/                 # Unit + Integration tests
├── transferplayer/        # Package principal
│   ├── api/               # Clientes API externas
│   ├── db/                # SQLAlchemy, Repository, Init
│   ├── models/            # ORM + Domain (Pydantic)
│   ├── services/          # Business logic
│   └── ui/                # Streamlit pages + components
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml         # Config moderna (ruff, mypy, pytest, black)
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

---

## 🔄 CI/CD Pipeline

| Workflow | Trigger | Qué Hace |
|----------|---------|----------|
| **CI** | Push/PR | Ruff + Black + MyPy + Tests + Coverage + Docker Build |
| **Sync Data** | Cron 03:00 UTC / Manual | Sync API-Football → Neon + Notificaciones Slack |

**Deploy:** vía **Render Blueprint** (`render.yaml`) — auto-deploy en cada push a `main`.

---

## 📊 Demo

> **Render:** `https://transferplayer.onrender.com` *(URL exacta tras el primer deploy)*

---

## 🤝 Contribuir

1. Fork del repo
2. Crea rama: `git checkout -b feat/mi-feature`
3. Commit convencional: `git commit -m "feat: añade filtro por temporada"`
4. Push: `git push origin feat/mi-feature`
5. Abre **Pull Request** → CI verifica calidad

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para detalles.

---

## 📄 Licencia

MIT License - ver [LICENSE](LICENSE)

---

## 🙌 Agradecimientos

- [API-Football](https://rapidapi.com/api-sports-api/api/api-football) por datos de traspasos
- [Neon](https://neon.tech) por PostgreSQL serverless gratis
- [Streamlit](https://streamlit.io) por el framework tan productivo
- [Football-Data.org](https://www.football-data.org) como alternativa de API