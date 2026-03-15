import requests
import concurrent.futures
from datetime import datetime, timezone
from .base import NewsSource


class HackerNewsSource(NewsSource):
    name = "hackernews"

    def fetch(self, limit=10):
        top_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        item_url = "https://hacker-news.firebaseio.com/v0/item/{}.json"

        try:
            ids = requests.get(top_url).json()[:limit]
        except Exception as e:
            print("failed to fetch top stories:", e)
            return []

        def get_story(story_id):
            try:
                res = requests.get(item_url.format(story_id)).json()
                ts = res.get("time", 0)
                return {
                    "title": res.get("title", "Untitled"),
                    "url": res.get("url") or f"https://news.ycombinator.com/item?id={story_id}",
                    "points": res.get("score", 0),
                    "created_at": datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d"),
                }
            except Exception:
                return None

        with concurrent.futures.ThreadPoolExecutor() as executor:
            return [s for s in executor.map(get_story, ids) if s]
