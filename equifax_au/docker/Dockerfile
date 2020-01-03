FROM python:3.7-slim

LABEL MANTAINER="Joelmir Ribacki" EMAIL="ribacki@devgrid.co.uk"

EXPOSE 8001

WORKDIR /app

COPY . /app

ENV FLASK_APP="app"

RUN pip install pipenv \
    && pipenv sync

ENTRYPOINT [ "pipenv", "run"]

CMD ["gunicorn","-w","1","-t","120","-b","0.0.0.0:8001","--log-level","info","--access-logfile","-","--access-logformat='%(h)s','%(t)s','%(r)s','%(s)s","--enable-stdio-inheritance","wsgi:app"]