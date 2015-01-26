"""
Trains and tests a classifier.

Usage:
    train_test -h | --help
    train_test <model> [--feature-scores=<path>]

Options:
    -h --help                Prints this documentation
    <model>                  ClassPath to a model
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
    
    model = import_from_path(args['<model>'])
    
    if args['--feature-scores'] == "<stdin>":
        feature_scores_file = sys.stdin
    else:
        feature_scores_file = open(args['--feature-scores'], 'r')
    
    feature_scores = read_feature_scores(feature_scores_file, model.features)
    
    run(feature_scores, model)

def run(feature_scores, model):
    
    feature_scores = list(feature_scores)
    random.shuffle(feature_scores)

    test_set_size = int(0.6*len(feature_scores))
    test_set = feature_scores[:test_set_size]
    train_set = feature_scores[test_set_size:]
    
    model.train(train_set)
    
    stats = model.test(test_set)
    del stats['roc']
    sys.stderr.write(pprint.pformat(stats) + "\n")
    
    model.dump(sys.stdout.buffer)

"""
./train_test \
    models/reverts.halfak_mix.model \
    revscores.scorers.LinearSVCModel \
    --feature-scores=datasets/enwiki.features_reverted.tsv > \
models/train_test.log
"""
