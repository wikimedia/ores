import importlib
from collections import OrderedDict

from flask import render_template


def configure(config, bp):
    """
    Configure a boke a.

    Args:
        config: (dict): write your description
        bp: (todo): write your description
    """

    @bp.route("/versions/")
    def versions():
        """
        Returns a list of versions of all versions.

        Args:
        """
        modules = ['ores', 'revscoring', 'editquality', 'wikiclass',
                   'draftquality']
        versions = OrderedDict()
        for module in modules:
            try:
                versions[module] = importlib.import_module(module).__version__
            except ImportError:
                pass

        return render_template("versions.html", versions=versions)

    return bp
