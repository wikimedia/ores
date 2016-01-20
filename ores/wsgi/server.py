import os


def configure(config):

    from flask import Blueprint, Flask

    from . import routes
    from ..score_processors import ScoreProcessor

    directory = os.path.dirname(os.path.realpath(__file__))

    app = Flask(__name__,
                static_url_path="/BASE_STATIC",
                template_folder=os.path.join(directory, 'templates'))

    app.config['APPLICATION_ROOT'] = config['ores']['wsgi']['application_root']

    bp = Blueprint('ores', __name__,
                   static_folder=os.path.join(directory, 'static'))

    sp_name = config['ores']['score_processor']
    score_processor = ScoreProcessor.from_config(config, sp_name)

    bp = routes.configure(config, bp, score_processor)

    app.register_blueprint(bp, url_prefix=config['ores']['wsgi']['url_prefix'])

    return app
