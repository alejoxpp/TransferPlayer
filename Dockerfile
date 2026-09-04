# Multi-stage build for TransferPlayer
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY transferplayer/ ./transferplayer/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Runtime stage
FROM python:3.11-slim AS runtime

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Copy from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app /app

# Environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Health check: python-slim no incluye curl; usamos urllib respetando $PORT
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD python -c "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.environ.get('PORT', '8501') + '/_stcore/health')" || exit 1

# Render/Railway inyectan el puerto en $PORT (10000 por defecto en Render);
# en local/docker-compose cae a 8501. Las migraciones son idempotentes y
# `exec` cede el PID 1 a streamlit para recibir señales (SIGTERM en redeploys).
CMD ["sh", "-c", "alembic upgrade head && exec streamlit run transferplayer/ui/main.py --server.port=${PORT:-8501} --server.address=0.0.0.0"]