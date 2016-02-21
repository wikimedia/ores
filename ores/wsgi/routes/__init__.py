
from . import scores
from . import ui


def configure(config, bp, score_processor):

    @bp.route("/", methods=["GET"])
    def index():
        content = "<head><meta http-equiv=\"refresh\" content=\"0;" \
            "url=https://meta.wikimedia.org/wiki/Objective_Revision" \
            "_Evaluation_Service\" /></head>"
        return content

    bp = scores.configure(config, bp, score_processor)
    bp = ui.configure(config, bp)

    return bp
