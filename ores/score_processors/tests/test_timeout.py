import time
from collections import namedtuple

from nose.tools import eq_, raises
from revscoring.dependencies import Context
from revscoring.features import Feature

from ..timeout import Timeout, TimeoutError

wait_time = Feature("wait_time", returns=float)

FakeSM = namedtuple("ScorerModel", ['score', 'features'])
waiter = FakeSM(
    lambda fvs: time.sleep(fvs[0]) or {'score': True},
    [wait_time]
)


class FakeExtractor(Context):
    pass


extractor = FakeExtractor()

FakeCache = namedtuple("ScoreCache", ['store'])
score_cache = FakeCache(lambda *args, **kwargs: None)


def test_score():
    score_processor = Timeout(timeout=0.10)

    result = score_processor.process(waiter, extractor, cache={wait_time: 0.05})
    eq_(result.get(), {'score': True})


@raises(TimeoutError)
def test_timeout():
    score_processor = Timeout(timeout=0.05)

    result = score_processor.process(waiter, extractor, cache={wait_time: 0.50})
    eq_(result.get(), {'score': True})
