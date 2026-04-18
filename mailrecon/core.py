"""Public validation entrypoint."""

from __future__ import annotations

from .providers import GmailProvider, YahooProvider, Provider
from .types import ValidationStatus

PROVIDERS: tuple[type[Provider], ...] = (GmailProvider, YahooProvider)


def _normalize_email(email: str) -> str:
    return email.strip()


def _select_provider(email: str) -> Provider | None:
    for provider_cls in PROVIDERS:
        if provider_cls.supports(email):
            return provider_cls()
    return None


def validate(email: str) -> ValidationStatus:
    """
    Returns:
        "exists"
        "does_not_exist"
        "unknown"
    """
    normalized = _normalize_email(email)
    if "@" not in normalized:
        return "unknown"

    provider = _select_provider(normalized)
    if provider is None:
        return "unknown"
    return provider.validate(normalized)
