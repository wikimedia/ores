import time

from revscoring import Datasource, Feature, Model
from revscoring.datasources.revision_oriented import revision
from revscoring.scoring import ModelInfo
from revscoring.scoring.statistics import Classification


def process_last_two_in_rev_id(rev_id):
    """
    Return the last revision identifier. git repo_id.

    Args:
        rev_id: (str): write your description
    """
    last_two = str(rev_id)[-2:]
    if len(last_two) == 1:
        return "0" + last_two
    else:
        return last_two


last_two_in_rev_id = Datasource(
    "revision.last_two_in_rev_id",
    process_last_two_in_rev_id,
    depends_on=[revision.id]
)


def process_reversed_last_two_in_rev_id(last_two):
    """
    Process the last revision number.

    Args:
        last_two: (todo): write your description
    """
    return int("".join(reversed(last_two)))


reversed_last_two_in_rev_id = Feature(
    "revision.reversed_last_two_in_rev_id",
    process_reversed_last_two_in_rev_id,
    returns=int,
    depends_on=[last_two_in_rev_id]
)


def process_delay():
    """
    Process the number of seconds.

    Args:
    """
    return 0.0


delay = Feature("delay", process_delay, returns=float)


class RevIdScorer(Model):
    """
    Implements a basic, testing scorer that predicts whether a revision ID's
    reversed last two digits are greater than 50.

    E.g. 974623 = 32 and 23754929 = 92
    """
    def __init__(self, version=None):
        """
        Initialize the statistics.

        Args:
            self: (todo): write your description
            version: (todo): write your description
        """
        super().__init__([reversed_last_two_in_rev_id, delay], version=version)
        self.info = ModelInfo()
        self.info['version'] = version
        self.info['type'] = "RevIDScorer"
        self.info['behavior'] = "Returns the last two digits in a rev_id " + \
                                "as a score."
        self.info['statistics'] = self.calculate_statistics()

    def score(self, feature_values):
        """
        Compute the score.

        Args:
            self: (todo): write your description
            feature_values: (bool): write your description
        """
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

    def calculate_statistics(self):
        "Jam some data through to generate statistics"
        rev_ids = range(0, 100, 1)
        feature_values = zip(rev_ids, [0] * 100)
        scores = [self.score(f) for f in feature_values]
        labels = [s['prediction'] for s in scores]
        statistics = Classification(labels, threshold_ndigits=1, decision_key='probability')
        score_labels = list(zip(scores, labels))
        statistics.fit(score_labels)
        return statistics

    @classmethod
    def from_config(cls, config, name, section_key='scorer_models'):
        """
        Initialize a configuration object from a configuration file.

        Args:
            cls: (todo): write your description
            config: (todo): write your description
            name: (str): write your description
            section_key: (str): write your description
        """
        section = config[section_key][name]
        return cls(**{k: v for k, v in section.items() if k != "class"})
