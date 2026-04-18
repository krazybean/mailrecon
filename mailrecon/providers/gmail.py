"""Gmail validation strategy."""

from __future__ import annotations

import random
import smtplib
from contextlib import suppress

from .base import Provider
from ..types import ValidationStatus


class GmailProvider(Provider):
    """Validate Gmail mailbox existence via SMTP RCPT probing."""

    smtp_hosts = (
        "gmail-smtp-in.l.google.com",
        "alt1.gmail-smtp-in.l.google.com",
        "alt2.gmail-smtp-in.l.google.com",
        "alt3.gmail-smtp-in.l.google.com",
        "alt4.gmail-smtp-in.l.google.com",
    )
    sender = "example@codecult.io"

    @classmethod
    def supports(cls, email: str) -> bool:
        domain = email.rsplit("@", 1)[-1].lower()
        return domain in {"gmail.com", "googlemail.com"}

    def validate(self, email: str) -> ValidationStatus:
        host = random.choice(self.smtp_hosts)
        smtp = smtplib.SMTP(timeout=10)
        try:
            smtp.connect(host)
            smtp.helo("codecult.io")
            smtp.mail(self.sender)
            code, _ = smtp.rcpt(email)
        except (OSError, smtplib.SMTPException):
            return "unknown"
        finally:
            with suppress(Exception):
                smtp.quit()

        if 200 <= code <= 299:
            return "exists"
        if 500 <= code <= 599:
            return "does_not_exist"
        return "unknown"
