FROM python:3.12-slim-bookworm

RUN pip install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/agent_poetry_cache

# Install Python and pip
RUN apt-get update && \
    apt-get install -y git python3-psycopg2 python3-poetry && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./pyproject.toml ./pyproject.toml
COPY ./poetry.lock ./poetry.lock
RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --no-root

COPY ./agent ./agent
CMD ["poetry", "run", "python", "agent/main.py"]