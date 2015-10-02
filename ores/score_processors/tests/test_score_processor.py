from ..score_processor import ScoreProcessor, SimpleScoreProcessor


def test_score_process():
    ssp = SimpleScoreProcessor({})
    assert isinstance(ssp, ScoreProcessor)
