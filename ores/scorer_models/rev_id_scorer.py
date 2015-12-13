from revscoring import ScorerModel
from revscoring.datasources import revision
from revscoring.features import Feature


def process_reversed_last_two_in_rev_id(rev_id):
    last_two = str(rev_id)[-2:]
    if len(last_two) == 1:
        return int(last_two + "0")
    else:
        return int("".join(reversed(last_two)))

reversed_last_two_in_rev_id = Feature(
    "revision.reversed_last_two_in_rev_id",
    process_reversed_last_two_in_rev_id,
    returns=int,
    depends_on=[revision.id]
)


class RevIdScorer(ScorerModel):
    """
    Implements a basic, testing scorer that predicts whether a revision ID's
    reversed last two digits are greater than 50.

    E.g. 974623 = 32 and 23754929 = 92
    """
    def __init__(self, version=None):
        super().__init__([reversed_last_two_in_rev_id], version=version)

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
