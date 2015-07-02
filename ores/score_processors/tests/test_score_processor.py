from nose.tools import eq_, raises

from ..score_processor import SimpleScoreResult


def test_simple_score_result():
    ssr = SimpleScoreResult(score=5)
    eq_(ssr.get(), 5)


@raises(RuntimeError)
def test_simple_score_error():
    ssr = SimpleScoreResult(error=RuntimeError())
    eq_(ssr.get(), 5)
