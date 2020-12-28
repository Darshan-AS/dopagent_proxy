FROM python:3.9-slim as base

# Turn off UI interaction
ENV DEBIAN_FRONTEND noninteractive

# Setup locales
RUN apt-get update && apt-get install -y --no-install-recommends \
    locales \
    && echo 'en_US.UTF-8 UTF-8' > /etc/locale.gen && /usr/sbin/locale-gen \
    && rm -rf /var/lib/apt/lists/*

# Set ENV for locales, python, and pip
ENV LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=off

# Set project specific ENVs (APP_MODULE is for uvicorn)
ENV WORKING_PATH=/dopagent_proxy \
    APP_MODULE=proxy.main:app \
    APP_HOST=0.0.0.0 \
    APP_PORT=8000


FROM base AS build

# Install build tools
RUN apt-get update && apt-get install -y \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# Tell poetry to create venv in current directory and turn off UI
ENV POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    POETRY_NO_ANSI=1

# Get poetry and install non dev project dependencies
COPY pyproject.toml poetry.lock ./
RUN pip install --upgrade pip \
    && pip install poetry \
    && poetry install --no-root --no-dev \
    && rm -rf pyproject.toml poetry.lock

# Add venv to path
ENV PATH /.venv/bin:$PATH


FROM build as dev

# Set default working directory
WORKDIR ${WORKING_PATH}

# Tell poetry to skip creating venv (reuses venv from build target)
ENV POETRY_VIRTUALENVS_CREATE=false

# Install project dependencies including dev
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

# Copy application into container. This is just a fallback. Use volumes to mount the source code
COPY . .

# Run the application
CMD uvicorn ${APP_MODULE} --host ${APP_HOST} --port ${APP_PORT}
EXPOSE 8000


FROM base AS prod

# Create and switch to a new user
RUN useradd dopagent
USER dopagent

# Copy venv from build stage
COPY --from=build .venv .venv
ENV PATH /.venv/bin:$PATH

# Set default working directory
WORKDIR ${WORKING_PATH}

# Copy application into container
COPY . .

# Run the application
ENTRYPOINT uvicorn ${APP_MODULE} --host ${APP_HOST} --port ${APP_PORT}
EXPOSE 8000
