import posixpath
from urllib.parse import urljoin, urlparse


def extend_url(base, path):
    url_parsed = urlparse(base)
    # append should not overwrite a path on the base (example: google.com/nl)
    if path[0] == "/":
        sanitized_path = path[1:]
    else:
        sanitized_path = path
    return urljoin(url_parsed.geturl(), posixpath.join(url_parsed.path, sanitized_path))


def join_urlpath(url, urlpath=None):
    if urlpath is None:
        return url
    elif urlpath == "/":
        return url + "/"
    else:
        return extend_url(url, urlpath)
