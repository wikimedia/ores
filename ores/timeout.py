import logging
import time
import traceback

import stopit

logger = logging.getLogger(__name__)


def timeout(func, *args, seconds=None, **kwargs):
    if seconds is None:
        return func(*args, **kwargs)

    try:
        start = time.time()
        with stopit.ThreadingTimeout(seconds) as to_ctx_mgr:
            result = func(*args, **kwargs)
        duration = time.time() - start

        # OK, let's check what happened
        if to_ctx_mgr.state == to_ctx_mgr.EXECUTED:
            # All's fine, everything was executed
            return result
        elif to_ctx_mgr.state == to_ctx_mgr.TIMED_OUT:
            # Timeout occurred while executing the block
            raise TimeoutError("Timed out after {0} seconds.".format(duration))
        else:
            traceback.print_tb()
            raise RuntimeError("Something weird happened.")

    except stopit.TimeoutException as e:
        raise TimeoutError("Timed out after {0} seconds.".format(e.seconds))

    duration = time.time() - seconds
