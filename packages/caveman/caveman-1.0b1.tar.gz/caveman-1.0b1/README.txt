Caveman: Validation of HTML5 cache manifests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Caveman is a package that parses and validates
`HTML5 cache manifests <http://www.w3.org/TR/html5/offline.html>`_.  HTML5
applications are notoriously picky about their cache manifests, and it is
difficult to check that all of the components are as they should be.

Caveman provides one command-line script, `check_manifest`, which pulls an HTML
page, scrapes it for used resources, parses its cache manifest, and validates
the resources against the manifest::

    $ check_manifest URL

Problems with the manifest are written to the standard output.  More detail
about the process is output if you set the log level to a different severity
with the --level=LEVEL switch, where LEVEL is DEBUG, INFO, WARNING, or ERROR.


Programmatic use
----------------

Caveman has been designed to be usable from your own code, for example, as
part of a larger validation process, or as part of unit tests in your web
application.

Caveman's work is done by the `ManifestChecker` class.  You instantiate it
with two helpers: a `get_url` function that fetches data from URLs, and a
`logger` object that gets logged messages::

    from caveman import ManifestChecker

    def get_url(url): ...

    logger = ...

    man_checker = ManifestChecker(get_url=get_url, logger=logger)

Then call its `check_manifest` method with the URL of the HTML page::

    man_checker.check_manifest(url)

No value is returned: the output has been logged to the logger object.
See the docstrings in the source code for details.


Django unit tests
+++++++++++++++++

As an example of programmatic use, here's one way to use Caveman in a Django
test suite::

    from caveman import ManifestChecker

    class TestManifest(django.test.TestCase):
        def setUp(self):
            self.checker = ManifestChecker(get_url=self.get_url, logger=self)
            self.caveman_log = []

        def get_url(self, url):
            """A get_url function for `caveman.ManifestChecker`."""
            # Use the Django test client to fetch the URL.
            response = self.client.get(url)
            return response.status_code, response.content, response

        # Record the serious Caveman messages in `self.caveman_log`.
        def debug(self, msg):       pass
        def info(self, msg):        pass
        def warning(self, msg):     self.caveman_log.append(msg)
        def error(self, msg):       self.caveman_log.append(msg)

        def test_my_manifest(self):
            """Caveman produces no warnings or errors for the cache manifest."""
            self.checker.check_manifest("/")
            self.assertEqual([], self.caveman_log)


Limitations
-----------

Caveman only pulls the HTML page you specify.  Although it validates links to
other HTML pages against the manifest, it does not pull those linked-to pages
and verify their resources.

Certain rules from the HTML5 spec are not validated.


More information
----------------

Caveman can be downloaded from PyPI: http://pypi.python.org/pypi/caveman

The HTML5 cache manifest spec is at http://www.w3.org/TR/html5/offline.html

Docs at `http://nedbatchelder.com/code/caveman <http://nedbatchelder.com/code/caveman>`_.

Code repository and issue tracker are at `bitbucket.org <http://bitbucket.org/ned/caveman>`_.
