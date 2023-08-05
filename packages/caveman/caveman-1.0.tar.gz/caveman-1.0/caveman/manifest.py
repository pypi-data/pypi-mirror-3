"""Caveman's representation of a cache manifest."""

from caveman.urls import resolve, split_fragment

class Manifest(object):
    """An HTML5 manifest:

        man = Manifest()
        man.open(url_to_manifest)
        # examine the data:
        man.url             # where the manifest came from
        man.explicit_urls   # a list
        man.fallbacks       # a dict
        man.online_whitelist_namespaces     # a list
        man.online_whitelist_wildcard_flag  # 'open' or 'blocking'

    """
    START = "CACHE MANIFEST"

    def __init__(self, env):
        self.env = env
        self.url = None
        self.explicit_urls = []
        self.fallbacks = {}
        self.online_whitelist_namespaces = []
        self.online_whitelist_wildcard_flag = 'blocking'

    def resolve(self, url):
        newurl, frag = split_fragment(resolve(self.url, url))
        if frag:
            self.env.logger.warning("Fragment ignored: %s" % url)
        return newurl

    def open(self, url):
        # parsing rules: http://www.w3.org/TR/html5/offline.html#manifests
        # ignored: utf-8 encoding, and BOM.
        # ignored: https and same-origin policy
        self.url = url
        data = self.env.fetch_url(self.url, "manifest", content_type="text/cache-manifest")
        if data is None:
            self.env.logger.error("Couldn't fetch manifest")
            return
        lines = data.splitlines() 
        first_line = lines[0] + "\n"
        if (not first_line.startswith(self.START)) or (first_line[len(self.START)] not in " \t\n\r"):
            self.env.logger.error("First line of manifest is incorrect: %r" % first_line[:-1])

        mode = 'explicit'

        for original_line in lines[1:]:
            line = original_line.strip()
            if not line or line[0] == '#':
                pass
            elif line == 'CACHE:':
                mode = 'explicit'
            elif line == 'FALLBACK:':
                mode = 'fallback'
            elif line == 'NETWORK:':
                mode = "online whitelist"
            elif line.endswith(':'):
                self.env.logger.warning("Entering 'unknown' mode: %r" % original_line)
                mode = "unknown"
            else:
                tokens = line.split()
                if mode == 'explicit':
                    self.explicit_urls.append(self.resolve(tokens[0]))
                    if len(tokens) > 1:
                        self.env.logger.warning("Extra data ignored: %r" % original_line)
                elif mode == 'fallback':
                    u1 = self.resolve(tokens[0])
                    u2 = self.resolve(tokens[1])
                    if u1 not in self.fallbacks:
                        self.fallbacks[u1] = u2
                    else:
                        self.env.logger.warning("Duplicate fallback entry ignored: %r" % original_line)
                    if len(tokens) > 2:
                        self.env.logger.warning("Extra data ignored: %r" % original_line)
                elif mode == 'online whitelist':
                    if tokens[0] == "*":
                        self.online_whitelist_wildcard_flag = 'open'
                    else:
                        self.online_whitelist_namespaces.append(self.resolve(tokens[0]))
                    if len(tokens) > 1:
                        self.env.logger.warning("Extra data ignored: %r" % original_line)
                else:
                    assert mode == 'unknown'
                    self.env.logger.warning("Line ignored in 'unknown' mode: %r" % original_line)

    def verify(self):
        """Verify that the manifest follows the rules for manifests."""
        # Examine the manifest: everything it mentions must exist.
        for url in self.explicit_urls:
            self.env.fetch_url(url, "cachable resource")
        for url in self.fallbacks.itervalues():
            self.env.fetch_url(url, "fallback resource")

    def matches_online_whitelist(self, url):
        """Determines if `url` is matched by something on the online whitelist"""
        for prefix in self.online_whitelist_namespaces:
            if url.startswith(prefix):
                return True
        return False
