FROM python:latest as base

RUN apt-get update -y && apt-get upgrade -y

FROM base as builder-base

RUN apt-get install -y curl

RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python3 -
ENV PATH="/opt/poetry/bin:$PATH"

FROM builder-base as builder

ADD . /workspace
WORKDIR /workspace

COPY . .
RUN poetry install && poetry build

FROM builder as runner

ENV DATABASE_URL="sqlite://:memory:" \
    SECRET_TOKEN="some_token" \
    SERVER_PORT=8080

EXPOSE 80
EXPOSE ${SERVER_PORT}

CMD ["poetry", "run", "python", "-m", "bftp"]