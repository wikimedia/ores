from ..process_pool import ProcessPool
from .util import fakewiki, wait_time, test_scoring_system


def test_score():
    scoring_system = ProcessPool({'fakewiki': fakewiki}, timeout=0.10)

    test_scoring_system(scoring_system)


def test_timeout():
    scoring_system = ProcessPool({'fakewiki': fakewiki}, timeout=0.05)

    score_doc = scoring_system.score(
        "fakewiki", ["fake"], [1], injection_caches={1: {wait_time: 0.10}})
    assert 'error' in score_doc['scores'][1], str(score_doc['scores'])
    assert 'Timed out after' in score_doc['scores'][1]['error']['message'], \
           score_doc['scores'][1]['error']['message']
