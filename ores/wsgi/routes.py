from flask import jsonify, render_template, request

from . import scorers
from .app import app


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

@app.route("/score/enwiki/reverted/<revids>")
def enwiki_reverted(revids):
    rev_ids = [int(rid) for rid in revids.split("|")]
    
    scores = {}
    for rev_id in rev_ids:
        score = next(scorers.enwiki_reverted.score([rev_id]))
        
        scores[rev_id] = {'reverted': score}
    
    return jsonify(scores)
