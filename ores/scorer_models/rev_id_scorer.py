from revscoring import ScorerModel
from revscoring.datasources import revision
from revscoring.features import Feature


def process_last_two_in_rev_id(rev_id):
    return int(str(rev_id)[-2:])

last_two_in_rev_id = Feature(
    "revision.last_two_in_rev_id",
    process_last_two_in_rev_id,
    returns=int,
    depends_on=[revision.id]
)


class RevIdScorer(ScorerModel):
    """
    Implements a basic, testing scorer that predicts whether a revision ID's
    last two digits are greater than 50.
    """
    def __init__(self, version=None):
        super().__init__([last_two_in_rev_id], version=version)

    def score(self, feature_values):
        probability = feature_values[0] / 100

        if probability > 0.5:
            prediction = True
        else:
            prediction = False

        return {
            'prediction': prediction,
            'probabilities': {
                True: probability,
                False: 1 - probability
            }
        }

    def info(self):
        return {
            'type': "RevIDScorer",
            'version': self.version,
            'behavior': "Returns the last two digits in a rev_id as a score."
        }

    @classmethod
    def from_config(cls, config, name, section_key='scorer_models'):
        section = config[section_key][name]
        return cls(**{k: v for k, v in section.items() if k != "class"})
