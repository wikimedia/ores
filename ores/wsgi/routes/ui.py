from flask import render_template


def configure(config, bp):
    """
    Decorator toilio.

    Args:
        config: (dict): write your description
        bp: (todo): write your description
    """
    @bp.route("/ui/", methods=["GET"])
    def ui():
        """
        Return a ui. template.

        Args:
        """
        return render_template("scorer.html")

    return bp
