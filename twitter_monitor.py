import streamlit as st
import requests

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
        "max_results": 10
    }

    response = requests.get(SEARCH_URL, headers=headers, params=params)

    if response.status_code != 200:
        return {"error": response.text}

    return response.json()
