"""URL utilities."""

import urlparse

def same_origin(url1, url2):
    """Do `url1` and `url2` have the same origin?"""
    p1 = urlparse.urlparse(url1)
    p2 = urlparse.urlparse(url2)
    return p1.scheme == p2.scheme and p1.netloc == p2.netloc

def same_resource(url1, url2):
    """Do `url1` and `url2` point to the same resource?"""
    p1 = urlparse.urlparse(url1)
    p2 = urlparse.urlparse(url2)
    return (
        p1.scheme == p2.scheme and p1.netloc == p2.netloc and
        p1.path == p2.path and p1.params == p2.params
    )

def resolve(base, url):
    """What is the full form of `url` if its base is `base`?"""
    return urlparse.urljoin(base, url)

def split_fragment(url):
    """Split `url` into the real URL and the fragment, and return the pair."""
    parts = urlparse.urlparse(url)
    scheme, netloc, path, params, query, fragment = parts[:6]
    return urlparse.urlunparse((scheme, netloc, path, params, query, '')), fragment
