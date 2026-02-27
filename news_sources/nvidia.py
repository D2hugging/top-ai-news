import feedparser


def fetch_nvidia_news(limit=10):
    feed = feedparser.parse("https://developer.nvidia.com/blog/feed/")
    items = []
    for entry in feed.entries[:limit]:
        items.append({
            "title": entry.title,
            "url": entry.link,
            "created_at": entry.get("published", "")[:10],
        })
    return items
