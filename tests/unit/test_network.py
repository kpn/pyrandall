from pyrandall.network import join_urlpath


def test_urljoin_accepts_none():
    url = "http://localhost.com/foo"
    result = join_urlpath(url, None)
    assert "http://localhost.com/foo" == result


def test_urljoin_append_slash():
    url = "http://localhost.com"
    result = join_urlpath(url, "/")
    assert "http://localhost.com/" == result


def test_urljoin_joins_two_paths():
    url = "http://localhost.com/foo"
    result = join_urlpath(url, "/bar")
    assert "http://localhost.com/foo/bar" == result


def test_urljoin_avoids_double_slashes():
    url = "http://localhost.com/foo/"
    result = join_urlpath(url, "/bar")
    assert "http://localhost.com/foo/bar" == result
