import streamlit as st
from twitter_monitor import search_portal_tweets

st.set_page_config(page_title="Portal Alert System", page_icon="🚨")

st.title("Portal Alert System")

if st.button("Search Live Portal Tweets"):
    results = search_portal_tweets()

    if "error" in results:
        st.error(results["error"])
    else:
        tweets = results.get("data", [])

        if not tweets:
            st.warning("No tweets found.")
        else:
            st.success(f"Found {len(tweets)} tweets")

            for tweet in tweets:
                st.write(tweet["text"])
                st.write("---")
