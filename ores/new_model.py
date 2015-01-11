r"""
Initializes a new model file based on a set of configuration parameters.

Usage:
    new_model -h | --help
    new_model <class> <feature>... [--kwargs=<path>]
    
Options:
    -h --help        Prints this documentation
    <class>          Classpath for the MLScorerModel to initialize
    <feature>        Classpath for a Feature
    --kwargs=<path>  Path to additional configuration for the model
                     (expects yaml)
"""
import sys
import traceback

import docopt
import yaml

from .util import import_from_path


def main():
    args = docopt.docopt(__doc__)
    
    Model = import_from_path(args['<class>'])
    features = tuple(import_from_path(c) for c in args['<feature>'])
    if args['--kwargs'] is not None:
        kwargs = yaml.load(open(args['--kwargs']))
    else:
        kwargs = {}
    
    run(Model, features, kwargs)

def run(Model, features, kwargs):
    
    model = Model(features, **kwargs)
    
    model.dump(sys.stdout.buffer)


if __name__ == "__main__": main()

"""
./new_model revscores.scorers.LinearSVCModel \
    revscores.features.added_badwords_ratio \
    revscores.features.added_misspellings_ratio \
    revscores.features.day_of_week_in_utc \
    revscores.features.hour_of_day_in_utc \
    revscores.features.is_custom_comment \
    revscores.features.is_mainspace \
    revscores.features.is_section_comment \
    revscores.features.longest_repeated_char_added \
    revscores.features.longest_token_added \
    revscores.features.numeric_chars_added \
    revscores.features.prev_words \
    revscores.features.proportion_of_markup_added \
    revscores.features.proportion_of_numeric_added \
    revscores.features.proportion_of_symbolic_added \
    revscores.features.proportion_of_uppercase_added \
    revscores.features.seconds_since_last_page_edit \
    revscores.features.segments_added \
    revscores.features.segments_removed \
    revscores.features.user_age_in_seconds \
    revscores.features.user_is_anon \
    revscores.features.user_is_bot > \
models/reverts.halfak_mix.model
"""
