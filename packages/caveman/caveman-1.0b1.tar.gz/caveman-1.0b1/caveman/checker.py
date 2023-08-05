"""The Caveman manifest checker."""

import lxml.html
from caveman.urls import same_origin, same_resource, resolve, split_fragment
from caveman.manifest import Manifest
from caveman.env import Env


class Link(object):
    """A link to an HTTP resource, with info about where it came from."""
    def __init__(self, env, url, tag, pos, source):
        self.url = url
        self.tag = tag
        self.pos = pos
        self.source = source
        env.logger.debug("Found link: %r" % self)

    def __repr__(self):
        return "%s (%s from %r)" % (self.url, self.tag, self.source)


class ManifestChecker(object):
    def __init__(self, get_url, logger):
        """Check the manifest for a URL.

        `get_url` is a function taking a URL and returning a triple, 
        (status, data, headers).  

        `logger` must have four callable attributes: debug, info, warning, error,
        each taking a message to report.

        """
        self.env = Env(get_url, logger)

    def stylesheets(self, html, base):
        """Generate a sequence of absolute stylesheet urls in `html`."""
        for link in html.iterlinks():
            elt, attr, url, pos = link
            if elt.tag == 'link' and elt.attrib.get('rel') == 'stylesheet':
                yield resolve(base, url)
            if elt.tag == 'style' and url.endswith('.css'):
                yield resolve(base, url)

    def links(self, html, base):
        """Generate a sequence of Links in `html`, including through referenced stylesheets."""
        for stylesheet_url in self.stylesheets(html, base):
            css = self.env.fetch_url(stylesheet_url, "stylesheet", content_type="text/css")
            if css:
                css_html = lxml.html.fromstring("<style>%s</style>" % css)
                for link in self.links(css_html, stylesheet_url):
                    yield link
        for link in html.iterlinks():
            elt, attr, url, pos = link
            url, _ = split_fragment(url)
            if not url:
                continue
            tag = elt.tag
            if tag == 'link':
                tag += ":" + elt.attrib.get('rel', 'NONE').replace(' ', '_')
            if attr:
                tag += "." + attr
            url = resolve(base, url)
            yield Link(self.env, url, tag, pos, source=base)

    def open_page(self, page_url):
        """Open the page."""
        self.page_url = page_url
        html = self.env.fetch_url(self.page_url, "html", content_type="text/html")
        self.page_html = lxml.html.fromstring(html)

    def page_links(self):
        """A sequence of links found on the page opened by `open_page`."""
        return self.links(self.page_html, self.page_url)

    def check_manifest(self, page_url):
        """Check an HTML5 cache manifest.

        The HTML page at `page_url` is fetched and crawled.  An interesting
        narrative is fed to `self.env.logger`, including warnings and errors.

        """
        # Get HTML, find manifest.
        self.open_page(page_url)
        try:
            manifest_url = self.page_html.attrib['manifest']
        except KeyError:
            self.env.logger.error("HTML at %r has no manifest attribute" % self.page_url)
            return

        # Get and parse the manifest.
        manifest = Manifest(self.env)
        manifest.open(resolve(self.page_url, manifest_url))
        manifest.verify()

        # Examine all the links in the page against the manifest.
        for link in self.page_links():
            if not same_origin(link.url, self.page_url):
                self.env.logger.debug("Off-site link: %r" % link)
            elif same_resource(link.url, self.page_url):
                self.env.logger.debug("Link to self: %r" % link)
            elif link.url in manifest.explicit_urls:
                self.env.logger.debug("Link mentioned explicitly in manifest: %r" % link)
            elif manifest.online_whitelist_wildcard_flag == 'open':
                self.env.logger.debug("Link allowed by * wildcard: %r" % link)
            elif manifest.matches_online_whitelist(link.url):
                self.env.logger.debug("Link matches whitelist: %r" % link)
            else:
                self.env.logger.warning("Link unaccounted: %r" % link)
