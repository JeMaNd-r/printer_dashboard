FROM python:3.13-slim-bookworm as base
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

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
