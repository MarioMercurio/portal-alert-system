import streamlit as st
from datetime import datetime
import time

st.set_page_config(page_title="Portal Alert System", page_icon="🚨")

st.title("Step 3 - Deep Debug")

st.write("This will show exactly where process_tweets is getting stuck.")
st.write(f"Loaded at: {datetime.now()}")

from twitter_monitor import process_tweets

if st.button("Run process_tweets(debug=True)"):

    st.write("🚀 Starting process_tweets...")
    start_time = time.time()

    try:
        alerts, debug_log = process_tweets(debug=True)

        end_time = time.time()
        st.success(f"✅ Finished in {round(end_time - start_time, 2)} seconds")

        st.write(f"Alerts: {len(alerts)}")
        st.write(f"Debug log: {len(debug_log)}")

        if debug_log:
            st.subheader("First Debug Item")
            st.write(debug_log[0])

    except Exception as e:
        st.error(f"❌ ERROR: {e}")
