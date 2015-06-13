
from .score_processor import ScoreProcessor, process_score


class Celery(ScoreProcessor):

    def __init__(self, celery, timeout=None)
        self.celery = celery
        self.timeout = timeout

        @self.celery.task
        def _process(*args, **kwargs):
            process_score(*args, **kwargs)


        self._process = _process

    def process(self, *args, **kwargs):
        return self._process.apply_async(args=args, kwargs=kwargs,
                                         expires=self.timeout)
