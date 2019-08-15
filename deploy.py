import os
from passfort_deployment import deploy_file, \
    project_uri, \
    logging, \
    run_command, \
    use_cluster, \
    git_tree_hash, \
    clean_pyc_files, \
    init, \
    argparse

integrations = {
    'comply_advantage': './comply_advantage',
    'duedil': './duedil',
    'equifax': './equifax',
    'onfido': './onfido',
    'vsure': './vsure',
    'bvd': './bvd',
    'worldcheck': './worldcheck',
    'trulioo': './trulioo',
}

sentry = {
    'production': 'https://0ca8ed37de6944919f2051bdb03a8366:d085be914c0f4e459a2bd7a767fddeb2@sentry.io/249150',
    'staging': 'https://498e4546bca44bfeb904f52c46e8349a:9dede010403e4f278804c90dee535656@sentry.io/246508',
}


def get_container_uri(service, container_tag):
    return "{}/integrations-{}:{}".format(project_uri, service, container_tag)


def build_container(container_tag, service, private_key, push=False):
    container_uri = get_container_uri(service, container_tag)
    build_dir = integrations[service]

    logging.info("Building " + container_uri)
    run_command(
        [
            "docker", "build",
            "--build-arg", 'git_key=' + private_key,
            "--tag", container_uri,
            build_dir
        ],
        stdout=True
    )

    if push:
        run_command(
            ["gcloud", "docker", "--", "push", container_uri],
            stdout=True
        )


def deploy_container(cluster, service, container_tag):
    container_uri = get_container_uri(service, container_tag)
    build_dir = integrations[service]
    sentry_url = sentry.get(cluster, '')

    # Container
    deploy_file(
        build_dir + "/deployment.yaml",
        container_uri,
        container_uri=container_uri,
        cluster=cluster,
        sentry_url=sentry_url,
    )


def get_private_key():
    file_name = os.environ.get('GITHUB_KEY_LOCATION', 'id_rsa')
    loc = os.path.expanduser('~/.ssh/' + file_name)
    with open(loc, 'r') as f:
        return f.read()


def main(cluster, service, tag, build, deploy, all, auto):
    is_local_cluster = cluster == 'local'
    services = service or []

    if not is_local_cluster:
        use_cluster(cluster)

    if all:
        if len(services):
            logging.error('Cannot specify --all and --service at same time')
            exit(1)

        services = list(integrations.keys())

    for service in services:
        if service not in integrations:
            logging.error('Could not find service ' + service)
            exit(1)

    if auto:
        if cluster == "production" or tag:
            build = False
            deploy = True
        else:
            build = True
            deploy = True

    if tag:
        if build:
            logging.error("Cannot specify a custom tag when building!")
            exit(1)
        container_tag = tag
    else:
        container_tag = git_tree_hash()

    if build:
        private_key = get_private_key()

        for service in services:
            clean_pyc_files(".")
            logging.info("Building " + container_tag)
            build_container(container_tag, service, private_key, not is_local_cluster)

            logging.info("Build completed")

    if deploy:
        for service in services:
            logging.info("Deploying {} to {}".format(container_tag, cluster))
            deploy_container(cluster, service, container_tag)
            logging.info("Deploy completed")


if __name__ == '__main__':
    init(__file__, 1.0)

    # Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s", "--service",
        help="one of [{}]".format(', '.join(integrations)),
        action='append'
    )
    parser.add_argument("cluster", help="staging or production")
    parser.add_argument("-b", "--build", action="store_true")
    parser.add_argument("-d", "--deploy", action="store_true")
    parser.add_argument("-a", "--auto", action="store_true")
    parser.add_argument("-A", "--all", action="store_true", help='all integrations')
    parser.add_argument("--tag", type=str)
    args = parser.parse_args()

    # Run!
    main(**args.__dict__)
