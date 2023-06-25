FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1
ENV PYTHONUNBUFFERED 1

ARG PIPENV_FLAGS

EXPOSE 80
WORKDIR /app

RUN set -ex &&  apt update && apt upgrade -y && rm -rf /var/lib/apt/lists/*

COPY Pipfile Pipfile.lock /app/

RUN pip install pipenv==2023.6.18
RUN pipenv install --system ${PIPENV_FLAGS}

COPY . /app/