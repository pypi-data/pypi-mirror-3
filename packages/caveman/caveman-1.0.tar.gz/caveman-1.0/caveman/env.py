"""Manage external resources for Caveman."""

class Env(object):
    """Hold references to external resources needed by Caveman."""

    def __init__(self, get_url, logger):
        """
        `get_url` is a function taking a URL and returning a triple, 
        (status, data, headers).  

        `logger` must have four callable attributes: debug, info, warning, error,
        each taking a message to report.
        
        """
        self.get_url = get_url
        self.logger = logger

    def fetch_url(self, url, kind='data', content_type=None):
        """Get something from a url.

        If `content_type` is specified, then a warning will be issued if it is wrong.
        
        Returns the data read from the url. If a page couldn't be fetched,
        returns None.

        """
        self.logger.info("Fetching %s from %r" % (kind, url))
        status, data, headers = self.get_url(url)
        if status != 200:
            self.logger.warning("Bad status for %s from %r: %d" % (kind, url, status))
            data = None
        else:
            if content_type:
                got = headers['content-type']
                # Content-type can be: "text/html; charset=utf-8"
                if ";" in got:
                    got = got.split(';', 1)[0]
                got = got.strip()
                if got != content_type:
                    self.logger.warning("Wrong content type for %s from %r: expected %r, got %r" % (kind, url, content_type, got))
        return data
