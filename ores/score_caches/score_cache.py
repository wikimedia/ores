import yamlconf


class ScoreCache:

    def lookup(self, wiki, model, rev_id, version=None):
        """
        Returns a pre-cached score
        """
        raise NotImplementedError()

    def store(self, wiki, model, rev_id, score):
        """
        Caches a new score
        """
        raise NotImplementedError()

    def context(self, wiki, model, version=None):
        return Context(self, wiki, model, version=None)

    @classmethod
    def from_config(cls, config, name, section_key="score_caches"):
        section = config[section_key][name]
        if 'module' in section:
            return yamlconf.import_module(section['module'])
        elif 'class' in section:
            Class = yamlconf.import_module(section['class'])
            return Class.from_config(config, name)
