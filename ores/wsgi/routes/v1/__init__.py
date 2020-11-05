from flask import request
from flask_swaggerui import render_swaggerui

from . import scores, spec


def configure(config, bp, score_processor):
    """
    Configure a swagger spec.

    Args:
        config: (dict): write your description
        bp: (todo): write your description
        score_processor: (bool): write your description
    """

    bp = scores.configure(config, bp, score_processor)
    bp = spec.configure(config, bp, score_processor)

    @bp.route("/v1/", methods=["GET"])
    def v1_index():
        """
        Render swagger index

        Args:
        """
        if "spec" in request.args:
            return spec.generate_spec(config)
        else:
            return render_swaggerui(swagger_spec_path="/v1/spec/")

    return bp
