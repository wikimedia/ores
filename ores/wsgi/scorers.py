from mw.api import Session

from revscoring.extractors import APIExtractor
from revscoring.scorers import MLScorer, MLScorerModel

enwiki_reverted = None
ptwiki_reverted = None


def configure(enwiki_reverted_file, ptwiki_reverted_file,
              enwiki_api,           ptwiki_api):
    global enwiki_reverted
    global ptwiki_reverted

    enwiki_model = MLScorerModel.load(enwiki_reverted_file)
    ptwiki_model = MLScorerModel.load(ptwiki_reverted_file)

    enwiki_extractor = APIExtractor(Session(enwiki_api), enwiki_model.language)
    ptwiki_extractor = APIExtractor(Session(ptwiki_api), ptwiki_model.language)

    enwiki_reverted = MLScorer(enwiki_extractor, enwiki_model)

    ptwiki_reverted = MLScorer(ptwiki_extractor, ptwiki_model)
