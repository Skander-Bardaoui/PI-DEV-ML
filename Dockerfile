# ═══════════════════════════════════════════════════════════════════════════
# DOCKERFILE - ML SERVICE (Python/FastAPI)
# ═══════════════════════════════════════════════════════════════════════════
# Multi-stage build pour optimiser la taille de l'image
# ═══════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────
# Stage 1: Builder - Installation des dépendances
# ─────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim as builder

# Métadonnées
LABEL maintainer="PI-DEV Team"
LABEL description="ML Service for Purchase Predictions"

# Variables d'environnement pour Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Installer les dépendances système nécessaires pour la compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Créer un environnement virtuel
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copier et installer les dépendances Python
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# ─────────────────────────────────────────────────────────────────────────
# Stage 2: Runtime - Image finale légère
# ─────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

# Arguments de build
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

# Labels OCI
LABEL org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.title="ML Service" \
      org.opencontainers.image.description="Machine Learning service for purchase predictions" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.vendor="PI-DEV Team" \
      org.opencontainers.image.source="https://github.com/your-org/pi-dev-ml"

# Installer uniquement les dépendances runtime nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Créer un utilisateur non-root pour la sécurité
RUN groupadd -r mluser && useradd -r -g mluser mluser

# Créer les répertoires nécessaires
RUN mkdir -p /app /app/logs /app/models && \
    chown -R mluser:mluser /app

# Définir le répertoire de travail
WORKDIR /app

# Copier l'environnement virtuel depuis le builder
COPY --from=builder /opt/venv /opt/venv

# Copier le code de l'application
COPY --chown=mluser:mluser app/ ./app/
COPY --chown=mluser:mluser requirements.txt .

# Créer un fichier .env par défaut (sera remplacé par ConfigMap en K8s)
RUN echo "LOG_LEVEL=INFO" > .env && \
    chown mluser:mluser .env

# Passer à l'utilisateur non-root
USER mluser

# Exposer le port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/v1/health')" || exit 1

# Commande de démarrage
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
