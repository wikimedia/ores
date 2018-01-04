

def format_set(s):
    return "{" + ", ".join(repr(value) for value in sorted(s)) + "}"
