from unittest.mock import Mock, patch

from mailrecon.providers.gmail import GmailProvider


def _provider_with_smtp(rcpt_result=None, side_effect=None):
    provider = GmailProvider()
    smtp = Mock()
    smtp.connect.return_value = (220, b"ok")
    smtp.helo.return_value = (250, b"ok")
    smtp.mail.return_value = (250, b"ok")
    smtp.quit.return_value = None
    if side_effect is not None:
        smtp.rcpt.side_effect = side_effect
    else:
        smtp.rcpt.return_value = rcpt_result
    return provider, smtp


def test_gmail_exists():
    provider, smtp = _provider_with_smtp(rcpt_result=(250, b"exists"))

    with patch("mailrecon.providers.gmail.random.choice", return_value="gmail-smtp-in.l.google.com"), patch(
        "mailrecon.providers.gmail.smtplib.SMTP", return_value=smtp
    ):
        assert provider.validate("user@gmail.com") == "exists"


def test_gmail_does_not_exist():
    provider, smtp = _provider_with_smtp(rcpt_result=(550, b"nope"))

    with patch("mailrecon.providers.gmail.random.choice", return_value="gmail-smtp-in.l.google.com"), patch(
        "mailrecon.providers.gmail.smtplib.SMTP", return_value=smtp
    ):
        assert provider.validate("user@gmail.com") == "does_not_exist"


def test_gmail_unknown_status():
    provider, smtp = _provider_with_smtp(rcpt_result=(451, b"try again"))

    with patch("mailrecon.providers.gmail.random.choice", return_value="gmail-smtp-in.l.google.com"), patch(
        "mailrecon.providers.gmail.smtplib.SMTP", return_value=smtp
    ):
        assert provider.validate("user@gmail.com") == "unknown"


def test_gmail_failure_is_unknown():
    provider = GmailProvider()

    with patch("mailrecon.providers.gmail.random.choice", return_value="gmail-smtp-in.l.google.com"), patch(
        "mailrecon.providers.gmail.smtplib.SMTP", side_effect=OSError("boom")
    ):
        assert provider.validate("user@gmail.com") == "unknown"
