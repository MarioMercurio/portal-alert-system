import json
import os

SEEN_FILE = "seen_tweets.json"


def load_seen():
    if not os.path.exists(SEEN_FILE):
        return set()

    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return set(str(x) for x in data)
    except Exception:
        return set()


def save_seen(seen_ids):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(list(seen_ids)), f)


def is_new_tweet(tweet_id, seen_ids):
    return str(tweet_id) not in seen_ids


def mark_tweet_seen(tweet_id, seen_ids):
    seen_ids.add(str(tweet_id))
    save_seen(seen_ids)
