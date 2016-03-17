from collections import defaultdict, namedtuple

from nose.tools import eq_
from revscoring import dependencies

from ..scoring_context import ScoringContext


def test_scoring_context():
    from revscoring.datasources import Datasource
    from revscoring.dependencies import Dependent
    from revscoring.features import Feature

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

    scoring_context = ScoringContext("fakewiki", {"fake": scorer_model},
                                     extractor)

    rev_ids = [1, 2, 3, 4, 5]
    root_ds_caches = scoring_context.extract_roots("fake", rev_ids)
    eq_(len(root_ds_caches), 5)
    eq_(root_ds_caches[1][1][fake_data], "fake")
    assert root_ds_caches[5][0] is not None

    score = scoring_context.score("fake", {characters: 10, is_fake: False})
    eq_(score['prediction'], "generated")
