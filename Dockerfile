# Vrixo — multi-stage Dockerfile
# Feature #73: Containerized Python backend and AI worker

# ---------- Stage 1: Builder ----------
FROM python:3.13-slim AS builder

WORKDIR /build

# Install system deps needed for OpenCV + torch wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps into a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY ai/requirements.txt ./ai/requirements.txt
COPY requirements-dev.txt ./requirements-dev.txt

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r ai/requirements.txt && \
    pip install --no-cache-dir streamlit

# ---------- Stage 2: Runtime ----------
FROM python:3.13-slim AS runtime

# Create unprivileged user
RUN useradd --create-home --shell /bin/bash vrixo

# Install runtime system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the prepared venv from the builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copy application code
COPY --chown=vrixo:vrixo ai ./ai
COPY --chown=vrixo:vrixo web ./web
COPY --chown=vrixo:vrixo pyproject.toml README.md ./

USER vrixo

EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run Streamlit
CMD ["streamlit", "run", "web/app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
