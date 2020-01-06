FROM python:3.7.4-alpine3.10

ARG git_key

ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8 \
    # This disables the ~/.ssh/known_hosts file
    GIT_SSH_COMMAND="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"

WORKDIR /src

COPY Pipfile Pipfile.lock Makefile /src/

RUN mkdir /srv/logs/ && \
    pip install pipenv && \
    mkdir -p ~/.ssh  && \
    echo "$git_key" > ~/.ssh/id_rsa && \
    chmod 600 ~/.ssh/id_rsa && \
    apk add --no-cache make openssh-client git build-base python3-dev libxml2-dev libxslt-dev && \
    pipenv run pip install --upgrade wheel && \
    pipenv install && \
    apk del --no-cache git openssh-client

COPY main.py /src
COPY coverage /src
COPY unit_coverage /src
COPY app /src/app
COPY e2e /src/e2e
COPY mock_data /src/mock_data

# Ports.
EXPOSE 8001

# Run gunicorn
CMD pipenv run gunicorn -w 4 -t 120 -b 0.0.0.0:8001 --log-level info --access-logfile - --access-logformat="%(h)s %(t)s %(r)s %(s)s" --enable-stdio-inheritance main:app
