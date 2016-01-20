from flask import render_template


def configure(config, bp):
    @bp.route("/ui/", methods=["GET"])
    def ui():
        return render_template("scorer.html")

    return bp
