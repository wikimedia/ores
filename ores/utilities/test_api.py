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
    make_request(
        ores_url,
        ("/v3/scores/testwiki/2342342/revid/?" +
         "feature.revision.reversed_last_two_in_rev_id=50"),
        is_json=True,
        equal_to={'testwiki': {
            'models': {'revid': {'version': '0.0.0'}},
            'scores': {'2342342': {
                'revid': {'score': {'prediction': False,
                                    'probability': {'true': 0.50,
                                                    'false': 0.50}}}
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

    make_request(
        ores_url,
        "/v3/scores/testwiki/?revids=1205|2309&feature.delay=2&features",
        is_json=True,
        equal_to={"testwiki": {
            "models": {"revid": {"version": "0.0.0"}},
            "scores": {
                "1205": {"revid": {
                    "score": {
                        "prediction": False,
                        "probability": {"false": 0.50, "true": 0.50}},
                    "features": {
                        "feature.delay": 2,
                        "feature.revision.reversed_last_two_in_rev_id": 50}
                }},
                "2309": {"revid": {
                    "score": {
                        "prediction": True,
                        "probability": {"false": 0.09999999999999998, "true": 0.90}},
                    "features": {
                        "feature.delay": 2,
                        "feature.revision.reversed_last_two_in_rev_id": 90}}
                }}
        }})

    other_wiki_event = {
        "comment": "/* K-O */", "database": "enwiki",
        "meta": {
            "domain": "en.wikipedia.org", "dt": "2017-12-05T15:56:51+00:00",
            "id": "e87a7723-d9d4-11e7-9e8e-141877613bad",
            "request_id": "3464552a-85d0-404e-aa24-80b74473b15f",
            "schema_uri": "mediawiki/revision/create/2",
            "stream": "mediawiki.revision-create",
            "uri": "https://en.wikipedia.org/wiki/List_of_Ateneo_de_Manila_University_people",
            "partition": 0, "offset": 561544941
        },
        "page_id": 4716305, "page_is_redirect": False,
        "page_namespace": 0,
        "page_title": "List_of_Ateneo_de_Manila_University_people",
        "parsedcomment": "<a href=\"/wiki/List_of_Ateneo_de_Manila_University_" +
                         "people#K-O\" title=\"List of Ateneo de Manila " +
                         "University people\">→</a>‎<span dir=\"auto\">" +
                         "<span class=\"autocomment\">K-O</span></span>",
        "performer": {
            "user_edit_count": 13845,
            "user_groups": ["extendedconfirmed", "*", "user", "autoconfirmed"],
            "user_id": 24365224, "user_is_bot": False,
            "user_registration_dt": "2015-03-09T02:40:31Z",
            "user_text": "Khendygirl"
        },
        "rev_content_changed": True, "rev_content_format": "wikitext",
        "rev_content_model": "wikitext", "rev_id": 813852458,
        "rev_len": 60647, "rev_minor_edit": False,
        "rev_parent_id": 813852231,
        "rev_sha1": "0a6fggdfff46x0bptqle6pycuz0paht",
        "rev_timestamp": "2017-12-05T15:56:51Z"
    }
    make_request(
        ores_url,
        "/v3/precache",
        post_json=other_wiki_event,
        http_code=204)

    own_event = other_wiki_event
    own_event['database'] = "testwiki"
    make_request(
        ores_url,
        "/v3/precache",
        is_json=True,
        post_json=own_event,
        http_code=200,
        equal_to={
            "testwiki": {
                "models": {"revid": {"version": "0.0.0"}},
                "scores": {"813852458": {"revid": {"score": {
                                "prediction": True,
                                "probability": {
                                    "false": 0.15000000000000002,
                                    "true": 0.85
                                }}}}}
            }})

    revids_param = "|".join(str(v) for v in range(100, 200))
    make_request(
        ores_url,
        "/v3/scores/testwiki/?revids={0}".format(revids_param),
        is_json=True,
        http_code=400,
        equal_to={"error": {
            "code": "bad request",
            "message": "Too many values for 'revids' parameter.  Max of 50."
        }})


def make_request(ores_url, path, http_code=200, is_json=False,
                 equal_to=None, post_json=None):
    logger.debug("Requesting {0}".format(path))
    if post_json is None:
        response = requests.get(ores_url + path)
    else:
        response = requests.post(ores_url + path, json=post_json)
    assert response.status_code == http_code, \
           "Status code mismatch {0} for {1}: {2}".format(
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
