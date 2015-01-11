"""
Trains and tests a classifier.

Usage:
    train_test -h | --help
    train_test <model> <class> [--feature-scores=<path>]

Options:
    -h --help                Prints this documentation
    <mode>                   Path to a model file
    <class>                  Class path of the model
    --feature-scores=<path>  Path to a file containing features and scores
                             [default: <stdin>]
"""
import pprint
import random
import sys

import docopt

from .util import import_from_path


def read_feature_scores(f, features):
    for line in f:
        parts = line.strip().split("\t")
        values = parts[:-1]
        score = parts[-1]
        
        feature_values = []
        for feature, value in zip(features, values):
            
            if feature.returns == bool:
                feature_values.append(value == "True")
            else:
                feature_values.append(feature.returns(value))
            
        
        yield feature_values, score == "True"

def main():
    args = docopt.docopt(__doc__)
    
    Model = import_from_path(args['<class>'])
    model = Model.load(open(args['<model>'], 'rb'))
    
    if args['--feature-scores'] == "<stdin>":
        feature_scores_file = sys.stdin
    else:
        feature_scores_file = open(args['--feature-scores'], 'rb')
    
    feature_scores = read_feature_scores(feature_scores_file, model.features)
    
    run(feature_scores, model)

def run(feature_scores, model):
    
    feature_scores = list(feature_scores)
    random.shuffle(feature_scores)
    
    test_set = feature_scores[:1000]
    train_set = feature_scores[1000:]
    
    model.train(train_set)
    
    sys.stderr.write(pprint.pformat(model.test(test_set)) + "\n")
    
    model.dump(sys.stdout.buffer)
