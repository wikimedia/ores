r"""
Gathers the reverted status for a set of revisions and
prints a TSV to stdout of the format:

<rev_id>\t<reverted>

Usage:
    label_reverted -h | --help
    label_reverted --host=<url> [--revert-radius=<revs>]
                               [--revert-window=<secs>]
                               [--rev-pages=<path>]
                               [--rev-reverteds=<path>]

Options:
    -h --help               Prints out this documentation
    --host=<url>            The host URL of the MediaWiki install where an API
                            can be found.
    --revert-radius=<revs>  The maximum amount of revisions that a reverting
                            edit can revert [default: 15]
    --revert-window=<secs>  The maximum amount of time to wait for a revision to
                            be reverted [default: 172800]
    --rev-pages=<path>      The location of a file containing rev_ids and
                            page_ids to extract. [default: <stdin>]
    --rev-reverteds=<path>  The location to write output to. [default: <stdout>]
"""
import sys
import traceback

import docopt
import mwapi

import mwreverts.api


def main(argv=None):
    args = docopt.docopt(__doc__, argv=argv)

    revert_radius = int(args['--revert-radius'])
    revert_window = int(args['--revert-window'])

    if args['--rev-pages'] == "<stdin>":
        rev_pages = read_rev_pages(sys.stdin)
    else:
        rev_pages = read_rev_pages(open(args['--rev-pages']))

    if args['--rev-reverteds'] == "<stdout>":
        rev_reverteds = sys.stdout
    else:
        rev_reverteds = open(args['--rev-reverteds'], "w")

    host = args['--host']
    session = mwapi.Session(host, user_agent="ORES revert labeling utility")

    run(rev_pages, rev_reverteds, session, revert_radius, revert_window)


def read_rev_pages(f):
    first_line_parts = f.readline().split("\t")
    if first_line_parts[0] != "rev_id":
        if len(first_line_parts) == 1:
            rev_id = first_line_parts[0]
            yield int(rev_id), None
        elif len(first_line_parts) == 2:
            rev_id, page_id = first_line_parts
            yield int(rev_id), int(page_id)

    for line in f:
        parts = line.strip().split('\t')

        if len(parts) == 1:
            rev_id = parts[0]
            yield int(rev_id), None
        elif len(parts) == 2:
            rev_id, page_id = parts
            yield int(rev_id), int(page_id)


def run(rev_pages, rev_reverteds, session, revert_radius, revert_window):
    for rev_id, page_id in rev_pages:
        try:
            # Detect reverted status
            _, reverted, _ = mwreverts.api.check(session, rev_id,
                                                 page_id=page_id,
                                                 radius=revert_radius,
                                                 window=revert_window)

            reverted = reverted is not None

            if reverted:
                sys.stderr.write("r")
                sys.stderr.flush()
            else:
                sys.stderr.write(".")
                sys.stderr.flush()

            # Print out row
            rev_reverteds.write('\t'.join(str(v) for v in [rev_id, reverted]))
            rev_reverteds.write("\n")

        except KeyboardInterrupt:
            sys.stderr.write("\n^C Caught.  Exiting...")
            break

        except:
            sys.stderr.write(traceback.format_exc())
            sys.stderr.write("\n")

    sys.stderr.write("\n")


if __name__ == "__main__":
    main()
