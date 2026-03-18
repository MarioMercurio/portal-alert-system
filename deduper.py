import json
import os
import hashlib
from datetime import datetime, timezone

SEEN_FILE = "seen_tweets.json"


def _empty_store():
    return {
        "tweet_ids": [],
        "text_hashes": [],
        "alert_keys": []
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


def _today_key():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def build_alert_key(player_name, reporter, school=""):
    player = _normalize_name(player_name)
    reporter = _normalize_name(reporter)
    school = _normalize_name(school)
    day_key = _today_key()
    raw = f"{player}|{reporter}|{school}|{day_key}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


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
            "alert_keys": data.get("alert_keys", [])
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
    alert_key = build_alert_key(player_name, reporter, school)
    return alert_key in seen_data["alert_keys"]


def mark_alert_seen(player_name, reporter, school, seen_data):
    alert_key = build_alert_key(player_name, reporter, school)

    if alert_key not in seen_data["alert_keys"]:
        seen_data["alert_keys"].append(alert_key)

    save_seen(seen_data)
