import os

import pytest

if not os.getenv("MAILRECON_LIVE_TEST"):
    pytest.skip("Live tests disabled to prevent rate limiting", allow_module_level=True)

from mailrecon import validate


def test_live_validate_returns_status():
    email = os.getenv("MAILRECON_LIVE_EMAIL", "test@gmail.com")
    assert validate(email) in {"exists", "does_not_exist", "unknown"}
