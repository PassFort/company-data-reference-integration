# Integrations

This repo contains code for wrapping third party services.

It is also setup for continuous integration and deployment of these services. Staging is deployed to the staging cluster; production to the production cluster.

## Service API & Responsibilities

Please see: https://docs.google.com/document/d/1eHZANyyfG9WZT3-k3mVFFqu7u2LxpkmLweQej8710lU

# Writing a new service

You can use `/base` as a blueprint for your new service.

To work with CI, your service should: 

- [x] Include a Dockerfile in it's top level directory.
- [x] Not use any files outside of it's top level directory (these will not be added into the docker env for building).
- [x] We use yarn as a command runner. Your service should expose a package.json file with the following scripts:
    - `unit`: runs unit tests. These tests are run within the docker image, please make sure it installs any dependencies.
    - `e2e`: run e2e tests. These tests are run within the docker image, please make sure it installs any dependencies.
- [x] Be registered at the top of `deploy.py`.
- [x] Have a workflow added to `.circleci/config.yml`:
    - The jobs are configured to be reusable (by using workflow workspaces), you simply need to add a new `set_integration_YOURINTEGRATION` job.
    - You can then duplicate an existing workflow.
- [x] Update the kubernetes file `deployment.yaml`

> Please note how private keys are passed into the docker builder (for accessing private git repositories) as a build_arg. I recommend not disturbing this code as it's a little fragile!
