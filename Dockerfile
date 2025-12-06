# =============================================================================
# Odoo 18 Dockerfile - Multi-stage build for development and production
# Compatible with Render deployment
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder - Install dependencies
# -----------------------------------------------------------------------------
FROM python:3.11-slim-bookworm AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libldap2-dev \
    libsasl2-dev \
    libssl-dev \
    libffi-dev \
    libjpeg-dev \
    libpng-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# -----------------------------------------------------------------------------
# Stage 2: Runtime - Minimal production image
# -----------------------------------------------------------------------------
FROM python:3.11-slim-bookworm AS runtime

LABEL maintainer="NarimERP Team"
LABEL description="Odoo 18 ERP - Custom Build"
LABEL version="18.0"

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    # PostgreSQL client for database operations
    libpq5 \
    postgresql-client \
    # LDAP support
    libldap-2.5-0 \
    libsasl2-2 \
    # Image processing
    libjpeg62-turbo \
    libpng16-16 \
    # XML processing
    libxml2 \
    libxslt1.1 \
    # PDF generation (wkhtmltopdf)
    wkhtmltopdf \
    xfonts-75dpi \
    xfonts-base \
    fontconfig \
    # Utilities
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Create odoo user (non-root for security)
RUN useradd --create-home --home-dir /opt/odoo --shell /bin/bash odoo

# Set working directory
WORKDIR /opt/odoo

# Set Python path to find odoo module
ENV PYTHONPATH=/opt/odoo

# Create necessary directories
RUN mkdir -p /opt/odoo/data \
    /opt/odoo/custom-addons \
    /opt/odoo/config \
    /var/log/odoo \
    && chown -R odoo:odoo /opt/odoo /var/log/odoo

# Copy Odoo source code
COPY --chown=odoo:odoo ./odoo /opt/odoo/odoo
COPY --chown=odoo:odoo ./setup /opt/odoo/setup
COPY --chown=odoo:odoo ./setup.py /opt/odoo/
COPY --chown=odoo:odoo ./setup.cfg /opt/odoo/

# Copy configuration
COPY --chown=odoo:odoo ./config/odoo.conf /opt/odoo/config/odoo.conf

# Switch to non-root user
USER odoo

# Expose Odoo ports
# 8069: HTTP
# 8071: Longpolling (for live chat, notifications)
# 8072: Gevent (websocket)
EXPOSE 8069 8071 8072

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8069/web/health || exit 1

# Default command - Odoo 18 runs as a Python module
CMD ["python", "-m", "odoo", "-c", "/opt/odoo/config/odoo.conf"]
