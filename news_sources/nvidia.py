import feedparser
from .base import NewsSource


class NvidiaNewsSource(NewsSource):
    name = "nvidia"

    def fetch(self, limit=10):
        feed = feedparser.parse("https://developer.nvidia.com/blog/feed/")
        return [
            {"title": e.title, "url": e.link, "created_at": e.get("published", "")[:10]}
            for e in feed.entries[:limit]
        ]
