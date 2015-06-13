import signal

from .score_processor import ScoreProcessor, SimpleScoreResult, process_score


class Timeout(ScoreProcessor):

    def __init__(self, timeout=None):

        self.timeout = timeout

    def process(self, scorer_model, extractor, cache):

        def _process():
            return process_score(scorer_model, extractor, cache)

        try:
            score = timeout(_process, self.timeout)
        except RuntimeError as e:
            score = {
                'error': {
                    'type': str(type(e)),
                    'message': str(e)
                }
            }

        return SimpleScoreResult(score)

def timeout_handler(signum, frame):
    raise RuntimeError("Function execution timed out.")

def timeout(func, seconds=None):
    if seconds is not None:
        result = func()
    else:
        # Set the signal handler and a 5-second alarm
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(seconds)

        # This func() may hang indefinitely
        result = func()

        signal.alarm(0)          # Disable the alarm

    return result
