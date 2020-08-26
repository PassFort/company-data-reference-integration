from app.api.models import validate_model, GeoCodingCheck
from loqate_international_batch_cleanse.api import RequestHandler


def init_app(app):
    @app.route("/health", methods=['GET'])
    def health():
        return "ok"

    @app.route("/check", methods=['POST'])
    @validate_model(GeoCodingCheck)
    def addressCheck(data: GeoCodingCheck):
        return RequestHandler().handle_geocoding_check(data)
