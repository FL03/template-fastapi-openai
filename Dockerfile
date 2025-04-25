FROM python:latest AS base

RUN apt-get update -y && apt-get upgrade -y

FROM base AS builder-base

RUN apt-get install -y curl

RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python3 -
ENV PATH="/opt/poetry/bin:$PATH"

FROM builder-base AS builder

ADD . /workspace
WORKDIR /workspace

COPY . .
RUN poetry install && poetry build

FROM builder AS runner

ENV DATABASE_URL="sqlite://:memory:" \
    OPENAI_API_KEY="sk-..." \
    OPENAI_API_BASE="https://api.openai.com/v1" \
    SECRET_TOKEN="some_token" \
    SERVER_PORT=8080

EXPOSE 80
EXPOSE ${SERVER_PORT}

CMD ["poetry", "run", "python", "-m", "bftp"]