import logging
import time

import yamlconf

logger = logging.getLogger("ores.score_processors.score_processor")


class ScoreResult():
    def get(self, *args, **kwargs):
        raise NotImplementedError()


class ScoreProcessor:

    def process(self, *args, **kwargs):
        raise NotImplementedError()

    @classmethod
    def from_config(cls, config, name, section_key="score_processors"):
        logger.info("Loading ScoreProcessor '{0}' from config.".format(name))
        section = config[section_key][name]
        if 'module' in section:
            return yamlconf.import_module(section['module'])
        elif 'class' in section:
            Class = yamlconf.import_module(section['class'])
            return Class.from_config(config, name)


class SimpleScoreResult(ScoreResult):

    def __init__(self, *, score=None, error=None):
        self.score = score
        self.error = error

    def get(self):
        if self.error is not None:
            raise self.error
        else:
            return self.score


def process_score(scorer_model, extractor, cache):
    # TODO: record time spend extracting features
    start = time.time()
    features = list(extractor.solve(scorer_model.features, cache=cache))
    logger.debug("Extracted features in {0} seconds"
                 .format(time.time() - start))

    # TODO: record time spent generating a score
    start = time.time()
    score = scorer_model.score(features)
    logger.debug("Scored features in {0} seconds"
                 .format(time.time() - start))

    return score
