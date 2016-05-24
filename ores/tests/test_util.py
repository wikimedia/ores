import time

from nose.tools import raises

from ..util import timeout
from ..errors import TimeoutError


def test_timeout():
    timeout(int, 5, seconds=0.5)


@raises(TimeoutError)
def test_timeout_error():
    timeout(time.sleep, 0.1, seconds=0.05)
