import os

import flask_swaggerui
import flask_wikimediaui


def configure(config):

    from flask import Blueprint, Flask

    from . import routes
    from ..scoring_systems import ScoringSystem

    directory = os.path.dirname(os.path.realpath(__file__))

    app = Flask(__name__,
                static_url_path="/BASE_STATIC",
                template_folder=os.path.join(directory, 'templates'))

    app.config['APPLICATION_ROOT'] = config['ores']['wsgi']['application_root']
    app.url_map.strict_slashes = False
    # Configure routes
    bp = Blueprint('ores', __name__,
                   static_folder=os.path.join(directory, 'static'),
                   url_prefix=config['ores']['wsgi']['url_prefix'])

    ss_name = config['ores']['scoring_system']
    scoring_system = ScoringSystem.from_config(config, ss_name)

    bp = routes.configure(config, bp, scoring_system)
    app.register_blueprint(bp)

    # Configure swagger-ui routes
    swagger_bp = flask_swaggerui.build_static_blueprint(
        'ores-swaggerui', __name__,
        url_prefix=config['ores']['wsgi']['url_prefix'])
    app.register_blueprint(swagger_bp)

    # Configure WikimediaUI routes
    wikimedia_bp = flask_wikimediaui.build_static_blueprint(
        'ores-wikimediaui', __name__,
        url_prefix=config['ores']['wsgi']['url_prefix'])
    app.register_blueprint(wikimedia_bp)

    return app
