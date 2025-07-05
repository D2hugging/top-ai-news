import requests
from datetime import datetime, timezone
import concurrent.futures
import time

def fetch_hackernews(limit=10):
    top_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    item_url = "https://hacker-news.firebaseio.com/v0/item/{}.json"

    try:
        ids = requests.get(top_url).json()[:limit]
    except Exception as e:
        print("⚠️ 获取热门故事 ID 失败:", e)
        return []

    def get_story(story_id):
        try:
            res = requests.get(item_url.format(story_id)).json()
            title = res.get("title", "Untitled")
            url = res.get("url") or f"https://news.ycombinator.com/item?id={story_id}"
            score = res.get("score", 0)
            ts = res.get("time", 0)
            dt = datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d")
            return {
                "title": title,
                "url": url,
                "points": score,
                "created_at": dt
            }
        except Exception as e:
            return None

    items = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for story in executor.map(get_story, ids):
            if story: items.append(story)

    return items