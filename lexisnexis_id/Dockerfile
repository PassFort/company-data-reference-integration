FROM python:3.7.4-alpine3.10

EXPOSE 8001

WORKDIR /app

RUN apk add --no-cache make gcc musl-dev openssh-client git
COPY Pipfile Pipfile.lock /app/

ENV FLASK_APP="app"

# Build and install deps, then remove build deps, leaving libxslt and make as
# they're required at runtime.
RUN pip install pipenv \
    && pipenv sync --dev \
    && apk del --no-cache git openssh-client musl-dev gcc

COPY . /app

CMD pipenv run gunicorn -w 4 -t 120 -b 0.0.0.0:8001 --log-level info --access-logfile - --access-logformat='%(h)s','%(t)s','%(r)s','%(s)s' --enable-stdio-inheritance main:app