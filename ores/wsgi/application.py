import json
import os

from flask import Blueprint, Flask, request
from revscoring.scorers import Scorer

from . import routes


def configure(config):
    app = Flask("ores")
    app.config["APPLICATION_ROOT"] = config['application_root']

    bp = Blueprint('ores', __name__)

    scorer_map = {wiki:Scorer.from_config(config, wiki)
                  for wiki in config['scorers']}

    bp = routes.configure(config, bp, scorer_map)

    app.register_blueprint(bp, url_prefix=config['url_prefix'])

    return app
