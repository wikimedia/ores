"""
Runs a basic test against an ORES api assuming that it supports the standard
configuration "/v2/testwiki/revid/..."

:Usage:
    test_api -h | --help
    test_api <ores-url> [--debug]

:Options:
    -h --help        Prints this documentation
    <ores-url>       URL of base ORES webserver
    --debug          Print debugging information
"""
import json
import logging

import docopt
import requests

logger = logging.getLogger(__name__)


def main(argv=None):
    args = docopt.docopt(__doc__, argv=argv)

    logging.basicConfig(
        level=logging.INFO if not args['--debug'] else logging.DEBUG,
        format='%(asctime)s %(levelname)s:%(name)s -- %(message)s'
    )
    # Requests is loud.  Be quiet requests.
    requests.packages.urllib3.disable_warnings()

    ores_url = args['<ores-url>']
    make_request(ores_url, "/")
    make_request(ores_url, "/ui/")
    make_request(ores_url, "/scores/", is_json=True)
    make_request(ores_url, "/v1/spec/", is_json=True)
    make_request(ores_url, "/v2/spec/", is_json=True)
    make_request(ores_url, "/v3/spec/", is_json=True)
    make_request(
        ores_url, "/v1/scores/testwiki/revid/2342342/", is_json=True,
        equal_to={"2342342": {"prediction": False,
                              "probability": {"false": 0.76, "true": 0.24}}})
    make_request(
        ores_url, "/v2/scores/testwiki/revid/2342342/", is_json=True,
        equal_to={"scores": {"testwiki": {"revid": {"scores": {
            "2342342": {
                "prediction": False,
                "probability": {"false": 0.76, "true": 0.24}
            }
        }, "version": "0.0.0"}}}})
    make_request(
        ores_url, "/v3/scores/testwiki/2342342/revid/", is_json=True,
        equal_to={"testwiki": {
            "models": {"revid": {"version": "0.0.0"}},
            "scores": {"2342342": {
                "revid": {"score": {"prediction": False,
                                    "probability": {"false": 0.76,
                                                    "true": 0.24}}}
            }}}})
    response = requests.get(ores_url + "/404/")
    assert response.status_code == 404, "/404/ didn't get a 404!"

    make_request(
        ores_url,
        "/v3/scores/testwiki/2342342/revid/?features&feature.delay=16",
        is_json=True,
        equal_to={"testwiki": {
            "models": {"revid": {"version": "0.0.0"}},
            "scores": {"2342342": {
                "revid": {"error": {'message': 'Timed out after 15 seconds.',
                                    'type': 'TimeoutError'}}
            }}}})


def make_request(ores_url, path, is_json=False, equal_to=None):
    logger.debug("Requesting {0}".format(path))
    response = requests.get(ores_url + path)
    assert response.status_code == 200, \
           "Non-OK status code {0} for {1}: {2}".format(
               response.status_code, path, response.content)

    content = response.text

    if is_json:
        try:
            content = json.loads(content)
        except ValueError:
            raise RuntimeError("Could not parse the following as JSON: '{0}"
                               .format(content[0:100]))

    if equal_to:
        assert content == equal_to, "{0} != {1}".format(content, equal_to)

    return response
