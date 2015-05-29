def configure(config):
    if 'data_path' in config and 'nltk' in config['data_path']:
        import nltk
        nltk.data.path.append(config['data_path']['nltk'])

    from flask import Blueprint, Flask
    from revscoring.scorers import Scorer

    from . import routes

    app = Flask("ores")
    app.config["APPLICATION_ROOT"] = config['application_root']

    bp = Blueprint('ores', __name__)

    scorer_map = {wiki: Scorer.from_config(config, wiki)
                  for wiki in config['scorers']}

    bp = routes.configure(config, bp, scorer_map)

    app.register_blueprint(bp, url_prefix=config['url_prefix'])

    return app
