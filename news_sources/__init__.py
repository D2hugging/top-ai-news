from config import CONFIG
from .base import NewsSource
from .hackernews import HackerNewsSource
from .google import GoogleNewsSource
from .meta import MetaNewsSource
from .nvidia import NvidiaNewsSource

REGISTRY: dict[str, NewsSource] = {
    src.name: src for src in [
        HackerNewsSource(),
        GoogleNewsSource(),
        MetaNewsSource(),
        NvidiaNewsSource(),
    ]
}


def fetch_all() -> list[dict]:
    sources_cfg = CONFIG.get("sources", {})
    items = []
    for name, source in REGISTRY.items():
        cfg = sources_cfg.get(name, {})
        if cfg.get("enabled", True):
            items += source.fetch(limit=cfg.get("limit", 10))
    return items
