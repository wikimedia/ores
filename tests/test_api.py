from ores import api


class FakeSession:

    def __init__(self, error_out=False):
        self.error_out = error_out

    def get(self, url, params, headers, verify=False, stream=False):
        if self.error_out:
            return FakeResponse(
                {"error": {"code": "an error", "message": "a message"}})
        else:
            return FakeResponse({
                "context": {
                    "scores": {
                        str(rev_id): {model: {"score": "my score"}
                                      for model in params['models'].split("|")}
                        for rev_id in params['revids'].split("|")
                    }
                }
            })


class FakeResponse:

    def __init__(self, doc):
        self.doc = doc

    def json(self):
        return self.doc


def test_fake_session():
    session = FakeSession(error_out=True)
    response = session.get(None, None, None)
    doc = response.json()
    assert 'error' in doc


def test_session():
    session1 = api.Session("myhost", session=FakeSession())
    scores = list(session1.score("context", ["foo", "bar"], range(0, 100)))
    assert len(scores) == 100
    assert scores[0] == {"foo": {"score": "my score"},
                         "bar": {"score": "my score"}}


def test_base_error():
    session2 = api.Session("myhost", session=FakeSession(error_out=True))
    scores = list(session2.score("context", ["foo", "bar"], range(0, 100)))
    assert len(scores) == 100
    assert scores[0]['foo']['error'] == \
        {'code': 'an error', 'message': 'a message'}
