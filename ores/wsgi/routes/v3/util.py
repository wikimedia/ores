import traceback
from collections import defaultdict

from revscoring.errors import ModelInfoLookupError

from .... import errors
from ... import responses, util


def format_v3_score_response(response):
    """
    {
        "<context_name>": {
            "scores": {
                "<rev_id>": {
                    "<model_name>": {
                        "score": <score>,
                        "features": <features>
                    },
                    "<model_name>": {
                        "score": <score>,
                        "features": <features>
                    }
                },
                "<rev_id>": {
                    "<model_name>": {
                        "score": <score>,
                        "features": <features>
                    },
                    "<model_name>": {
                        "score": <score>,
                        "features": <features>
                    }
                }
            },
            "models": {
                "<model_name>": <model_info>,
                "<model_name>": <model_info>
            }
        }
    }
    """
    context_doc = defaultdict(lambda: defaultdict(dict))
    if len(response.scores) > 0 or len(response.errors) > 0:
        for rev_id, rev_scores in response.scores.items():
            for model_name, score in rev_scores.items():
                context_doc['scores'][rev_id][model_name] = \
                    {'score': score}

        for rev_id, rev_errors in response.errors.items():
            for model_name, error in rev_errors.items():
                context_doc['scores'][rev_id][model_name] = \
                    util.format_error(error)

        for rev_id, rev_features in response.features.items():
            for model_name, features in rev_features.items():
                context_doc['scores'][rev_id][model_name]['features'] = \
                    features

    if len(response.model_info) > 0:
        context_doc['models'] = {
            model_name: info_doc
            for model_name, info_doc in response.model_info.items()}

    return util.jsonify({response.context.name: context_doc})


def build_v3_context_model_map(score_request, scoring_system):
    """
    {
        "<context>": {
            "models": {
                "<model_name>": <model_info>,
                "<model_name>": <model_info>
            }
        },
        "<context>": {
            "models": {
                "<model_name>": <model_info>,
                "<model_name>": <model_info>
            }
        }
    }
    """
    try:
        context_models_doc = {}
        for context_name, context in scoring_system.items():
            context_models_doc[context_name] = {'models': {}}
            for model_name in context:
                model_doc = context.format_model_info(
                    model_name, score_request.model_info or ['version'])
                context_models_doc[context_name]['models'][model_name] = model_doc
        return util.jsonify(context_models_doc)
    except Exception:
        return responses.unknown_error(traceback.format_exc())


def process_score_request(score_request, scoring_system):
    score_request.model_info = score_request.model_info or ['version']
    try:
        if len(score_request.rev_ids) > 50:
            return responses.bad_request(
                "Too many values for 'revids' parameter.  Max of 50.")
        else:
            score_response = scoring_system.score(score_request)
            return format_v3_score_response(score_response)
    except errors.ScoreProcessorOverloaded:
        scoring_system.metrics_collector.response_made(
                responses.SERVER_OVERLOADED, score_request)
        return responses.server_overloaded()
    except errors.MissingContext as e:
        scoring_system.metrics_collector.response_made(
                responses.NOT_FOUND, score_request)
        return responses.not_found("No scorers available for {0}"
                                   .format(e))
    except errors.MissingModels as e:
        scoring_system.metrics_collector.response_made(
                responses.NOT_FOUND, score_request)
        context_name, model_names = e.args
        return responses.not_found(
            "Models {0} not available for {1}"
            .format(tuple(model_names), context_name))
    except ModelInfoLookupError as e:
        return responses.model_info_lookup_error(e)
    except errors.TimeoutError:
        scoring_system.metrics_collector.response_made(
                responses.TIMEOUT, score_request)
        return responses.timeout_error()
    except errors.TooManyRequestsError:
        scoring_system.metrics_collector.response_made(
                responses.TOO_MANY_REQUESTS, score_request)
        return responses.too_many_requests_error()
    except Exception:
        return responses.unknown_error(traceback.format_exc())
