from __future__ import annotations

from .base import SiteFlow
from .dantri.flow import DanTriFlow
from .happy_vietnam.flow import HappyVietnamFlow


_SITE_FLOWS: dict[str, SiteFlow] = {
    "dantri": DanTriFlow(),
    "happy_vietnam": HappyVietnamFlow(),
}


def get_site_flow(site_key: str) -> SiteFlow:
    normalized_key = site_key.strip().lower()
    try:
        return _SITE_FLOWS[normalized_key]
    except KeyError as exc:
        supported = ", ".join(sorted(_SITE_FLOWS))
        raise ValueError(f"Unsupported site '{site_key}'. Supported sites: {supported}") from exc
