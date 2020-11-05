import logging

logger = logging.getLogger("ores.score_caches.score_cache")


class ScoreCache:

    def lookup(self, score, context_name, model_name, rev_id, version=None, injection_cache=None):
        """
        Returns a pre-cached score
        """
        raise NotImplementedError()

    def store(self, score, context_name, model_name, rev_id, version=None,
              injection_cache=None):
        """
        Caches a new score
        """
        raise NotImplementedError()

    def context(self, wiki, model, version=None):
        """
        Constructs a context

        Args:
            self: (todo): write your description
            wiki: (todo): write your description
            model: (todo): write your description
            version: (str): write your description
        """
        return Context(self, wiki, model, version=None)

    @classmethod
    def from_config(cls, config, name, section_key="score_caches"):
        """
        Create a class from a configuration file.

        Args:
            cls: (todo): write your description
            config: (todo): write your description
            name: (str): write your description
            section_key: (str): write your description
        """
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

    def __init__(self, scorer_cache, context, model, version=None):
        """
        Initialize the cache.

        Args:
            self: (todo): write your description
            scorer_cache: (todo): write your description
            context: (str): write your description
            model: (todo): write your description
            version: (todo): write your description
        """
        self.scorer_cache = scorer_cache
        self.context = str(context)
        self.model = str(model)
        self.version = version

    def lookup(self, rev_id, injection_cache=None):
        """
        Look up a scorer object.

        Args:
            self: (todo): write your description
            rev_id: (int): write your description
            injection_cache: (todo): write your description
        """
        return self.scorer_cache.lookup(
            self.context, self.model, rev_id, injection_cache=injection_cache,
            version=self.version)

    def store(self, rev_id, score, injection_cache=None):
        """
        Store a cache for a particular revision.

        Args:
            self: (todo): write your description
            rev_id: (str): write your description
            score: (todo): write your description
            injection_cache: (todo): write your description
        """
        return self.scorer_cache.store(
            score, self.context, self.model, rev_id,
            injection_cache=injection_cache, version=self.version)
