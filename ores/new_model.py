r"""
Initializes a new model file based on a set of configuration parameters.

Usage:
    new_model -h | --help
    new_model <model> [--kwargs=<path>]
    
Options:
    -h --help        Prints this documentation
    <module>         Classpath for the MLScorerModel to initialize
"""
import sys
import traceback

import docopt
import yaml

from .util import import_from_path


def main():
    args = docopt.docopt(__doc__)
    
    model = import_from_path(args['<module>'])
    
    run(model)

def run(model):
    
    model.dump(sys.stdout.buffer)


if __name__ == "__main__": main()
