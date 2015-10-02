import logging

logger = logging.getLogger("ores.score_caches.score_cache")


class ScoreCache:

    def lookup(self, wiki, model, rev_id, version=None):
        """
        Returns a pre-cached score
        """
        raise NotImplementedError()

    def store(self, wiki, model, rev_id, score, version=None):
        """
        Caches a new score
        """
        raise NotImplementedError()

    def context(self, wiki, model, version=None):
        return Context(self, wiki, model, version=None)

    @classmethod
    def from_config(cls, config, name, section_key="score_caches"):
        try:
            import yamlconf
        except ImportError:
            raise ImportError("Could not find yamlconf.  This packages is " +
                              "required when using yaml config files.")
        logger.info("Loading ScoreCache '{0}' from config.".format(name))
        section = config[section_key][name]
        if 'module' in section:
            return yamlconf.import_module(section['module'])
        elif 'class' in section:
            Class = yamlconf.import_module(section['class'])
            return Class.from_config(config, name)


class Context:

    def __init__(self, scorer_cache, wiki, model, version=None):
        self.scorer_cache = scorer_cache
        self.wiki = str(wiki)
        self.model = str(model)
        self.version = version

    def lookup(self, rev_id):
        return self.scorer_cache.lookup(self.wiki, self.model, rev_id,
                                        version=self.version)

    def store(self, rev_id, score):
        return self.scorer_cache.store(self.wiki, self.model, rev_id, score,
                                       version=self.version)
