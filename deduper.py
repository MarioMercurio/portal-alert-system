import json
import os
import hashlib

SEEN_FILE = "seen_tweets.json"


def _empty_store():
    return {
        "tweet_ids": [],
        "text_hashes": [],
        "alerts": {}
    }


def _normalize_text(text):
    text = (text or "").strip().lower()
    return " ".join(text.split())


def _hash_text(text):
    normalized = _normalize_text(text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _normalize_name(value):
    value = (value or "").strip().lower()
    return " ".join(value.split())


def load_seen():
    if not os.path.exists(SEEN_FILE):
        return _empty_store()

    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            return _empty_store()

        return {
            "tweet_ids": data.get("tweet_ids", []),
            "text_hashes": data.get("text_hashes", []),
            "alerts": data.get("alerts", {})
        }
    except Exception:
        return _empty_store()


def save_seen(seen_data):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(seen_data, f, indent=2)


def has_seen_tweet(tweet_id, tweet_text, seen_data):
    tweet_id = str(tweet_id or "").strip()
    text_hash = _hash_text(tweet_text)

    if tweet_id and tweet_id in seen_data["tweet_ids"]:
        return True

    if text_hash in seen_data["text_hashes"]:
        return True

    return False


def mark_tweet_seen(tweet_id, tweet_text, seen_data):
    tweet_id = str(tweet_id or "").strip()
    text_hash = _hash_text(tweet_text)

    if tweet_id and tweet_id not in seen_data["tweet_ids"]:
        seen_data["tweet_ids"].append(tweet_id)

    if text_hash not in seen_data["text_hashes"]:
        seen_data["text_hashes"].append(text_hash)

    save_seen(seen_data)


def has_seen_alert(player_name, reporter, school, seen_data):
    key = _normalize_name(player_name)
    if not key:
        return False
    return key in seen_data["alerts"]


def mark_alert_seen(player_name, reporter, school, seen_data):
    key = _normalize_name(player_name)
    if not key:
        return

    seen_data["alerts"][key] = True
    save_seen(seen_data)
