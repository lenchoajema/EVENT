import os

# DEV_MODE controls whether endpoints use lightweight fallbacks when
# infrastructure (Postgres, MQTT) is unavailable. Default `True` so
# developer and CI environments remain tolerant. Set `DEV_MODE=false`
# in production to enforce strict behavior.
DEV_MODE = os.getenv("DEV_MODE", "true").lower() in ("1", "true", "yes")

def is_dev_mode() -> bool:
    return DEV_MODE
"""Application configuration helpers.

Provides a single `DEV_MODE` constant that other modules can import to
decide whether to enable development fallbacks (e.g. echo responses when
the database is unavailable). Controlled by the `DEV_MODE` environment
variable. Default: `true` to keep developer/test experience smooth; set
to `false` in production.
"""
import os


def _parse_bool(s: str) -> bool:
    return str(s).strip().lower() in ("1", "true", "yes", "on")


# Read once at import-time
DEV_MODE = _parse_bool(os.getenv("DEV_MODE", "true"))
