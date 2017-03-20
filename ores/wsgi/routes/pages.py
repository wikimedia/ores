from collections import OrderedDict
from flask import render_template
import importlib

def configure(config, bp):

    @bp.route("/version/")
    def version():
        modules = ['ores', 'revscoring', 'editquality', 'wikiclass', 'draftquality']
        versions = OrderedDict()
        for module in modules:
            try:
                versions[module] = importlib.import_module( module ).__version__
            except ImportError:
                pass

        return render_template("version.html",
                               versions=versions)

    return bp
