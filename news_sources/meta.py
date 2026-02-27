import feedparser


def fetch_meta_news(limit=10):
    feed = feedparser.parse("https://engineering.fb.com/feed/")
    items = []
    for entry in feed.entries[:limit]:
        items.append({
            "title": entry.title,
            "url": entry.link,
            "created_at": entry.get("published", "")[:10],
        })
    return items
