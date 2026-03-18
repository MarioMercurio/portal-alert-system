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

SEARCH_URL = "https://api.twitter.com/2/tweets/search/recent"
USER_TWEETS_URL = "https://api.twitter.com/2/users/{user_id}/tweets"

REPORTERS = [
    {"username": "GoodmanHoops", "id": "17330792"},
    {"username": "jeffborzello", "id": "40235531"},
    {"username": "TiptonEdits", "id": "145602194"},
    {"username": "VerbalCommits", "id": "362586870"},
    {"username": "On3sports", "id": "149871064"},
]

PORTAL_QUERY = (
    '"transfer portal" OR '
    '"entered the transfer portal" OR '
    '"has entered the transfer portal" OR '
    '"plans to enter the transfer portal" OR '
    '"intends to enter the transfer portal" OR '
    '"is entering the transfer portal" OR '
    '"will enter the transfer portal" OR '
    '"entered the portal" OR '
    '"in the transfer portal" OR '
    '"hit the transfer portal"'
)


def get_headers():
    return {
        "Authorization": f"Bearer {st.secrets['X_BEARER_TOKEN']}"
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


def search_portal_tweets(max_results=25):
    params = {
        "query": PORTAL_QUERY,
        "max_results": max_results,
        "tweet.fields": "author_id,created_at,lang",
        "expansions": "author_id",
        "user.fields": "username,name"
    }

    response = requests.get(SEARCH_URL, headers=get_headers(), params=params)

    if response.status_code != 200:
        return {
            "ok": False,
            "status_code": response.status_code,
            "error_text": response.text,
            "tweets": []
        }

    data = response.json()
    tweets = data.get("data", [])
    users = data.get("includes", {}).get("users", [])

    user_map = {}
    for user in users:
        user_map[user.get("id", "")] = {
            "username": user.get("username", "unknown"),
            "name": user.get("name", "")
        }

    enriched = []
    for tweet in tweets:
        author_id = tweet.get("author_id", "")
        author = user_map.get(author_id, {"username": "unknown", "name": ""})

        enriched.append({
            "id": str(tweet.get("id", "")).strip(),
            "text": tweet.get("text", ""),
            "lang": tweet.get("lang", ""),
            "username": author.get("username", "unknown"),
            "author_name": author.get("name", ""),
            "source": "search"
        })

    return {
        "ok": True,
        "status_code": 200,
        "error_text": "",
        "tweets": enriched
    }


def fetch_reporter_timeline_tweets():
    collected = []
    debug_items = []

    for reporter in REPORTERS:
        username = reporter["username"]
        user_id = reporter["id"]

        result = get_recent_tweets_for_user(user_id, max_results=10)

        if not result["ok"]:
            debug_items.append({
                "text": f"Timeline failed for @{username}",
                "score": 0,
                "likely": False,
                "player_name": "",
                "player_found": False,
                "reasons": [f"timeline_api_error_{result['status_code']}"],
                "api_status_code": result["status_code"],
                "api_error_text": result["error_text"],
                "source": "timeline"
            })
            continue

        raw_tweets = result["tweets"]

        if not raw_tweets:
            debug_items.append({
                "text": f"No tweets returned for @{username}",
                "score": 0,
                "likely": False,
                "player_name": "",
                "player_found": False,
                "reasons": ["no_tweets_returned"],
                "api_status_code": 200,
                "api_error_text": "",
                "source": "timeline"
            })
            continue

        debug_items.append({
            "text": f"Fetched {len(raw_tweets)} timeline tweets for @{username}",
            "score": 0,
            "likely": False,
            "player_name": "",
            "player_found": False,
            "reasons": ["timeline_ok"],
            "api_status_code": 200,
            "api_error_text": "",
            "source": "timeline"
        })

        for tweet in raw_tweets:
            collected.append({
                "id": str(tweet.get("id", "")).strip(),
                "text": tweet.get("text", ""),
                "lang": tweet.get("lang", ""),
                "username": username,
                "author_name": username,
                "source": "timeline"
            })

    return collected, debug_items


def fetch_search_tweets():
    result = search_portal_tweets(max_results=25)

    if not result["ok"]:
        return [], [{
            "text": "Broad search failed",
            "score": 0,
            "likely": False,
            "player_name": "",
            "player_found": False,
            "reasons": [f"search_api_error_{result['status_code']}"],
            "api_status_code": result["status_code"],
            "api_error_text": result["error_text"],
            "source": "search"
        }]

    tweets = result["tweets"]

    debug_items = [{
        "text": f"Fetched {len(tweets)} search tweets",
        "score": 0,
        "likely": False,
        "player_name": "",
        "player_found": False,
        "reasons": ["search_ok"],
        "api_status_code": 200,
        "api_error_text": "",
        "source": "search"
    }]

    return tweets, debug_items


def process_tweets(debug=False):
    df = load_superfile()
    seen_data = load_seen()

    alerts_sent = []
    debug_log = []

    timeline_tweets, timeline_debug = fetch_reporter_timeline_tweets()
    search_tweets, search_debug = fetch_search_tweets()

    debug_log.extend(timeline_debug)
    debug_log.extend(search_debug)

    all_candidates = timeline_tweets + search_tweets

    if not all_candidates:
        if debug:
            return alerts_sent, debug_log
        return alerts_sent

    for tweet in all_candidates:
        tweet_id = str(tweet.get("id", "")).strip()
        text = tweet.get("text", "")
        lang = tweet.get("lang", "")
        username = tweet.get("username", "unknown")
        author_name = tweet.get("author_name", username)
        source = tweet.get("source", "unknown")

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
                "api_error_text": "",
                "source": source
            })
            continue

        likely, score, reasons = is_likely_portal_tweet(
            tweet_text=text,
            author_username=username,
            author_name=author_name
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
            "api_error_text": "",
            "source": source
        })

        if lang and lang != "en":
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

        if has_seen_alert(player_data.get("Full Name", player_name), username, school, seen_data):
            debug_log.append({
                "text": text,
                "score": score,
                "likely": likely,
                "player_name": player_name,
                "player_found": True,
                "reasons": ["duplicate_alert_seen_same_day"],
                "api_status_code": 200,
                "api_error_text": "",
                "source": source
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
            "text": text,
            "source": source,
            "reporter": username
        })

    if debug:
        return alerts_sent, debug_log

    return alerts_sent
