import streamlit as st
import requests
from tweet_parser import extract_player_name
from superfile_loader import load_superfile, find_player
from format_alert import format_portal_alert
from email_sender import send_email_alert
from portal_rules import is_likely_portal_tweet
from deduper import (
    load_seen,
    has_seen_tweet,
    mark_tweet_seen,
    has_seen_alert,
    mark_alert_seen,
)

USER_LOOKUP_URL = "https://api.twitter.com/2/users/by/username/{username}"
USER_TWEETS_URL = "https://api.twitter.com/2/users/{user_id}/tweets"

REPORTERS = [
    "GoodmanHoops",
    "jeffborzello",
    "TiptonEdits",
    "VerbalCommits",
    "On3sports",
]


def get_headers():
    return {
        "Authorization": f"Bearer {st.secrets['X_BEARER_TOKEN']}"
    }


def lookup_user(username):
    url = USER_LOOKUP_URL.format(username=username)
    response = requests.get(url, headers=get_headers())

    if response.status_code != 200:
        return {
            "ok": False,
            "status_code": response.status_code,
            "error_text": response.text,
            "user_id": None,
        }

    data = response.json()
    user_id = data.get("data", {}).get("id")

    return {
        "ok": True,
        "status_code": 200,
        "error_text": "",
        "user_id": user_id,
    }


def get_recent_tweets_for_user(user_id, max_results=10):
    url = USER_TWEETS_URL.format(user_id=user_id)

    params = {
        "max_results": max_results,
        "tweet.fields": "created_at,lang"
    }

    response = requests.get(url, headers=get_headers(), params=params)

    if response.status_code != 200:
        return {
            "ok": False,
            "status_code": response.status_code,
            "error_text": response.text,
            "tweets": []
        }

    data = response.json()

    return {
        "ok": True,
        "status_code": 200,
        "error_text": "",
        "tweets": data.get("data", [])
    }


def process_tweets(debug=False):
    df = load_superfile()
    seen_data = load_seen()

    alerts_sent = []
    debug_log = []

    for username in REPORTERS:
        lookup = lookup_user(username)

        if not lookup["ok"]:
            debug_log.append({
                "text": f"User lookup failed for @{username}",
                "score": 0,
                "likely": False,
                "player_name": "",
                "player_found": False,
                "reasons": [f"lookup_api_error_{lookup['status_code']}"],
                "api_status_code": lookup["status_code"],
                "api_error_text": lookup["error_text"]
            })
            continue

        user_id = lookup["user_id"]

        timeline = get_recent_tweets_for_user(user_id, max_results=10)

        if not timeline["ok"]:
            debug_log.append({
                "text": f"Timeline failed for @{username}",
                "score": 0,
                "likely": False,
                "player_name": "",
                "player_found": False,
                "reasons": [f"timeline_api_error_{timeline['status_code']}"],
                "api_status_code": timeline["status_code"],
                "api_error_text": timeline["error_text"]
            })
            continue

        tweets = timeline["tweets"]

        if not tweets:
            debug_log.append({
                "text": f"No tweets returned for @{username}",
                "score": 0,
                "likely": False,
                "player_name": "",
                "player_found": False,
                "reasons": ["no_tweets_returned"],
                "api_status_code": 200,
                "api_error_text": ""
            })
            continue

        for tweet in tweets:
            tweet_id = str(tweet.get("id", "")).strip()
            text = tweet.get("text", "")
            lang = tweet.get("lang", "")

            if not tweet_id or not text:
                continue

            if has_seen_tweet(tweet_id, text, seen_data):
                debug_log.append({
                    "text": text,
                    "score": 0,
                    "likely": False,
                    "player_name": "",
                    "player_found": False,
                    "reasons": ["duplicate_tweet_seen"],
                    "api_status_code": 200,
                    "api_error_text": ""
                })
                continue

            likely, score, reasons = is_likely_portal_tweet(
                tweet_text=text,
                author_username=username,
                author_name=username
            )

            player_name = extract_player_name(text)
            player = find_player(df, player_name) if player_name else None
            player_data = player.to_dict() if player is not None else None

            school = ""
            if player_data is not None:
                school = player_data.get("2025-2026 School", "")

            debug_log.append({
                "text": text,
                "score": score,
                "likely": likely,
                "player_name": player_name,
                "player_found": player is not None,
                "reasons": reasons + ([f"lang_{lang}"] if lang else []),
                "api_status_code": 200,
                "api_error_text": ""
            })

            if lang != "en":
                mark_tweet_seen(tweet_id, text, seen_data)
                continue

            if not likely:
                mark_tweet_seen(tweet_id, text, seen_data)
                continue

            if not player_name:
                mark_tweet_seen(tweet_id, text, seen_data)
                continue

            if player is None:
                mark_tweet_seen(tweet_id, text, seen_data)
                continue

            if has_seen_alert(player_name, username, school, seen_data):
                debug_log.append({
                    "text": text,
                    "score": score,
                    "likely": likely,
                    "player_name": player_name,
                    "player_found": True,
                    "reasons": ["duplicate_alert_seen_same_day"],
                    "api_status_code": 200,
                    "api_error_text": ""
                })
                mark_tweet_seen(tweet_id, text, seen_data)
                continue

            subject, body = format_portal_alert(
                player_name=player_data.get("Full Name", player_name),
                school=school,
                hdi=player_data.get("RATING", ""),
                reporter=username,
                tweet_url=f"https://x.com/{username}/status/{tweet_id}",
                report_url="https://portalapp.com/reports/example.png"
            )

            send_email_alert(subject, body)

            mark_tweet_seen(tweet_id, text, seen_data)
            mark_alert_seen(player_data.get("Full Name", player_name), username, school, seen_data)

            alerts_sent.append({
                "player": player_data.get("Full Name", player_name),
                "score": score,
                "text": text
            })

    if debug:
        return alerts_sent, debug_log

    return alerts_sent
