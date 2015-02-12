

def error(status, code, message):
    return {'error': {'code': code, 'message': message}}, status

def bad_request(message):
    return error(400, 'request invalid', message)
