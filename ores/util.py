
def jsonify_error(error):
    error_type = error.__class__.__name__
    message = str(error)

    return {'type': error_type, 'message': message}
