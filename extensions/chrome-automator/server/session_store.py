"""
session_store.py — Save and load Playwright browser cookies from Chrome extension captures.
Cookies are stored as JSON files in recordings/sessions/.
"""

import json
import logging
from pathlib import Path

log = logging.getLogger("session_store")
SESSIONS_DIR = Path(__file__).parent.parent / "recordings" / "sessions"
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


def save_session_cookies(platform: str, cookies: list[dict]):
    """Save cookies captured by the Chrome extension."""
    # Convert Chrome extension cookie format to Playwright format
    pw_cookies = []
    for c in cookies:
        pw_cookie = {
            "name": c.get("name", ""),
            "value": c.get("value", ""),
            "domain": c.get("domain", ""),
            "path": c.get("path", "/"),
            "secure": c.get("secure", False),
            "httpOnly": c.get("httpOnly", False),
        }
        if c.get("expirationDate"):
            pw_cookie["expires"] = int(c["expirationDate"])
        if c.get("sameSite"):
            # Chrome uses "no_restriction", "lax", "strict", "unspecified"
            same_site_map = {"no_restriction": "None", "lax": "Lax", "strict": "Strict", "unspecified": "None"}
            pw_cookie["sameSite"] = same_site_map.get(c["sameSite"].lower(), "Lax")
        pw_cookies.append(pw_cookie)

    out_path = SESSIONS_DIR / f"{platform}.json"
    out_path.write_text(json.dumps(pw_cookies, indent=2), encoding="utf-8")
    log.info("Saved %d cookies for %s → %s", len(pw_cookies), platform, out_path)


def load_cookies(platform: str) -> list[dict]:
    """Load Playwright-format cookies for a platform."""
    cookie_path = SESSIONS_DIR / f"{platform}.json"
    if not cookie_path.exists():
        return []
    try:
        return json.loads(cookie_path.read_text(encoding="utf-8"))
    except Exception as e:
        log.error("Failed to load cookies for %s: %s", platform, e)
        return []
