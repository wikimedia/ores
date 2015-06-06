
from . import scores


def configure(config, bp, scorers):

    @bp.route("/", methods=["GET"])
    def index():
        return "Hi!  I'm ORES.  :D"

    bp = scores.configure(config, bp, scorers)

    return bp
