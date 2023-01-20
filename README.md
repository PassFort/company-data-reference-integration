# Company Data Reference Integration

This project provides an example of a service implementing a [PassFort Integration](https://passfort.github.io/integration-docs/)
supporting electronic identity verification.

Only demo checks are supported, no provider specific logic is implemented.


## Running Locally

Requires at least Python 3.7

You can run the application in a Python environment of your choosing, install the
dependencies from `requirements.txt` and `requirements-dev.txt` and start
the service with `python main.py`.


## Deploying

This stateless service is designed to be deployed to Google App Engine, the `app.yaml`
and `Dockerfile` reflect this. However, there is no requirement for your integration
to use such a platform.


## Monitored Polling Reference

The monitored polling reference implementation is available at the
path `/monitored-polling/`. It uses the same demo data as the synchronous
reference implementation by default. To support testing ongoing monitoring changes,
there is a private API at `/monitored-polling/monitored_checks/<reference>/_update`.

The reference is injected as the external generic reference into the original check
result for ease of testing.
The private update endpoint is authenticated similarly to the other endpoints, thus
every request must be signed as per the officially supported  HTTP Signature
draft spec.
The payload for the update endpoint must be in the same format as that returned
by the poll endpoint.
