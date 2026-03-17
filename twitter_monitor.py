import streamlit as st
import requests
from tweet_parser import extract_player_name
from superfile_loader import load_superfile, find_player
from format_alert import format_portal_alert
from email_sender import send_email_alert
from portal_rules import is_likely_portal_tweet


SEARCH_URL = "https://api.twitter.com/2/tweets/search/recent"

PORTAL_QUERY = (
    '"entered the transfer portal" OR '
    '"has entered the transfer portal" OR '
    '"plans to enter the transfer portal" OR '
    '"is entering the transfer portal" OR '
    '"in the transfer portal"'
)


def search_portal_tweets():
    bearer_token = st.secrets["X_BEARER_TOKEN"]

    headers = {
        "Authorization": f"Bearer {bearer_token}"
    }

    params = {
        "query": PORTAL_QUERY,
        "max_results": 10,
        "tweet.fields": "author_id,created_at"
    }

    response = requests.get(SEARCH_URL, headers=headers, params=params)

    if response.status_code != 200:
        return []

    data = response.json()
    return data.get("data", [])


def process_tweets():
    df = load_superfile()
    tweets = search_portal_tweets()

    alerts_sent = []

    for tweet in tweets:
        text = tweet.get("text", "")

        # Score the tweet
        likely, score, reasons = is_likely_portal_tweet(
            tweet_text=text,
            author_username=""  # we don't have username yet
        )

        if not likely:
            continue

        # Extract player
        player_name = extract_player_name(text)
        if not player_name:
            continue

        # Match player
        player = find_player(df, player_name)
        if player is None:
            continue

        player_data = player.to_dict()

        # Format alert
        subject, body = format_portal_alert(
            player_name=player_data.get("Full Name", player_name),
            school=player_data.get("2025-2026 School", ""),
            hdi=player_data.get("RATING", ""),
            reporter="Unknown",
            tweet_url=f"https://x.com/i/web/status/{tweet.get('id')}",
            report_url="https://portalapp.com/reports/example.png"
        )

        # Send email
        send_email_alert(subject, body)

        alerts_sent.append({
            "player": player_data.get("Full Name", player_name),
            "score": score,
            "text": text
        })

    return alerts_sent
