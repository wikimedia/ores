from importlib import import_module


def import_from_path(path):
    """
    Import a module from a path.

    Args:
        path: (str): write your description
    """
    parts = path.split(".")
    module_path = ".".join(parts[:-1])
    attribute_name = parts[-1]

    module = import_module(module_path)

    attribute = getattr(module, attribute_name)

    return attribute
