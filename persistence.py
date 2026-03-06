import json
import logging
import os
from datetime import datetime, timezone, timedelta
from huggingface_hub import hf_hub_download, upload_file

HF_DATASET_REPO = os.getenv("HF_DATASET_REPO")  # "hf-username/news-urls"
HF_TOKEN = os.getenv("HF_TOKEN")
RECENT_DAYS = 180
RECENT_FILE = "recent_urls.json"   # {url: date} — rolling 180 days, used for dedup
ALL_FILE = "all_urls.json"         # [{url, date}, ...] — append-only, full history


def _download(filename: str):
    try:
        path = hf_hub_download(
            repo_id=HF_DATASET_REPO,
            filename=filename,
            repo_type="dataset",
            force_download=True,
            token=HF_TOKEN,
        )
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        logging.warning(f"[persistence] failed to download {filename}: {e}, dedup skipped")
        return {} if filename == RECENT_FILE else []


def _upload(filename: str, data):
    try:
        upload_file(
            path_or_fileobj=json.dumps(data, ensure_ascii=False, indent=2).encode(),
            path_in_repo=filename,
            repo_id=HF_DATASET_REPO,
            repo_type="dataset",
            token=HF_TOKEN,
            commit_message=f"update {filename}",
        )
        logging.info(f"[persistence] uploaded {filename}")
    except Exception as e:
        logging.error(f"[persistence] failed to upload {filename}: {e}")


def load_recent_urls() -> set:
    if not HF_DATASET_REPO:
        logging.warning("[persistence] HF_DATASET_REPO not set, dedup skipped")
        return set()
    recent = _download(RECENT_FILE)
    cutoff = (datetime.now(timezone.utc) - timedelta(days=RECENT_DAYS)).strftime("%Y-%m-%d")
    seen = {url for url, date in recent.items() if date >= cutoff}
    logging.info(f"[persistence] loaded {len(seen)} seen URLs")
    return seen


def save_urls(items: list):
    if not HF_DATASET_REPO:
        logging.warning("[persistence] HF_DATASET_REPO not set, URLs not saved")
        return
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    new_urls = {item["url"] for item in items}

    # update recent_urls.json — rolling 180 days, preserve original date
    recent = _download(RECENT_FILE)
    for url in new_urls:
        if url not in recent:
            recent[url] = today
    cutoff = (datetime.now(timezone.utc) - timedelta(days=RECENT_DAYS)).strftime("%Y-%m-%d")
    recent = {url: date for url, date in recent.items() if date >= cutoff}
    _upload(RECENT_FILE, recent)

    # update all_urls.json — append only, no duplicates
    all_urls = _download(ALL_FILE)
    existing = {entry["url"] for entry in all_urls}
    all_urls.extend({"url": url, "date": today} for url in new_urls if url not in existing)
    _upload(ALL_FILE, all_urls)
