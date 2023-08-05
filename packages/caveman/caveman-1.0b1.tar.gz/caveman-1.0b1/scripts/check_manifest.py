#/bin/env python

import logging
import optparse
import sys
import urllib

from caveman import ManifestChecker

def really_get_url(url):
    """Fetch a URL, to help ManifestChecker."""
    u = urllib.urlopen(url)
    data = u.read()
    return u.getcode(), data, dict(u.headers)

def main(argv):
    """Run this as a command-line tool."""
    parser = optparse.OptionParser(usage="usage: %prog [options] URL")
    parser.add_option("-l", "--level", help="Logging level to use (DEBUG, INFO, WARNING, ERROR)", default="WARNING")
    options, args = parser.parse_args(argv[1:])

    if not args:
        print "Need a url to scrape"
        return

    logging.basicConfig(stream=sys.stderr, level=getattr(logging, options.level), format="%(levelname)8s: %(msg)s")
    logger = logging.getLogger(__name__)
    ManifestChecker(get_url=really_get_url, logger=logger).check_manifest(args[0])

if __name__ == '__main__':
    main(sys.argv)

