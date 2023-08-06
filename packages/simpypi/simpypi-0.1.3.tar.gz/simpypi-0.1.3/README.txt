simpypi
=======

Simple python package index

How simpypi works
-----------------

The heart of simpypi is ``simpypi.wsgi.SimPyPI``, a simple
`WSGI <http://www.python.org/dev/peps/pep-0333/>`_ web app that
accepts a uploaded
`python package <http://guide.python-distribute.org/introduction.html>`_
distribution and places it according to its name and version metadata
appropriate to the
`simple index protocol <http://guide.python-distribute.org/contributing.html#the-simple-index-protocol>`_ .

For security, ``SimPyPI`` returns straight
`HTTP 400 <http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html>`_ s
for invalid requests.  This could probably be improved.

``SimPyPI`` itself does not serve this directory.  The directory
should be served by a fileserver that will generate directory indices
(as apprpropriate to
http://guide.python-distribute.org/contributing.html#the-simple-index-protocol
) such as Apache or
`FileServer <http://pypi.python.org/pypi/FileServer>`_ .
``simpypi.factory.factory`` does provide a factory to make a WSGI app
that wraps ``FileServer`` in middleware and serves the simple index
under ``/index/`` and the ``SimPyPI`` app at ``/``.  Additionally, a
``simpypi`` command line program is provided that front-ends this.

Currently ``simpypi`` only works on source distributions (that is,
packages made with ``python setup.py sdist``).

Example
-------

I installed an instance of ``simpypi`` at http://k0s.org:8080 for
demonstration purposes with a package index at http://k0s.org:8080/index/ .
For testing purposes, I made a script,
`upload_mobase.py <http://k0s.org/mozilla/hg/simpypi/file/tip/tests/upload_mozbase.py>`_
that uploads the
`mozbase <https://github.com/mozilla/mozbase>`_ packages to
``simpypi``.  So the
`index <http://k0s.org:8080/index/>`_ is now populated with them.

You can upload packages with
`curl <http://www.cs.sunysb.edu/documentation/curl/>`_ ::

    > wget http://pypi.python.org/packages/source/P/PyYAML/PyYAML-3.10.tar.gz
    > curl -F 'package=@PyYAML-3.10.tar.gz' http://k0s.org:8080/

You can ``easy_install`` mozbase from http://k0s.org:8080/index/ .
If a package's dependencies can be found from the ``simpypi`` package
index, they will also be installed from the index::

    > virtualenv.py tmp
    New python executable in tmp/bin/python
    Installing setuptools............done.
    Installing pip...............done.
    > cd tmp/
    (tmp)│easy_install -i http://k0s.org:8080/index/ mozrunner
    Searching for mozrunner
    Reading http://k0s.org:8080/index/mozrunner/
    Best match: mozrunner 5.1
    Downloading http://k0s.org:8080/index/mozrunner/mozrunner-5.1.tar.gz
    Processing mozrunner-5.1.tar.gz
    Running mozrunner-5.1/setup.py -q bdist_egg --dist-dir
    /tmp/easy_install-gqerOV/mozrunner-5.1/egg-dist-tmp-Qyx3Cr
    Adding mozrunner 5.1 to easy-install.pth file
    Installing mozrunner script to /home/jhammel/tmp/bin
    Installed
    /home/jhammel/tmp/lib/python2.7/site-packages/mozrunner-5.1-py2.7.egg
    Processing dependencies for mozrunner
    Searching for mozprofile>=0.1
    Reading http://k0s.org:8080/index/mozprofile/
    Best match: mozprofile 0.1
    Downloading http://k0s.org:8080/index/mozprofile/mozprofile-0.1.tar.gz
    Processing mozprofile-0.1.tar.gz
    Running mozprofile-0.1/setup.py -q bdist_egg --dist-dir
    /tmp/easy_install-4Im6x0/mozprofile-0.1/egg-dist-tmp-9Jp5TR
    Adding mozprofile 0.1 to easy-install.pth file
    Installing mozprofile script to /home/jhammel/tmp/bin
    Installed
    /home/jhammel/tmp/lib/python2.7/site-packages/mozprofile-0.1-py2.7.egg
    Searching for mozprocess
    Reading http://k0s.org:8080/index/mozprocess/
    Best match: mozprocess 0.1b2
    Downloading
    http://k0s.org:8080/index/mozprocess/mozprocess-0.1b2.tar.gz
    Processing mozprocess-0.1b2.tar.gz
    Running mozprocess-0.1b2/setup.py -q bdist_egg --dist-dir
    /tmp/easy_install-KU6AiF/mozprocess-0.1b2/egg-dist-tmp-4j5CMP
    Adding mozprocess 0.1b2 to easy-install.pth file
    Installed
    /home/jhammel/tmp/lib/python2.7/site-packages/mozprocess-0.1b2-py2.7.egg
    Searching for mozinfo
    Reading http://k0s.org:8080/index/mozinfo/
    Best match: mozinfo 0.3.3
    Downloading http://k0s.org:8080/index/mozinfo/mozinfo-0.3.3.tar.gz
    Processing mozinfo-0.3.3.tar.gz
    Running mozinfo-0.3.3/setup.py -q bdist_egg --dist-dir
    /tmp/easy_install-JaKeaz/mozinfo-0.3.3/egg-dist-tmp-xWojez
    Adding mozinfo 0.3.3 to easy-install.pth file
    Installing mozinfo script to /home/jhammel/tmp/bin
    Installed
    /home/jhammel/tmp/lib/python2.7/site-packages/mozinfo-0.3.3-py2.7.egg
    Searching for ManifestDestiny>=0.5.4
    Reading http://k0s.org:8080/index/ManifestDestiny/
    Best match: ManifestDestiny 0.5.4
    Downloading
    http://k0s.org:8080/index/ManifestDestiny/ManifestDestiny-0.5.4.tar.gz
    Processing ManifestDestiny-0.5.4.tar.gz
    Running ManifestDestiny-0.5.4/setup.py -q bdist_egg --dist-dir
    /tmp/easy_install-2blF3S/ManifestDestiny-0.5.4/egg-dist-tmp-R3KZde
    Adding ManifestDestiny 0.5.4 to easy-install.pth file
    Installing manifestparser script to /home/jhammel/tmp/bin
    Installed
    /home/jhammel/tmp/lib/python2.7/site-packages/ManifestDestiny-0.5.4-py2.7.egg
    Finished processing dependencies for mozrunner

Note that all of the packages come from the k0s.org installation and
not from http://pypi.python.org/ .


Running the Tests
-----------------

The
`tests directory <http://k0s.org/mozilla/hg/simpypi/file/tip/tests>`_
contains
`doctests <http://docs.python.org/library/doctest.html>`_ and
the test-runner,
`test.py <http://k0s.org/mozilla/hg/simpypi/file/tip/tests/test.py>`_ .
These tests illustrate basic functionality and protect from
regressions if they are run before code is committed.
``tests-require.txt`` contains dependencies that should be installed
to run the tests.
`Paste <http://pythonpaste.org/>`_
`TestApp <http://pythonpaste.org/testing-applications.html>`_ ,
though this could be transitioned to
`WebTest <http://webtest.pythonpaste.org/en/latest/index.html>`_ .
`virtualenv <http://www.virtualenv.org/>`_
is used for isolating python environments.

To run the tests, do::

    python test.py

TODO
----

While simpypi is pretty simple, just because it is only 100 lines of
code doesn't mean that it is the *right* 100 lines of code.  The
following issues could be addressed:

 * the temporary package should be dealt with entirely in memory,
   ideally.  Currently we write to a file and move it.

 * ``simpypi`` use ``pkginfo.sdist`` to read the data from a source
   distribution. Instead, the uploaded package should probably be
   unpacked and ``python setup.py sdist`` run and the resulting
   package put in the appropriate place.  This will allow archives
   without ``PKG-INFO``
   (e.g. http://hg.mozilla.org/build/talos/archive/tip.tar.gz )
   to be uploaded as well as at least partially correct for the fact
   that currently ``simpypi`` only works for uploaded source
   distributions.

--

http://k0s.org/mozilla/hg/simpypi
