

def format_set(s):
    """
    Format a string to a string.

    Args:
        s: (str): write your description
    """
    return "{" + ", ".join(repr(value) for value in sorted(s)) + "}"
