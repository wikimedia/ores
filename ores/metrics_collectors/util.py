

def format_set(s):
    l = list(s)
    l.sort()
    return "{" + ", ".join(repr(value) for value in l) + "}"
