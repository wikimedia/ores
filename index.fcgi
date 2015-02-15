#!/usr/bin/env python3
from ores.wsgi import scorers, routes
from ores.wsgi.app import app
from flask import request

app.debug = True

@app.errorhandler(404)
def page_not_found(error):
    return '<h1>404 - Not found</h1><p><small>' + request.path + '</small></p><p><small>' + repr(app.url_map) + '</small></p>', 404

scorers.configure(open('models/enwiki.reverted.linear_svc.model', 'rb'),
                  open('models/ptwiki.reverted.linear_svc.model', 'rb'),
                  'https://en.wikipedia.org/w/api.php',
                  'https://pt.wikipedia.org/w/api.php')

if __name__ == '__main__':
    from flup.server.fcgi import WSGIServer
    WSGIServer(app, debug=True).run()
