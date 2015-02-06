r"""
Gathers a set of features and reverted status for a set of revisions and
prints a TSV to stdout of the format:

<feature_value1>\t<feature_value2>\t...\t<reverted>

Usage:
    features_reverted -h | --help
    features_reverted <model> --api=<url> [--rev_pages=<path>]
    
Options:
    -h --help             Prints out this documentation
    <model>               The ClassPath to a model for which to extract features
    --api=<url>           The url of the API to use to extract features
    --rev_pages=<path>    The location of a file containing rev_ids and
                          page_ids to extract. [default: <stdin>]
"""
import sys
import traceback
from importlib import import_module

import docopt
from mw import api
from mw.lib import reverts

from revscoring.extractors import APIExtractor
from revscoring.languages import english
from revscoring.scorers import MLScorerModel


def read_rev_ids(f):
    
    for line in f:
        parts = line.strip().split('\t')
        
        if len(parts) == 1:
            rev_id = parts
            yield int(rev_id[0]), None
        elif len(parts) == 2:
            rev_id, page_id = parts
            yield int(rev_id), int(page_id)

def import_from_path(path):
    parts = path.split(".")
    module_path = ".".join(parts[:-1])
    attribute_name = parts[-1]
    
    module = import_module(module_path)
    
    attribute = getattr(module, attribute_name)
    
    return attribute

def main():
    args = docopt.docopt(__doc__)
    
    if args['--rev_pages'] == "<stdin>":
        rev_pages = read_rev_ids(sys.stdin)
    else:
        rev_pages = read_rev_ids(open(args['--rev_pages']))
    
    model = import_from_path(args['<model>'])
    
    api_url = args['--api']
    
    run(rev_pages, api_url, model)

def run(rev_pages, api_url, model):
    
    session = api.Session(api_url)
    extractor = APIExtractor(session, language=model.language)
    
    for rev_id, page_id in rev_pages:
        sys.stderr.write(".");sys.stderr.flush()
        try:
            # Extract features
            values = extractor.extract(rev_id, model.features)
            
            # Detect reverted status
            revert = reverts.api.check(session, rev_id, page_id, radius=3)
            reverted = revert is not None
            
            # Print out row
            print('\t'.join(str(v) for v in values + [reverted]))
        
        except KeyboardInterrupt:
            sys.stderr.write("\n^C Caught.  Exiting...")
            break
        
        except:
            sys.stderr.write(traceback.format_exc())
            sys.stderr.write("\n")
    
    sys.stderr.write("\n")


if __name__ == "__main__": main()
