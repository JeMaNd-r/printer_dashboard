FROM python:3.13-slim-bookworm@sha256:9d7f287598e1a5a978c015ee176d8216435aaf335ed69ac3c38dd1bbb10e8d64 as base
COPY --from=ghcr.io/astral-sh/uv:latest@sha256:cf4eedcaa81655197f625739489effcbe71b61ceb1506f332c3facae5deceded /uv /uvx /bin/

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
