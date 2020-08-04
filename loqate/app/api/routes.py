import logging
import os
from flask import request
from app.api.models import validate_model, GeoCodingCheck


def init_app(app):
    @app.route("/health", methods=['GET'])
    def health():
        return "ok"

    @app.route("/check", methods=['POST'])
    @validate_model(GeoCodingCheck)
    def addressCheck(data: GeoCodingCheck):
        return {}, 400
