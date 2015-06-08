from nose.tools import raises

from ..empty import Empty


def test_empty():

    empty = Empty()
    context = empty.context("foo", "bar", version="nope")
    context.store(1, "foo")


@raises(KeyError)
def test_key_error():

    empty = Empty()
    context = empty.context("foo", "bar", version="nope")
    context.store(1, "foo")

    context.lookup(1)
