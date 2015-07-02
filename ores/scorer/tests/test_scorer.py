from collections import defaultdict, namedtuple

from nose.tools import eq_
from revscoring import dependencies

from ..scorer import Scorer


def test_scorer():
    from revscoring.datasources import Datasource
    from revscoring.dependencies import Dependent
    from revscoring.features import Feature

    from ...score_caches import LRU

    fake_data = Datasource("fake_data", lambda: "fake")
    len_func = Dependent("len_func")
    literal_fake = Dependent("literal_fake")
    characters = Feature("characters", lambda word, len: len(word),
                         returns=int,
                         depends_on=[fake_data, len_func])
    is_fake = Feature("is_fake", lambda word, fake: word == fake,
                      returns=bool,
                      depends_on=[fake_data, literal_fake])

    FakeExtractor = namedtuple("Extractor", ['extract', 'solve', 'language'])

    def fake_extract(rev_ids, dependents, caches=None):
        caches = caches or defaultdict(dict)
        for rev_id in rev_ids:
            cache = caches[rev_id]
            if rev_id % 5 != 0:
                values = dependencies.solve(dependents,
                                            context={len_func: lambda: len},
                                            cache=cache)
                yield None, list(values)
            else:
                yield RuntimeError("extract"), None

    def fake_solve(dependents, cache=None):
        cache = cache or {}
        cache.update({len_func: len,
                      literal_fake: "fake"})
        return dependencies.solve(dependents, cache=cache)

    extractor = FakeExtractor(fake_extract, fake_solve, None)

    FakeScorerModel = namedtuple("FakeScorerModel",
                                 ['score', 'version', 'language', 'features'])
    scorer_model = FakeScorerModel(lambda fvs: {"prediction": "generated"},
                                   "1", None, [characters, is_fake])

    score_cache = LRU(128)
    score_cache.store("fakewiki", "fake", 2, {"cached": True}, version="1")

    scorer = Scorer("fakewiki", {"fake": scorer_model}, extractor,
                    score_cache=score_cache)

    rev_ids = list(range(10))
    for rev_id, score in scorer.score(rev_ids, model="fake").items():
        print(score)
        if rev_id % 5 == 0:
            assert 'error' in score
            eq_(score['error']['message'], "extract")
        elif rev_id == 2:
            assert 'cached' in score
            eq_(score['cached'], True)
        else:
            eq_(score['prediction'], "generated")
