def configure(config):

    from flask import Blueprint, Flask

    from . import routes
    from ..score_processors import ScoreProcessor

    app = Flask(__name__)
    app.config['APPLICATION_ROOT'] = config['ores']['wsgi']['application_root']

    bp = Blueprint('ores', __name__)

    sp_name = config['ores']['score_processor']
    score_processor = ScoreProcessor.from_config(config, sp_name)

    bp = routes.configure(config, bp, score_processor)

    app.register_blueprint(bp, url_prefix=config['ores']['wsgi']['url_prefix'])

    return app
