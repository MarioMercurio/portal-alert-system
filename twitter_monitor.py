import streamlit as st
import requests
from tweet_parser import extract_player_name
from superfile_loader import load_superfile, find_player
from format_alert import format_portal_alert
from email_sender import send_email_alert
from portal_rules import is_likely_portal_tweet


USER_TWEETS_URL = "https://api.twitter.com/2/users/{user_id}/tweets"

REPORTERS = [
    {"username": "GoodmanHoops", "id": "17330792"},
    {"username": "jeffborzello", "id": "40235531"},
    {"username": "TiptonEdits", "id": "145602194"},
    {"username": "VerbalCommits", "id": "362586870"},
    {"username": "On3sports", "id": "149871064"},
]


def get_headers():
    return {
        "Authorization": f"Bearer {st.secrets['X_BEARER_TOKEN']}"
    }


def get_recent_tweets_for_user(user_id, max_results=25):
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

    alerts_sent = []
    debug_log = []

    for reporter in REPORTERS:
        username = reporter["username"]
        user_id = reporter["id"]

        result = get_recent_tweets_for_user(user_id, max_results=25)
        tweets = result["tweets"]

        if not result["ok"]:
            debug_log.append({
                "text": f"Twitter API error for @{username}",
                "score": 0,
                "likely": False,
                "player_name": "",
                "player_found": False,
                "reasons": [f"api_error_{result['status_code']}"],
                "api_status_code": result["status_code"],
                "api_error_text": result["error_text"]
            })
            continue

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

        debug_log.append({
            "text": f"Fetched {len(tweets)} raw tweets for @{username}",
            "score": 0,
            "likely": False,
            "player_name": "",
            "player_found": False,
            "reasons": ["raw_fetch_ok"],
            "api_status_code": 200,
            "api_error_text": ""
        })

        for tweet in tweets:
            text = tweet.get("text", "")
            lang = tweet.get("lang", "")

            if not text:
                continue

            reasons = []
            filtered_out = False

            if text.startswith("RT "):
                reasons.append("filtered_retweet")
                filtered_out = True

            if lang and lang != "en":
                reasons.append(f"filtered_lang_{lang}")
                filtered_out = True

            if "transfer portal" not in text.lower() and "portal" not in text.lower():
                reasons.append("filtered_no_portal_keyword")
                filtered_out = True

            likely, score, score_reasons = is_likely_portal_tweet(
                tweet_text=text,
                author_username=username,
                author_name=username
            )

            player_name = extract_player_name(text)
            player = find_player(df, player_name) if player_name else None

            all_reasons = reasons + score_reasons

            debug_log.append({
                "text": text,
                "score": score,
                "likely": likely and not filtered_out,
                "player_name": player_name,
                "player_found": player is not None,
                "reasons": all_reasons if all_reasons else ["passed_basic_checks"],
                "api_status_code": 200,
                "api_error_text": ""
            })

            if filtered_out:
                continue

            if not likely:
                continue

            if not player_name:
                continue

            if player is None:
                continue

            player_data = player.to_dict()

            subject, body = format_portal_alert(
                player_name=player_data.get("Full Name", player_name),
                school=player_data.get("2025-2026 School", ""),
                hdi=player_data.get("RATING", ""),
                reporter=username,
                tweet_url=f"https://x.com/{username}/status/{tweet.get('id')}",
                report_url="https://portalapp.com/reports/example.png"
            )

            send_email_alert(subject, body)

            alerts_sent.append({
                "player": player_data.get("Full Name", player_name),
                "score": score,
                "text": text
            })

    if debug:
        return alerts_sent, debug_log

    return alerts_sent
