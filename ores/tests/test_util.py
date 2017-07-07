import time

from nose.tools import raises

from ..errors import TimeoutError
from ..util import timeout


def test_timeout():
    timeout(int, 5, seconds=0.5)


@raises(TimeoutError)
def test_timeout_error():
    timeout(time.sleep, 2, seconds=1)
