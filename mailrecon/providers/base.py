"""Provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..types import ValidationStatus


class Provider(ABC):
    """Base class for provider-specific validation strategies."""

    @classmethod
    @abstractmethod
    def supports(cls, email: str) -> bool:
        """Return True when the provider can validate the email."""

    @abstractmethod
    def validate(self, email: str) -> ValidationStatus:
        """Validate the email address."""
