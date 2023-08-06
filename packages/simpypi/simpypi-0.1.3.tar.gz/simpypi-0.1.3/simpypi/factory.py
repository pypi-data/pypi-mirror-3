#!/usr/bin/env python

"""
WSGI factories for simpypi
"""

import optparse
import os
import shutil
import sys
import tempfile

from fileserver import DirectoryServer
from webob import exc
from wsgi import SimPyPI
from wsgiref import simple_server

class NamespacedFileserver(DirectoryServer):

    def __init__(self, app, directory, namespace):
        DirectoryServer.__init__(self, directory)
        self.app = app
        self.namespace = namespace

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO']
        if path == self.namespace:
            response = exc.HTTPMovedPermanently(add_slash=True)
            return response(environ, start_response)
            environ['PATH_INFO'] = '/'
            return DirectoryServer.__call__(self, environ, start_response)
        elif path.startswith(self.namespace + '/'):
            environ['PATH_INFO'] = path[len(self.namespace):]
            return DirectoryServer.__call__(self, environ, start_response)
        return self.app(environ, start_response)


def factory(**app_conf):
    """create a webob view and wrap it in middleware"""
    directory = app_conf['directory']
    app = SimPyPI(**app_conf)
    return NamespacedFileserver(app, directory, '/index')

def main(args=sys.argv[1:]):

    # parse command line options
    usage = '%prog [options]'
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-p', '--port', dest='port',
                      type='int', default=8080,
                      help="port to run the server on")
    parser.add_option('-d', '--directory', dest='directory',
                      help='directory to serve')
    options, args = parser.parse_args(args)

    # create a temporary directory, if none specified
    tmpdir = None
    if not options.directory:
        tmpdir = tempfile.mkdtemp()
        options.directory = tmpdir

    # serve
    print "http://localhost:%d/" % options.port
    try:
        app = factory(directory=options.directory)
        server = simple_server.make_server(host='0.0.0.0', port=options.port, app=app)
        server.serve_forever()
    finally:
        if tmpdir:
            shutil.rmtree(tmpdir)

if __name__ == '__main__':
    main()
