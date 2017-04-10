from nose.tools import eq_
from revscoring.extractors import OfflineExtractor

from ... import errors
from ...score_caches import LRU
from ...score_request import ScoreRequest
from ...scorer_models import RevIdScorer
from ...scoring_context import ScoringContext
from ..process_pool import ProcessPool
from .util import fakewiki, test_scoring_system, wait_time


def test_score():
    scoring_system = ProcessPool({'fakewiki': fakewiki}, timeout=0.10,
                                 workers=8)

    test_scoring_system(scoring_system)


def test_rev_id_scorer():
    revid = RevIdScorer(version='0.0.1')
    fakewiki = ScoringContext(
        'fakewiki', {'revid': revid}, OfflineExtractor())
    scoring_system = ProcessPool({'fakewiki': fakewiki}, timeout=0.10,
                                 workers=8,
                                 score_cache=LRU(size=10))
    response = scoring_system.score(
        ScoreRequest("fakewiki", [1, 19], ["revid"], model_info=['']))
    print(response.scores, response.errors)
    eq_(response.model_info['revid']['version'], '0.0.1')
    eq_(response.scores[1]['revid']['prediction'], False)
    eq_(response.scores[19]['revid']['prediction'], True)


def test_timeout():
    scoring_system = ProcessPool({'fakewiki': fakewiki}, timeout=0.05)

    response = scoring_system.score(
        ScoreRequest("fakewiki", [1], ['fake'],
                     injection_caches={1: {wait_time: 0.10}}))
    assert 1 in response.errors, str(response.errors)
    assert isinstance(response.errors[1]['fake'], errors.TimeoutError), \
           type(response.errors[1]['fake'])
