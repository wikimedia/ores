from . import errors


class ParamError(Exception):

    def __init__(self, error):
        super().__init__()
        self.error = error


def read_param(request, param, default=None, type=str):
    try:
        value = request.args.get(param, request.form.get(param, default))
        return type(value.strip())
    except (ValueError, TypeError) as e:
        error = errors.bad_request("Could not interpret {0}. {1}"
                                   .format(param, str(e)))
        raise ParamError(error)


def read_bar_split_param(request, param, default=None, type=str):
    values = read_param(request, param, default=default)
    if values is None:
        return []
    return [type(value) for value in values.split("|")]
