from .cache import cache


class Nope(Cache):

    def lookup(*args, **kwargs): return None
    def store(*args, **kwargs): return None
