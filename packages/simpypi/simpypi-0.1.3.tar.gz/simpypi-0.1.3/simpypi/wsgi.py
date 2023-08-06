import os
import pkginfo
import shutil
import tempfile
from webob import Request, Response, exc

here = os.path.dirname(os.path.abspath(__file__))

class SimPyPI(object):
    """Simple Python Package Index"""

    def __init__(self, directory, index=None):

        self.directory = directory
        assert os.path.exists(directory)

        # request handlers
        self.handlers = dict([(method, getattr(self, method))
                              for method in ('GET', 'POST')])
        # TODO: HEAD, OPTIONS, maybe more

        # cache index HTML
        self.index = index or os.path.join(here, 'templates', 'index.html')
        assert os.path.exists(self.index)
        self.index = file(self.index).read()

    def __call__(self, environ, start_response):

        # get a request object
        request = Request(environ)

        # match the request to a handler
        handler = self.handlers.get(request.method)
        if handler:
            res = handler(request)
        else:
            res = exc.HTTPNotFound()

        return res(environ, start_response)

    def GET(self, request):
        return Response(body=self.index, content_type='text/html')

    def POST(self, request):
        """handle posting a package"""

        # get the package
        try:
            package = request.POST['package']
        except KeyError:
            # sanity check: does the field exist?
            return exc.HTTPBadRequest()

        # sanity check: is it a file? (TODO)
        if not hasattr(package, 'file') or not hasattr(package, 'filename'):
            return exc.HTTPBadRequest()

        # successful response: redirect to the main page
        response = exc.HTTPSeeOther()

        # make a temporary copy for pkginfo
        # (or PaInt?)
        tmpdir = tempfile.mkdtemp()
        try:
            path = os.path.join(tmpdir, package.filename)
            f = file(path, 'w')
            f.write(package.file.read())
            f.close()

            # get package data
            sdist = pkginfo.sdist.SDist(path)

            # put the package in the right place
            self.add_package(sdist)
        except BaseException, e:
            # something bad happen
            response = exc.HTTPBadRequest()
        finally:
            # cleanup
            shutil.rmtree(tmpdir)

        return response

    ### API

    def add_package(self, sdist, move=True):
        """
        add a package to the directory
        """

        # make a directory for the package
        directory = os.path.join(self.directory, sdist.name)
        if not os.path.exists(directory):
            os.mkdir(directory)
        assert os.path.isdir(directory)

        # determine the extension (XXX hacky)
        extensions = ('.tar.gz', '.zip', '.tar.bz2')
        for ext in extensions:
            if sdist.filename.endswith(ext):
                break
        else:
            raise Exception("Extension %s not found: %s" % (extensions, sdist.filename))

        # get the filename destination
        filename = '%s-%s%s' % (sdist.name, sdist.version, ext)
        filename = os.path.join(directory, filename)

        if move:
            # move the file
            shutil.move(sdist.filename, filename)
        else:
            # copy the file
            shutil.copy(sdist.filename, filename)
