import json
import logging
import traceback
from urllib.parse import unquote

from flask import request
from flask.ext.jsonpify import jsonify

from ... import preprocessors, responses
from .... import errors

logger = logging.getLogger(__name__)


def configure(config, bp, scoring_system):

    precache_map = build_precache_map(config)

    @bp.route("/v2/precache/", methods=["GET"])
    @preprocessors.nocache
    @preprocessors.minifiable
    def precache_v2():
        try:
            event = json.loads(unquote(request.args.get('event', '{}')).strip())
        except json.JSONDecodeError:
            return responses.bad_request("Can not parse event argument as JSON blob")
        try:
            context = event['database']
        except KeyError:
            return responses.bad_request("'database' missing from event data")
        try:
            rev_id = event['rev_id']
        except KeyError:
            return responses.bad_request("'rev_id' midding from event data")

        # Check to see if we have the context available in our score_processor
        if context not in scoring_system:
            return responses.no_content()

        # Start building the response document
        response_doc = {context: {}}

        event_set = build_event_set(event)

        models = {precache_map[context][e] for e in event_set
                  if e in precache_map[context]}

        if len(models) == 0:
            return responses.no_content()

        for model_name in models:
            response_doc[context][model_name] = \
                {'version': scoring_system[context].model_version(model_name)}

        try:
            scores_doc = scoring_system.score(
                context, models, [rev_id], precache=True,
                include_model_info=None)
        except errors.ScoreProcessorOverloaded:
            return responses.server_overloaded()
        except Exception:
            return responses.unknown_error(traceback.format_exc())

        for model_name in models:
            response_doc[context][model_name]['scores'] = {}
            if 'error' in scores_doc['scores'][rev_id]:
                response_doc[context][model_name]['scores'][rev_id] = \
                    scores_doc['scores'][rev_id]
            else:
                response_doc[context][model_name]['scores'][rev_id] = \
                    scores_doc['scores'][rev_id][model_name]['score']

        return jsonify({'scores': response_doc})

    return bp


# TODO: This strategy for building up events is not sustainable.
def build_event_set(event):
    """
    Turn an EventStream event into a set of event types that ORES
    uses internally.
    """
    event_set = set()
    if event['meta']['topic'] == "mediawiki.revision-create":
        event_set.add('edit')

        user_groups = event.get('performer', {}).get('user_groups', [])
        if 'bot' in user_groups:
            event_set.add('bot_edit')
        else:
            event_set.add('nonbot_edit')

        if event['rev_parent_id'] == 0:
            event_set.add('page_creation')
            if 'bot' in user_groups:
                event_set.add('bot_page_creation')
            else:
                event_set.add('nonbot_page_creation')

    return event_set


AVAILABLE_EVENTS = {'edit', 'bot_edit', 'nonbot_edit', 'page_creation',
                    'bot_page_creation', 'nonbot_page_creation'}


def build_precache_map(config):
    """
    Build a mapping of contexts and models from the configuration
    """
    precache_map = {}
    ss_name = config['ores']['scoring_system']
    for context in config['scoring_systems'][ss_name]['scoring_contexts']:
        precache_map[context] = {}
        for model in config['scoring_contexts'][context].get('precache', []):
            precached_config = \
                config['scoring_contexts'][context]['precache'][model]

            events = precached_config['on']
            if len(set(events) - AVAILABLE_EVENTS) > 0:
                logger.error("{0} events are not available"
                             .format(set(events) - AVAILABLE_EVENTS))
            for event in precached_config['on']:
                precache_map[context][event] = model
                logger.debug("Setting up precaching for {0} in {1} on {2}"
                             .format(model, context, event))

    return precache_map
