import os

import flask_swaggerui
import flask_wikimediaui


def configure(config):

    from flask import Blueprint, Flask

    from . import routes
    from ..score_processors import ScoreProcessor

    directory = os.path.dirname(os.path.realpath(__file__))

    app = Flask(__name__,
                static_url_path="/BASE_STATIC",
                template_folder=os.path.join(directory, 'templates'))

    app.config['APPLICATION_ROOT'] = config['ores']['wsgi']['application_root']

    # Configure routes
    bp = Blueprint('ores', __name__,
                   static_folder=os.path.join(directory, 'static'),
                   url_prefix=config['ores']['wsgi']['url_prefix'])

    sp_name = config['ores']['score_processor']
    score_processor = ScoreProcessor.from_config(config, sp_name)

    bp = routes.configure(config, bp, score_processor)
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
