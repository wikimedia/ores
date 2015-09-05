import logging
import time
import traceback

import stopit

from ..score_caches import ScoreCache
from .score_processor import SimpleScoreProcessor

logger = logging.getLogger("ores.score_processors.timeout")


class Timeout(SimpleScoreProcessor):

    def __init__(self, *args, timeout=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeout = float(timeout) if timeout is not None else None

    def _process(self, context, model, cache):
        return timeout(super()._process, context, model, cache,
                       seconds=self.timeout)


    @classmethod
    def from_config(cls, config, name, section_key="score_processors"):
        section = config[section_key][name]

        # TODO: this is a weird place to have this set.
        if 'data_paths' in config['ores'] and \
           'nltk' in config['ores']['data_paths']:
            import nltk
            nltk.data.path.append(config['ores']['data_paths']['nltk'])

        from ..scoring_contexts import ScoringContext

        section = config[section_key][name]

        scoring_contexts = {name: ScoringContext.from_config(config, name)
                            for name in section['scoring_contexts']}

        if 'score_cache' in section:
            score_cache = ScoreCache.from_config(config, section['score_cache'])
        else:
            score_cache = None

        timeout = section.get('timeout')

        return cls(scoring_contexts, score_cache=score_cache, timeout=timeout)


class TimeoutError(Exception):
    pass


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
