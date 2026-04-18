import http.cookiejar
from unittest.mock import Mock, patch

from mailrecon.providers.yahoo import YahooProvider


def _cookiejar_with_crumb(value: str = "crumb") -> http.cookiejar.CookieJar:
    jar = http.cookiejar.CookieJar()
    cookie = http.cookiejar.Cookie(
        version=0,
        name="AS",
        value=f"s={value}",
        port=None,
        port_specified=False,
        domain="login.yahoo.com",
        domain_specified=False,
        domain_initial_dot=False,
        path="/",
        path_specified=True,
        secure=False,
        expires=None,
        discard=True,
        comment=None,
        comment_url=None,
        rest={},
        rfc2109=False,
    )
    jar.set_cookie(cookie)
    return jar


class FakeResponse:
    def __init__(self, status_code: int, text: str = "", cookies: http.cookiejar.CookieJar | None = None):
        self.status_code = status_code
        self.text = text
        self.cookies = cookies or http.cookiejar.CookieJar()

    def json(self):
        import json

        return json.loads(self.text)


def test_yahoo_exists():
    provider = YahooProvider()
    get_response = FakeResponse(200, cookies=_cookiejar_with_crumb())
    post_response = FakeResponse(200, '{"errors":[{"name":"userId","error":"IDENTIFIER_EXISTS"}]}')

    with patch("mailrecon.providers.yahoo.requests.get", return_value=get_response) as mock_get, patch(
        "mailrecon.providers.yahoo.requests.post", return_value=post_response
    ) as mock_post:
        assert provider.validate("user@yahoo.com") == "exists"
        assert mock_get.called
        assert mock_post.called


def test_yahoo_does_not_exist():
    provider = YahooProvider()
    get_response = FakeResponse(200, cookies=_cookiejar_with_crumb())
    post_response = FakeResponse(200, '{"errors":[{"name":"userId","error":"SOMETHING_ELSE"}]}')

    with patch("mailrecon.providers.yahoo.requests.get", return_value=get_response), patch(
        "mailrecon.providers.yahoo.requests.post", return_value=post_response
    ):
        assert provider.validate("user@yahoo.com") == "does_not_exist"


def test_yahoo_malformed_response_is_unknown():
    provider = YahooProvider()
    get_response = FakeResponse(200, cookies=_cookiejar_with_crumb())
    post_response = FakeResponse(200, "not-json")

    with patch("mailrecon.providers.yahoo.requests.get", return_value=get_response), patch(
        "mailrecon.providers.yahoo.requests.post", return_value=post_response
    ):
        assert provider.validate("user@yahoo.com") == "unknown"


def test_yahoo_http_failure_is_unknown():
    provider = YahooProvider()

    with patch("mailrecon.providers.yahoo.requests.get", side_effect=OSError("boom")):
        assert provider.validate("user@yahoo.com") == "unknown"


def test_yahoo_post_failure_is_unknown():
    provider = YahooProvider()
    get_response = FakeResponse(200, cookies=_cookiejar_with_crumb())

    with patch("mailrecon.providers.yahoo.requests.get", return_value=get_response), patch(
        "mailrecon.providers.yahoo.requests.post", side_effect=OSError("boom")
    ):
        assert provider.validate("user@yahoo.com") == "unknown"
