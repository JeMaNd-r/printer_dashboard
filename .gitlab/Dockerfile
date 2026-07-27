FROM python:3.13-slim-bookworm@sha256:9d7f287598e1a5a978c015ee176d8216435aaf335ed69ac3c38dd1bbb10e8d64 as base
COPY --from=ghcr.io/astral-sh/uv:latest@sha256:df4cae8f3a96d175e2e5f992e597550000edbe78fdc2594d5cd8de1a217f504c /uv /uvx /bin/

ADD pyproject.toml uv.lock /app/

WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND noninteractive

COPY . .

FROM base as app

ENV UV_NO_DEV 1
RUN uv sync --group production
ENV UV_NO_SYNC 1
RUN uv run manage.py collectstatic --no-input
