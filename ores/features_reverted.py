r"""
Gathers a set of features and reverted status for a set of revisions and
prints a TSV to stdout of the format:

<feature_value1>\t<feature_value2>\t...\t<reverted>

Usage:
    features_reverted -h | --help
    features_reverted <features> --api=<url> [--language=<module>]
                      [--rev-pages=<path>]

Options:
    -h --help             Prints out this documentation
    <features>            Classpath to a list of features to extract
    --api=<url>           The url of the API to use to extract features
    --language=<module>   The Classpath of a language module (required if a
                          feature depends on 'language')
    --rev-pages=<path>    The location of a file containing rev_ids and
                          page_ids to extract. [default: <stdin>]
"""
import sys
import traceback
from importlib import import_module

import docopt
from mw import api
from mw.lib import reverts

from revscoring.extractors import APIExtractor


def read_rev_pages(f):

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

    if args['--rev-pages'] == "<stdin>":
        rev_pages = read_rev_pages(sys.stdin)
    else:
        rev_pages = read_rev_pages(open(args['--rev-pages']))

    features = import_from_path(args['<features>'])
    if args['--language'] is not None:
        language = import_from_path(args['--language'])
    else:
        language = None

    api_url = args['--api']

    run(rev_pages, features, language, api_url)


def run(rev_pages, features, language, api_url):

    session = api.Session(api_url)
    extractor = APIExtractor(session, language=language)

    for rev_id, page_id in rev_pages:
        sys.stderr.write(".")
        sys.stderr.flush()
        try:
            # Extract features

            values = extractor.extract(rev_id, features)

            # Detect reverted status
            revert = reverts.api.check(session, rev_id, page_id, radius=3)
            reverted = revert is not None

            # Print out row
            print('\t'.join(str(v) for v in (list(values) + [reverted])))

        except KeyboardInterrupt:
            sys.stderr.write("\n^C Caught.  Exiting...")
            break

        except:
            sys.stderr.write(traceback.format_exc())
            sys.stderr.write("\n")

    sys.stderr.write("\n")


if __name__ == "__main__":
    main()

"""
./features_reverted \
    ores.features.enwiki.damaging \
    --language=revscoring.languages.english \
    --api=https://en.wikipedia.org/w/api.php \
    --rev-pages=datasets/enwiki.rev_pages.5k.tsv > \
datasets/enwiki.features_reverted.5k.tsv
"""
