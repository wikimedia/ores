
class ParamError(Exception):
    pass


def read_param(request, param, default=None, type=str):
    try:
        value = request.args.get(param, request.form.get(param))
        if value is None:
            return default
        else:
            return type(value)
    except (ValueError, TypeError) as e:
        raise ParamError("Could not interpret {0}. {1}"
                         .format(param, str(e)))


def read_bar_split_param(request, param, default=None, type=str):
    values = read_param(request, param, default=default)
    if values is None:
        return []

    try:
        return [type(value) for value in values.split("|")]
    except (ValueError, TypeError) as e:
        raise ParamError("Could not interpret {0}. {1}"
                         .format(param, str(e)))
