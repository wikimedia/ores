import time

from revscoring import ScorerModel
from revscoring.datasources.revision_oriented import revision
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


def process_delay():
    return 0.0
delay = Feature("delay", process_delay, returns=float)


class RevIdScorer(ScorerModel):
    """
    Implements a basic, testing scorer that predicts whether a revision ID's
    reversed last two digits are greater than 50.

    E.g. 974623 = 32 and 23754929 = 92
    """
    def __init__(self, version=None):
        super().__init__([reversed_last_two_in_rev_id, delay], version=version)

    def score(self, feature_values):
        last_two_in_rev_id, delay = feature_values
        time.sleep(delay)
        probability = last_two_in_rev_id / 100

        if probability > 0.5:
            prediction = True
        else:
            prediction = False

        return {
            'prediction': prediction,
            'probability': {
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

    def format_info(self, format="str"):
        if format == 'str':
            return str(self.info())
        elif format == 'json':
            return self.info()
        else:
            raise TypeError("Format {0} not supported".format(format))

    @classmethod
    def from_config(cls, config, name, section_key='scorer_models'):
        section = config[section_key][name]
        return cls(**{k: v for k, v in section.items() if k != "class"})
