FROM python:3.7-alpine3.12

ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8

EXPOSE 8001

WORKDIR /app

RUN apk --no-cache upgrade

RUN apk add --no-cache make openssh-client git build-base python3-dev libxml2-dev libxslt-dev
COPY Pipfile Pipfile.lock Makefile /app/

ENV FLASK_APP="app"

RUN pip install pipenv \
    && pipenv install \
    && apk del --no-cache git openssh-client

COPY . /app

CMD pipenv run gunicorn -w 4 -t 120 -b 0.0.0.0:8001 --log-level info --access-logfile - --access-logformat="%(h)s %(t)s %(r)s %(s)s" --enable-stdio-inheritance main:app
