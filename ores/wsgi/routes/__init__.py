
from . import scores


def configure(config, bp, scorer_map):

    @bp.route("/", methods=["GET"])
    def index():
        return "Hi!  I'm ORES.  :D"

    bp = scores.configure(config, bp, scorer_map)

    return bp
