# FlagDojo Dockerfile
# Uses the official uv Docker image for fast, reliable Python package management

FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

# Copy dependency files first (for better layer caching)
COPY pyproject.toml ./
COPY uv.lock* ./

# Install dependencies using uv
# --frozen: Use exact versions from uv.lock
# --no-dev: Skip development dependencies in production
RUN uv sync --frozen --no-dev

# Copy application code
COPY app/ ./app/
COPY challenges/ ./challenges/
COPY scripts/ ./scripts/
COPY run.py ./
COPY .env.example ./.env

# Create data directory for SQLite database
RUN mkdir -p /app/data && \
    chmod 755 /app/data

# Create a non-root user
RUN useradd -m -u 1000 flagdojo && \
    chown -R flagdojo:flagdojo /app

# Switch to non-root user
USER flagdojo

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/', timeout=5)" || exit 1

# Initialize database and start application
CMD ["sh", "-c", "uv run python scripts/init_db.py && uv run gunicorn -b 0.0.0.0:5000 -w 2 --timeout 120 run:app"]
