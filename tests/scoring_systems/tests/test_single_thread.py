from ores import errors
from ores.score_request import ScoreRequest
from ores.scoring_systems.single_thread import SingleThread

from .util import fakewiki, test_scoring_system, wait_time


def test_score():
    scoring_system = SingleThread({'fakewiki': fakewiki}, timeout=0.10)

    test_scoring_system(scoring_system)


def test_single_thread():
    scoring_system = SingleThread({'fakewiki': fakewiki}, timeout=1.0)

    response = scoring_system.score(
        ScoreRequest("fakewiki", [1], ["fake"],
                     injection_caches={1: {wait_time: 2.0}}))
    assert 1 in response.errors, str(response.errors)
    assert isinstance(response.errors[1]['fake'], errors.TimeoutError), \
           type(response.errors[1]['fake'])
