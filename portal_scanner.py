import json
import os
import re
import time
from datetime import datetime, timezone

from twitter_monitor import search_portal_tweets
from tweet_parser import extract_player_name
from superfile_loader import load_superfile, find_player
from sms_alerts import send_portal_alert

STATE_FILE = "seen_tweets.json"
POLL_SECONDS = 45

PORTAL_PHRASES = [
    "entered the transfer portal",
    "has entered the transfer portal",
    "plans to enter the transfer portal",
    "is entering the transfer portal",
    "in the transfer portal",
]

MEN_BASKETBALL_HINTS = [
    "men's basketball",
    "mens basketball",
    "mbb",
    "guard",
    "forward",
    "center",
    "hoops",
    "basketball",
]


def load_seen_tweets():
    if not os.path.exists(STATE_FILE):
        return set()

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return set(data)
    except Exception:
        return set()


def save_seen_tweets(seen_ids):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(list(seen_ids)), f, indent=2)


def normalize_text(text):
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def looks_like_mens_basketball(tweet_text, author_name="", author_username=""):
    blob = " ".join([
        tweet_text or "",
        author_name or "",
        author_username or "",
    ]).lower()

    return any(hint in blob for hint in MEN_BASKETBALL_HINTS)


def get_hdi_emoji(hdi_value):
    try:
        hdi = float(hdi_value)
    except Exception:
        return ""

    if hdi >= 90:
        return " 💰"
    if hdi >= 85:
        return " 🧨"
    if hdi >= 80:
        return " 🔥"
    return ""


def build_report_url(player_row):
    """
    Placeholder.
    Replace this once your report generator is wired in.
    """
    player_name = str(player_row.get("Full Name", "")).strip()
    school = str(player_row.get("2025-2026 School", "")).strip()

    safe_player = re.sub(r"[^a-z0-9]+", "_", player_name.lower()).strip("_")
    safe_school = re.sub(r"[^a-z0-9]+", "_", school.lower()).strip("_")

    return f"https://myportalapp.com/reports/{safe_player}_{safe_school}.png"


def process_tweet(tweet, superfile_df, seen_ids):
    tweet_id = str(tweet.get("id", "")).strip()
    tweet_text = tweet.get("text", "") or ""
    author_name = tweet.get("author_name", "") or ""
    author_username = tweet.get("author_username", "") or ""

    if not tweet_id or tweet_id in seen_ids:
        return None

    text_norm = normalize_text(tweet_text)

    if not any(phrase in text_norm for phrase in PORTAL_PHRASES):
        return None

    if not looks_like_mens_basketball(tweet_text, author_name, author_username):
        return None

    player_name = extract_player_name(tweet_text)
    if not player_name:
        return None

    player_row = find_player(superfile_df, player_name)
    if not player_row:
        return {
            "status": "unmatched",
            "tweet_id": tweet_id,
            "tweet_text": tweet_text,
            "player_name": player_name,
        }

    school = str(player_row.get("2025-2026 School", "")).strip()
    hdi = player_row.get("RATING", "")
    emoji = get_hdi_emoji(hdi)

    tweet_url = f"https://x.com/{author_username}/status/{tweet_id}" if author_username else ""
    report_url = build_report_url(player_row)

    alert_text = (
        "🚨 Portal Entry\n\n"
        f"{player_name} – {school}\n"
        f"HDI: {hdi}{emoji}\n\n"
        f"Reported by: @{author_username}\n\n"
        f"Tweet:\n{tweet_url}\n\n"
        f"Report:\n{report_url}"
    )

    send_portal_alert(alert_text)

    return {
        "status": "alert_sent",
        "tweet_id": tweet_id,
        "player_name": player_name,
        "school": school,
        "hdi": hdi,
        "tweet_url": tweet_url,
        "report_url": report_url,
    }


def run_scanner():
    print("Loading SuperFile...")
    superfile_df = load_superfile()

    print("Loading seen tweet cache...")
    seen_ids = load_seen_tweets()

    print(f"Scanner started. Polling every {POLL_SECONDS} seconds.")

    while True:
        try:
            tweets = search_portal_tweets()

            if not tweets:
                print(f"[{datetime.now().isoformat()}] No tweets found.")
            else:
                print(f"[{datetime.now().isoformat()}] Found {len(tweets)} candidate tweets.")

            for tweet in tweets:
                result = process_tweet(tweet, superfile_df, seen_ids)

                if result:
                    tweet_id = result["tweet_id"]
                    seen_ids.add(tweet_id)
                    save_seen_tweets(seen_ids)
                    print(result)

        except Exception as e:
            print(f"[ERROR] {e}")

        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    run_scanner()
