FROM python:3.7.4-alpine3.10

ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8

EXPOSE 8001

WORKDIR /src

RUN apk add --no-cache yarn openssh-client git 
COPY Pipfile Pipfile.lock package.json yarn.lock /src/


RUN pip install pipenv \
    && pipenv install \
    && yarn \
    && apk del --no-cache git openssh-client

COPY main.py /src
COPY unit_coverage /src
COPY app /src/app
COPY demo_data /src/demo_data
COPY e2e /src/e2e
COPY coverage /src

CMD pipenv run gunicorn -w 4 -t 120 -b 0.0.0.0:8001 --log-level info --access-logfile - --access-logformat="%(h)s %(t)s %(r)s %(s)s" --enable-stdio-inheritance main:app
