from nose.tools import eq_
from revscoring.extractors import OfflineExtractor

from ..process_pool import ProcessPool
from ...metrics_collectors import Logger
from .util import fakewiki, wait_time, test_scoring_system
from ...scorer_models import RevIdScorer
from ...scoring_context import ScoringContext
from ...score_caches import LRU


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
    score_doc = scoring_system.score("fakewiki", ["revid"], [1, 19],
                                     include_model_info="all")
    eq_(score_doc['models']['revid']['version'], '0.0.1')
    eq_(score_doc['scores'][1]['revid']['score']['prediction'], False)
    eq_(score_doc['scores'][19]['revid']['score']['prediction'], True)


def test_timeout():
    scoring_system = ProcessPool({'fakewiki': fakewiki}, timeout=0.05)

    score_doc = scoring_system.score(
        "fakewiki", ["fake"], [1], injection_caches={1: {wait_time: 0.10}})
    assert 'error' in score_doc['scores'][1], str(score_doc['scores'])
    assert 'Timed out after' in score_doc['scores'][1]['error']['message'], \
           score_doc['scores'][1]['error']['message']
