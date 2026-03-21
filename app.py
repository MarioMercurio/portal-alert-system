import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Portal Alert System", page_icon="🚨")

st.title("Step 2 - Runtime Test")

st.write("This page tests whether process_tweets() runs successfully.")
st.write(f"Loaded at: {datetime.now()}")

try:
    from twitter_monitor import process_tweets
    st.success("twitter_monitor imported successfully ✅")
except Exception as e:
    st.error(f"twitter_monitor FAILED to import ❌: {e}")

if st.button("Run process_tweets(debug=True)"):
    try:
        alerts, debug_log = process_tweets(debug=True)

        st.success("process_tweets(debug=True) ran successfully ✅")
        st.write(f"Alerts returned: {len(alerts)}")
        st.write(f"Debug items returned: {len(debug_log)}")

        if alerts:
            st.subheader("Alerts")
            for alert in alerts[:10]:
                st.write(alert)

        if debug_log:
            st.subheader("Debug Log")
            for item in debug_log[:20]:
                st.write(item)

    except Exception as e:
        st.error(f"process_tweets(debug=True) FAILED ❌: {e}")
