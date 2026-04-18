"""Provider registry."""

from .base import Provider
from .gmail import GmailProvider
from .yahoo import YahooProvider

__all__ = ["Provider", "GmailProvider", "YahooProvider"]
