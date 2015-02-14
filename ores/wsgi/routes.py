import traceback
from collections import defaultdict

from flask import jsonify, render_template, request

from . import errors, scorers
from .app import app
from .util import ParamError, read_bar_split_param


'''
@app.route("/")
def index():
    return render_template("index.html")
    
@app.route("/scores/")
def scores():
    wiki_scorers = [(wiki, scorer) for wiki in scorers
                                   for scorer in scorers[wiki]]
    
    wiki_scorers.sort()
    
    return render_template("scores.html", wiki_scorers)
'''



# /enwiki?models=reverted
@app.route("/<wiki>/")
def enwiki_reverted(wiki):
    
    scorer_models = {
        ('enwiki', 'reverted'): scorers.enwiki_reverted,
        ('ptwiki', 'reverted'): scorers.ptwiki_reverted
    }
    
    try:
        models = read_bar_split_param(request, "models", str) # Ignored for now
        rev_ids = read_bar_split_param(request, "revids", int)
    except ParamError as e:
        return e.error
        
    
    for model in models:
        if (wiki, model) not in scorer_models:
            return errors.bad_request("Model '{0}' not available for '{1}'" \
                                      .format(model, wiki))
    
    scores = defaultdict(lambda: {})
    for rev_id in rev_ids:
        for model in models:
            scorer = scorer_models[(wiki, model)]
            try:
                score = next(scorer.score([rev_id]))
            except Exception as e:
                score = {"error": {'type': str(type(e)), 'message': str(e)}}
            
            scores[rev_id].update({model: score})
    
    return jsonify(scores)
