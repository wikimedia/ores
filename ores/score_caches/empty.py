from .score_cache import ScoreCache


class Empty(ScoreCache):

    def lookup(self, *args, **kwargs):
        """
        Lookup a lookup.

        Args:
            self: (todo): write your description
        """
        raise KeyError()

    def store(self, *args, **kwargs):
        """
        Calls the callable.

        Args:
            self: (todo): write your description
        """
        return None

    @classmethod
    def from_config(cls, config, name, section_key="score_caches"):
        """
        Initialize an instance from a configuration file.

        Args:
            cls: (todo): write your description
            config: (todo): write your description
            name: (str): write your description
            section_key: (str): write your description
        """
        return cls()
