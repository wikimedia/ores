def configure(config):
    if 'data_paths' in config['ores'] and \
       'nltk' in config['ores']['data_paths']:
        import nltk
        nltk.data.path.append(config['ores']['data_paths']['nltk'])

    from flask import Blueprint, Flask

    from . import routes
    from ..scorer import Scorer

    app = Flask(__name__)
    app.config['APPLICATION_ROOT'] = config['ores']['wsgi']['application_root']

    bp = Blueprint('ores', __name__)

    scorers = {wiki: Scorer.from_config(config, wiki)
               for wiki in config['ores']['scorers']}

    bp = routes.configure(config, bp, scorers)

    app.register_blueprint(bp, url_prefix=config['ores']['wsgi']['url_prefix'])

    return app
