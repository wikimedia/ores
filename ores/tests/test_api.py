from .. import api


def test_session():
    #  Ensures that the class can be constructed
    api.Session("foo")
