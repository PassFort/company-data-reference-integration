from flask import send_file, Blueprint

metadata_api = Blueprint("metadata", __name__)


@metadata_api.route('/')
def index():
    return send_file('../static/metadata.json', cache_timeout=-1)
