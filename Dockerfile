FROM python:3.12.10 AS base

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

COPY . /app/

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --no-root

RUN poetry build  && \
    rm -rf $POETRY_CACHE_DIR

FROM python:3.12.10-slim AS runtime

ENV DATABASE_URL="sqlite://:memory:" \
    SERVER_PORT=8080

ENV PATH="/app/.venv/bin:$PATH" \
    VIRTUAL_ENV=/app/.venv

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY bftp ./bftp

EXPOSE 80
EXPOSE ${SERVER_PORT}

ENTRYPOINT ["python", "-m", "fastapi", "run", "bftp", "--host", "0.0.0.0", "--port", ${SERVER_PORT}]