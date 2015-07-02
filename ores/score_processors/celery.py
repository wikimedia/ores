import logging

import celery

from .score_processor import ScoreProcessor, ScoreResult, process_score
from .timeout import timeout as timeout_func

logger = logging.getLogger("ores.score_processors.celery")


def configure(config, name, section_key="score_processors"):
    section = config[section_key][name]

    application = celery.Celery("ores")
    logger.info("Configuring Celery application {0}".format(repr(name)))

    @application.task(track_started=True)
    def score(*args, timeout=None, **kwargs):
        return timeout_func(process_score, *args, seconds=timeout, **kwargs)

    application_config_kwargs = {k: v for k, v in section.items()
                                 if k not in ("class", "timeout")}

    application.conf.update(**application_config_kwargs)

    return application


class CeleryTimeoutResult(ScoreResult):

    def __init__(self, async_result, timeout):
        self.async_result = async_result
        self.timeout = float(timeout)

    def get(self):
        return self.async_result.get(self.timeout)


class Celery(ScoreProcessor):

    def __init__(self, application, timeout=None):
        self.application = application
        self.timeout = float(timeout) if timeout is not None else None

        # This is a bit of a hack, but it works in practice.
        self._process = application.tasks['ores.score_processors.celery.score']

    def in_progress(self, id):
        id_bytes = bytes(":".join(str(v) for v in id), 'utf-8')

        # Try to get an async_result for an in_progress task
        logger.debug("Checking if {0} is already being processed"
                     .format(repr(id)))
        result = self._process.AsyncResult(task_id=id_bytes)
        if result.state not in ("STARTED", "SUCCESS"):
            raise KeyError(id)
        else:
            logger.debug("Found AsyncResult for {0}".format(repr(id)))
            return result

    def process(self, *args, id=None, **kwargs):
        id_bytes = bytes(":".join(str(v) for v in id), 'utf-8')

        # Tells the _process function to time itself out
        kwargs['timeout'] = self.timeout

        # Starts a new task and gets async result
        logger.debug("Starting a new task for {0}".format(repr(id)))
        result = self._process.apply_async(args=args, kwargs=kwargs,
                                           task_id=id_bytes)

        # Wraps the result so the get function implements a timeout
        return CeleryTimeoutResult(result, self.timeout)

    @classmethod
    def from_config(cls, config, name, section_key="score_processors"):
        section = config[section_key][name]

        timeout = section.get('timeout')

        application = configure(config, name, section_key=section_key)

        return cls(application, timeout)
