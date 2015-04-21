from mw.api import Session
from revscoring.extractors import APIExtractor
from revscoring.scorers import MLScorerModel, Scorer

enwiki = None
ptwiki = None

def configure(enwiki_reverted_file, ptwiki_reverted_file,
              enwiki_api,           ptwiki_api):
    global enwiki
    global ptwiki

    enwiki_model = MLScorerModel.load(enwiki_reverted_file)
    ptwiki_model = MLScorerModel.load(ptwiki_reverted_file)

    enwiki_extractor = APIExtractor(Session(enwiki_api), enwiki_model.language)
    ptwiki_extractor = APIExtractor(Session(ptwiki_api), ptwiki_model.language)

    enwiki = Scorer({'reverted': enwiki_model}, enwiki_extractor)

    ptwiki = Scorer({'reverted': ptwiki_model}, ptwiki_extractor)
