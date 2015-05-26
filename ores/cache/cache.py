
class Cache:

    def lookup(wiki, model, rev_id):
        """
        Returns a pre-cached score
        """
        raise NotImplementedError()

    def store(wiki, model, rev_id, score):
        """
        Caches a new score
        """
        raise NotImplementedError()
