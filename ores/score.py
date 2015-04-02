r"""
Uses a model to score a revision.

Usage:
    score -h | --help
    score <model> <revid>... --api=<url> [--print-features]

Options:
    -h --help            Prints out this documentation
    <model>              The path to a trained model file
    <revid>              Revisions to make predictions for
    --print-features     Prints the feature values along with the score
    --api=<url>          The url of the API to use to extract features
"""
import sys
import traceback
from importlib import import_module
from pprint import pformat

import docopt
from mw import api

from revscoring.extractors import APIExtractor
from revscoring.scorers import MLScorerModel


def import_from_path(path):
    """
    Return attributes from a given path.

    @param path: path to be imported
    @type path: basestring
    @return: attributes of the module
    """
    parts = path.split(".")
    module_path = ".".join(parts[:-1])
    attribute_name = parts[-1]

    module = import_module(module_path)

    attribute = getattr(module, attribute_name)

    return attribute


def main():
    args = docopt.docopt(__doc__)

    model = MLScorerModel.load(open(args['<model>'], 'rb'))

    rev_ids = [int(rev_id) for rev_id in args['<revid>']]

    api_url = args['--api']
    print_features = args['--print-features']

    run(model, rev_ids, api_url, print_features)


def run(model, rev_ids, api_url, print_features):
    """
    Main function to be ran by L{main}.

    @param model: the model to score revisions
    @param rev_ids: revision ids to be analyzed
    @type rev_ids: list of integers
    @param api_url: url of Wiki's API like: https://en.wikipedia.org/w/api.php
    @type api_url: basestring
    @param print_features: shows features or not
    @type print_features: bool
    """
    session = api.Session(api_url, user_agent="Revscores test scoring script")
    extractor = APIExtractor(session, language=model.language)

    feature_values = [extractor.extract(rev_id, model.features)
                      for rev_id in rev_ids]

    scores = model.score(feature_values)

    for rev_id, values, score in zip(rev_ids, feature_values, scores):
        if print_features:
            print(pformat({str(f): v
                           for f, v in zip(model.features, values)}))
        print("{0}: {1}".format(rev_id, pformat(score)))


if __name__ == "__main__":
    main()
