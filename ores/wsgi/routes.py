import traceback
from collections import defaultdict

from flask import jsonify, render_template, request

from . import errors, scorers
from .app import app
from .util import ParamError, read_bar_split_param


def scorer_map():
    return {
        ('enwiki', 'reverted'): scorers.enwiki_reverted,
        ('ptwiki', 'reverted'): scorers.ptwiki_reverted
    }
	

# /
@app.route("/")
def index():
    return "Welcome to the index page of the ores flask app."
    
# /scores/
@app.route("/scores/")
def scores():
    wiki_models = [wiki_model for wiki_model in scorer_map()]
    
    wiki_models.sort()
    
    return "These are the scorers I have: {0}.".format(wiki_models)



# /scores/enwiki?models=reverted&revids=456789|4567890
@app.route("/scores/<wiki>")
def score_revisions(wiki):
    
    scorer_models = scorer_map()
    
    try:
        model_names = read_bar_split_param(request, "models", str)
        rev_ids = read_bar_split_param(request, "revids", int)
    except ParamError as e:
        return e.error
        
    
    for model_name in model_names:
        if (wiki, model_name) not in scorer_models:
            return errors.bad_request("Model '{0}' not available for '{1}'" \
                                      .format(model_name, wiki))
    
    scores = defaultdict(lambda: {})
    for model_name in model_names:
        scorer = scorer_models[(wiki, model_name)]
        for rev_id in rev_ids:
            
            try:
                score = next(scorer.score([rev_id]))
            except Exception as e:
                score = {"error": {'type': str(type(e)), 'message': str(e)}}
            
            scores[rev_id][model_name] = score
        
        
    
    return jsonify(scores)
