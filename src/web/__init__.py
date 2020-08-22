# -*- coding: utf-8 -*-
from flask import Flask, current_app
from flask_cors import CORS

from src.web.routes import misc_bp, api_bp


def create_flask_application(config):
    application = Flask("Switcher_Recognizer")
    application.config.from_object(config.flask)
    application.register_blueprint(api_bp)
    application.debug = config.general.logging_level == 'DEBUG'

    with application.app_context():
        zip_obj = zip(['api', 'major', 'minor', 'patch'], config.general.api_version.split('.'))
        current_app.api_version = {k: v for k, v in zip_obj}

    CORS(application, resources={r'/*': {'origins': config.flask.ORIGINS}}, supports_credentials=True)
    return application
