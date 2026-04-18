import mailrecon.core as core


class FakeYahooProvider:
    created = 0
    validated = []

    @classmethod
    def supports(cls, email: str) -> bool:
        return email.endswith("@yahoo.com")

    def __init__(self) -> None:
        type(self).created += 1

    def validate(self, email: str) -> str:
        type(self).validated.append(email)
        return "exists"


class FakeGmailProvider:
    created = 0
    validated = []

    @classmethod
    def supports(cls, email: str) -> bool:
        return email.endswith("@gmail.com")

    def __init__(self) -> None:
        type(self).created += 1

    def validate(self, email: str) -> str:
        type(self).validated.append(email)
        return "does_not_exist"


def test_routes_yahoo_email(monkeypatch):
    FakeYahooProvider.created = 0
    FakeYahooProvider.validated = []
    FakeGmailProvider.created = 0
    FakeGmailProvider.validated = []
    monkeypatch.setattr(core, "YahooProvider", FakeYahooProvider)
    monkeypatch.setattr(core, "GmailProvider", FakeGmailProvider)
    monkeypatch.setattr(core, "PROVIDERS", (FakeYahooProvider, FakeGmailProvider))

    assert core.validate("user@yahoo.com") == "exists"
    assert FakeYahooProvider.created == 1
    assert FakeYahooProvider.validated == ["user@yahoo.com"]
    assert FakeGmailProvider.created == 0


def test_routes_gmail_email(monkeypatch):
    FakeYahooProvider.created = 0
    FakeYahooProvider.validated = []
    FakeGmailProvider.created = 0
    FakeGmailProvider.validated = []
    monkeypatch.setattr(core, "YahooProvider", FakeYahooProvider)
    monkeypatch.setattr(core, "GmailProvider", FakeGmailProvider)
    monkeypatch.setattr(core, "PROVIDERS", (FakeYahooProvider, FakeGmailProvider))

    assert core.validate("user@gmail.com") == "does_not_exist"
    assert FakeGmailProvider.created == 1
    assert FakeGmailProvider.validated == ["user@gmail.com"]


def test_unknown_domain_returns_unknown(monkeypatch):
    FakeYahooProvider.created = 0
    FakeYahooProvider.validated = []
    FakeGmailProvider.created = 0
    FakeGmailProvider.validated = []
    monkeypatch.setattr(core, "YahooProvider", FakeYahooProvider)
    monkeypatch.setattr(core, "GmailProvider", FakeGmailProvider)
    monkeypatch.setattr(core, "PROVIDERS", (FakeYahooProvider, FakeGmailProvider))

    assert core.validate("user@example.com") == "unknown"
