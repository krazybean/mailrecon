"""Shared types for mailrecon."""

from typing import Literal

ValidationStatus = Literal["exists", "does_not_exist", "unknown"]
