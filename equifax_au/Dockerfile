FROM python:3.7.4-alpine3.10

ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8

EXPOSE 8001

WORKDIR /app

RUN apk add --no-cache make libxslt gcc musl-dev libxslt-dev openssh-client git
COPY Pipfile Pipfile.lock /app/

ENV FLASK_APP="app"

# Build and install deps, then remove build deps, leaving libxslt and make as
# they're required at runtime.
RUN pip install pipenv \
    && pipenv install --dev \
    && apk del --no-cache git openssh-client libxslt-dev musl-dev gcc

COPY . /app

CMD pipenv run gunicorn -w 4 -t 120 -b 0.0.0.0:8001 --log-level info --access-logfile - --access-logformat="%(h)s %(t)s %(r)s %(s)s" --enable-stdio-inheritance wsgi:app
