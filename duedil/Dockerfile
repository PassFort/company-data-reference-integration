FROM frolvlad/alpine-python3

ARG git_key

ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8 \
    # This disables the ~/.ssh/known_hosts file
    GIT_SSH_COMMAND="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"

WORKDIR /src

COPY Pipfile Pipfile.lock package.json /src/

RUN mkdir /srv/logs/ && \
    pip install pipenv==2018.10.13 && \
    mkdir -p ~/.ssh  && \
    echo "$git_key" > ~/.ssh/id_rsa && \
    chmod 600 ~/.ssh/id_rsa && \
    apk add --no-cache yarn openssh-client git && \
    pipenv run pip install --upgrade wheel && \
    pipenv install && \
    yarn && \
    apk del --no-cache git openssh-client

COPY main.py /src
COPY coverage /src
COPY app /src/app
COPY demo_data /src/demo_data
COPY e2e /src/e2e

# Ports.
EXPOSE 8001

# Run gunicorn
CMD pipenv run gunicorn -w 4 -t 120 -b 0.0.0.0:8001 --log-level info --access-logfile - --access-logformat="%(h)s %(t)s %(r)s %(s)s" --enable-stdio-inheritance main:app
