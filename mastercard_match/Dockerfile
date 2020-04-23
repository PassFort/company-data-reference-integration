FROM python:3.7-alpine3.10

ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8

WORKDIR /src

RUN apk --no-cache upgrade

RUN apk add --no-cache make openssh-client git gcc musl-dev python3-dev libffi-dev openssl-dev

COPY Pipfile Pipfile.lock Makefile /src/

RUN pip install pipenv \
    && pipenv install \
    && apk del --no-cache git openssh-client gcc musl-dev libffi-dev

COPY main.py /src
COPY coverage /src
COPY app /src/app
COPY mock_data /src/mock_data

EXPOSE 8001

CMD pipenv run gunicorn -w 4 -t 120 -b 0.0.0.0:8001 --log-level info --access-logfile - --access-logformat="%(h)s %(t)s %(r)s %(s)s" --enable-stdio-inheritance main:app
