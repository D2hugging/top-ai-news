import feedparser
from .base import NewsSource


class GoogleNewsSource(NewsSource):
    name = "google"

    def fetch(self, limit=10):
        feed = feedparser.parse("https://blog.google/technology/ai/rss/")
        return [
            {"title": e.title, "url": e.link, "created_at": e.get("published", "")[:10]}
            for e in feed.entries[:limit]
        ]
