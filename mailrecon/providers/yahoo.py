"""Yahoo validation strategy."""

from __future__ import annotations

import os
import json
import time
import traceback
from typing import Any
from urllib import parse

try:
    from curl_cffi import requests  # type: ignore[import-not-found]
    _USE_CURL_CFFI = True
except ImportError:  # pragma: no cover - local safety fallback
    import requests  # type: ignore[no-redef]

    _USE_CURL_CFFI = False

from .base import Provider
from ..types import ValidationStatus


class YahooProvider(Provider):
    """Validate Yahoo mailbox existence through Yahoo signup validation."""

    bootstrap_url = "https://login.yahoo.com/account/create"
    url = "https://login.yahoo.com/account/module/create?validateField=userId"

    headers = {
        "origin": "https://login.yahoo.com",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "user-agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/63.0.3239.108 Safari/537.36"
        ),
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "accept": "*/*",
        "referer": "https://login.yahoo.com/account/create",
        "authority": "login.yahoo.com",
        "x-requested-with": "XMLHttpRequest",
    }

    def __init__(self) -> None:
        if _USE_CURL_CFFI:
            self.session = requests.Session(impersonate="chrome124")
        else:  # pragma: no cover - fallback only for environments without curl_cffi
            self.session = requests.Session()
        self.debug = os.getenv("MAILRECON_DEBUG") == "1"

    @classmethod
    def supports(cls, email: str) -> bool:
        domain = email.rsplit("@", 1)[-1].lower()
        return domain == "yahoo.com"

    @staticmethod
    def _local_part(email: str) -> str:
        return email.split("@", 1)[0]

    @staticmethod
    def _valid_response(status_code: int) -> bool:
        return 200 <= status_code <= 299

    @staticmethod
    def _extract_crumb(cookies):
        """
        Extract Yahoo crumb from cookies (curl_cffi compatible)
        """

        if not cookies:
            return None

        as_cookie = None
        try:
            as_cookie = cookies.get("AS")
        except Exception:
            for cookie in cookies:
                if getattr(cookie, "name", None) == "AS":
                    as_cookie = getattr(cookie, "value", None)
                    break

        if not as_cookie:
            return None

        for data in as_cookie.split("&"):
            if data.startswith("s="):
                return data[len("s=") :]
        return None

    @staticmethod
    def _reshape_cookie(cookies):
        if not cookies:
            return ""

        return "; ".join(f"{k}={v}" for k, v in cookies.items())

    @staticmethod
    def _browser_fp_data() -> dict[str, Any]:
        now = int(time.time())
        return {
            "language": "en-US",
            "colorDepth": 24,
            "deviceMemory": 8,
            "pixelRatio": 2,
            "hardwareConcurrency": 8,
            "resolution": {"w": 1440, "h": 900},
            "availableResolution": {"w": 1440, "h": 846},
            "timezoneOffset": 300,
            "timezone": "America/Chicago",
            "sessionStorage": 1,
            "localStorage": 1,
            "indexedDb": 1,
            "openDatabase": 1,
            "cpuClass": "unknown",
            "platform": "MacIntel",
            "doNotTrack": 1,
            "canvas": "canvas winding:yes~canvas",
            "webgl": 1,
            "webglVendorAndRenderer": (
                "Google Inc. (ATI Technologies Inc.)~"
                "ANGLE (ATI Technologies Inc., AMD Radeon Pro 555 OpenGL Engine, OpenGL 4.1)"
            ),
            "adblock": 0,
            "hasLiedLanguages": 0,
            "hasLiedResolution": 0,
            "hasLiedOs": 0,
            "hasLiedBrowser": 0,
            "touch_support": {"points": 0, "event": 0, "start": 0},
            "plugins": {"count": 0, "hash": "24700f9f1986800ab4fcc880530dd0ed"},
            "fonts": {"count": 27, "hash": "d52a1516cfb5f1c2d8a427c14bc3645f"},
            "audio": "124.04347657808103",
            "ts": {"serve": now, "render": now + 10},
        }

    def _payload(self, email: str, acrumb: str | None) -> dict[str, Any]:
        local_part = self._local_part(email)
        return {
            "browser-fp-data": self._browser_fp_data(),
            "specId": "yidregsimplified",
            "cacheStored": "true",
            "crumb": "QFM5cNikkUV",
            "acrumb": acrumb or "",
            "sessionIndex": "QQ--",
            "done": "https%3A%2F%2Fwww.yahoo.com",
            "attrSetIndex": 0,
            "googleIdToken": "",
            "authCode": "",
            "tos0": "oath_freereg|us|en-US",
            "firstName": "",
            "lastName": "",
            "userid-domain": "yahoo",
            "userId": local_part,
            "yidDomainDefault": "yahoo.com",
            "yidDomain": "yahoo.com",
            "password": "",
            "shortCountryCode": "US",
            "phone": "",
            "mm": "",
            "dd": "",
            "yyyy": "",
            "multiDomain": "",
            "signup": "",
            "freeformGender": "",
        }

    @staticmethod
    def _encode_payload(payload: dict[str, Any]) -> bytes:
        flattened = dict(payload)
        flattened["browser-fp-data"] = json.dumps(flattened["browser-fp-data"], separators=(",", ":"))
        return parse.urlencode(flattened).encode("utf-8")

    @staticmethod
    def _digest_response(data: dict[str, Any]) -> ValidationStatus:
        if not isinstance(data, dict):
            return "unknown"
        errors = data.get("errors")
        if not isinstance(errors, list):
            return "unknown"
        user_id_error_present = any(
            isinstance(error, dict) and error.get("name") == "userId"
            for error in errors
        )
        if user_id_error_present:
            return "exists"
        return "does_not_exist"

    def _debug_response(self, label: str, response: Any) -> None:
        if not self.debug:
            return
        print(f"=== {label} ===")
        print("STATUS:", response.status_code)
        print("HEADERS:", dict(response.headers))
        if hasattr(response, "cookies"):
            try:
                print("COOKIES:", response.cookies.get_dict())
            except Exception:
                print("COOKIES:", response.cookies)
        body = getattr(response, "text", "")
        print("BODY (first 300):", body[:300])

    def validate(self, email: str) -> ValidationStatus:
        try:
            if _USE_CURL_CFFI:
                response = self.session.get(self.bootstrap_url, impersonate="chrome")
            else:  # pragma: no cover - fallback only for environments without curl_cffi
                response = self.session.get(self.bootstrap_url)
            self._debug_response("INITIAL REQUEST", response)
            if not self._valid_response(response.status_code):
                return "unknown"

            acrumb = self._extract_crumb(response.cookies)
            if self.debug:
                try:
                    print("SESSION COOKIES:", response.cookies.get_dict())
                except Exception:
                    print("SESSION COOKIES:", response.cookies)

            headers = dict(self.headers)
            payload = self._payload(email, acrumb)
            req = self.session.post(
                self.url,
                headers=headers,
                data=self._encode_payload(payload)
            )
            self._debug_response("POST REQUEST", req)
            if not self._valid_response(req.status_code):
                return "unknown"
            return self._digest_response(req.json())

        except Exception as e:
            print("=== EXCEPTION ===")
            print(type(e).__name__, str(e))
            traceback.print_exc()
            return "unknown"
