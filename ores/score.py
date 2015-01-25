r"""
Uses a model to score a revision.

Usage:
    score -h | --help
    score --api=<url> [--features] <model> <revid>...
    
Options:
    -h --help         Prints out this documentation
    <model>           The path to a trained model file
    <revid>           Revisions to make predictions for
    --show-features   Prints the feature values along with the score
    --api=<url>       The url of the API to use to extract features
"""
import sys
import traceback
from importlib import import_module
from pprint import pformat

import docopt
from mw import api
from mw.lib import reverts

from revscores.extractors import APIExtractor
from revscores.languages import english
from revscores.scorers import MLScorerModel


def import_from_path(path):
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
    show_features = args['--show-features']
    
    run(model, rev_ids, api_url, show_features)

def run(model, rev_ids, api_url, show_features):
    
    session = api.Session(api_url)
    extractor = APIExtractor(session, language=english) # This is a hack.  Need to fix langauges
    
    feature_values = [extractor.extract(rev_id, model.features)
                      for rev_id in rev_ids]
    
    scores = model.score(feature_values, probabilities=True)
    
    for rev_id, values, score in zip(rev_ids, feature_values, scores):
        if show_features:
            print(pformat({str(f): v
                           for f, v in zip(model.features, values)}))
        print("{0}: {1}".format(rev_id, pformat(score)))


if __name__ == "__main__": main()
