from flask import request
from flask_swaggerui import render_swaggerui

from . import precache, scores, spec


def configure(config, bp, score_processor):
    """
    Configure a swagger route.

    Args:
        config: (dict): write your description
        bp: (todo): write your description
        score_processor: (bool): write your description
    """

    @bp.route("/v3/", methods=["GET"])
    def v3_index():
        """
        Render swagger index

        Args:
        """
        if "spec" in request.args:
            return spec.generate_spec(config)
        else:
            return render_swaggerui(swagger_spec_path="/v3/spec/")

    bp = precache.configure(config, bp, score_processor)
    bp = scores.configure(config, bp, score_processor)
    bp = spec.configure(config, bp, score_processor)

    return bp
