import feedparser
from .base import NewsSource


class MetaNewsSource(NewsSource):
    name = "meta"

    def fetch(self, limit=10):
        feed = feedparser.parse("https://engineering.fb.com/feed/")
        return [
            {"title": e.title, "url": e.link, "created_at": e.get("published", "")[:10]}
            for e in feed.entries[:limit]
        ]
