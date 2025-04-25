FROM python:3.12-buster AS base

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN apt-get update -y && apt-get upgrade -y

RUN pip install poetry

FROM base AS builder

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

ADD . /app
WORKDIR /app

COPY pyproject.toml poetry.lock ./
COPY bftp ./bftp

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --without dev --no-root

RUN poetry build  && \
    rm -rf $POETRY_CACHE_DIR

FROM python:3.12-slim-buster AS runtime

ENV DATABASE_URL="sqlite://:memory:" \
    OPENAI_API_KEY="sk-..." \
    OPENAI_API_BASE="https://api.openai.com/v1" \
    SECRET_TOKEN="some_token" \
    SERVER_PORT=8080

ENV PATH="/app/.venv/bin:$PATH" \
    VIRTUAL_ENV=/app/.venv

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY bftp ./bftp

ENTRYPOINT ["python", "-m", "bftp.main"]