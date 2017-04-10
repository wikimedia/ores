import json
import logging

from ..score_request import ScoreRequest

logger = logging.getLogger(__name__)


class CacheParsingError(Exception):
    pass


class ParamError(Exception):
    pass


def read_param(request, param, default=None, type=str):
    try:
        value = request.args.get(param, request.form.get(param))
        if value is None:
            return default
        else:
            return type(value)
    except (ValueError, TypeError) as e:
        raise ParamError("Could not interpret {0}. {1}".format(param, str(e)))


def read_bar_split_param(request, param, default=None, type=str):
    values = read_param(request, param, default=default)
    if values is None:
        return []

    try:
        return [type(value) for value in values.split("|")]
    except (ValueError, TypeError) as e:
        raise ParamError("Could not interpret {0}. {1}"
                         .format(param, str(e)))


def format_error(error):
    error_type = error.__class__.__name__
    message = str(error)

    return {'error': {'type': error_type, 'message': message}}


def build_score_request(scoring_system, request, context_name=None, rev_id=None,
                        model_name=None):
    """
    Build an :class:`ores.ScoreRequest` from information contained in a
    request.

    :Parameters:
        scoring_system : :class:`ores.ScoringSystem`
            A scoring system to build request with
        request : :class:`flask.Request`
            A web request to extract information from
        context_name : `str`
            The name of the context to perform scoring
        rev_id : int
            The revision ID to score.  Note that multiple IDs can be provided
            in `request.args`
        model_name = `str`
            The name of the model to score.  Note that multiple models can be
            provided in `request.args`
    """
    rev_ids = parse_rev_ids(request, rev_id)
    model_names = parse_model_names(request, model_name)
    precache = 'precache' in request.args
    include_features = 'features' in request.args
    injection_caches = parse_injection(request, rev_id)
    model_info = parse_model_info(request)

    if context_name and context_name in scoring_system and not model_names:
        model_names = scoring_system[context_name].keys()

    return ScoreRequest(context_name, rev_ids, model_names,
                        precache=precache,
                        include_features=include_features,
                        injection_caches=injection_caches,
                        model_info=model_info)


def parse_rev_ids(request, rev_id):
    if rev_id is not None:
        return [int(rev_id)]
    else:
        return read_bar_split_param(request, "revids", type=int)


def parse_model_names(request, model_name):
    if model_name is not None:
        return [model_name]
    else:
        return read_bar_split_param(request, "models", type=str)


def parse_injection(request, rev_id):
    """Parse values for features / datasources of interest."""
    cache = {}

    if 'inject' in request.values:
        try:
            cache = json.loads(request.values['inject'])
        except json.JSONDecodeError as e:
            raise CacheParsingError(e)

    if rev_id is not None:
        rev_cache = cache

        try:
            for k, v in request.values.items():
                if k.startswith(("feature.", "datasource.")):
                    rev_cache[k] = json.loads(v)
        except json.JSONDecodeError as e:
            raise CacheParsingError(e)

        if len(rev_cache) > 0:
            cache = {rev_id: rev_cache}
    else:
        cache = {int(rev_id): c for rev_id, c in cache.items()}

    return cache or None


def parse_model_info(request):
    return read_bar_split_param(request, "model_info", type=str)


def build_score_request_from_event(precache_map, event):
    context_name = event['database']
    rev_id = event['rev_id']

    # Check to see if we have the context available in our precache_map
    if context_name not in precache_map:
        return None

    # Start building the response document
    event_set = build_event_set(event)

    model_names = {precache_map[context_name][e] for e in event_set
                   if e in precache_map[context_name]}

    if len(model_names) == 0:
        return None

    return ScoreRequest(context_name, model_names, rev_id)


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
                logger.warning("{0} events are not available"
                               .format(set(events) - AVAILABLE_EVENTS))
            for event in precached_config['on']:
                precache_map[context][event] = model
                logger.debug("Setting up precaching for {0} in {1} on {2}"
                             .format(model, context, event))

    return precache_map
