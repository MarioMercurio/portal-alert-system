import streamlit as st
from datetime import datetime
from twitter_monitor import process_tweets

st.set_page_config(page_title="Portal Alert System", page_icon="🚨")

st.title("Portal Alert System - Search Debug")

st.write("This page shows exactly what the search-only monitor is doing.")
st.write(f"Loaded at: {datetime.now()}")

if st.button("Run process_tweets(debug=True)"):
    try:
        st.write("🚀 Starting process_tweets...")
        alerts, debug_log = process_tweets(debug=True)

        st.success("process_tweets(debug=True) finished successfully ✅")
        st.write(f"Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.write(f"Alerts returned: {len(alerts)}")
        st.write(f"Debug items returned: {len(debug_log)}")

        if alerts:
            st.subheader("Alerts")
            for alert in alerts[:20]:
                st.write(alert)

        st.subheader("Debug Log")

        if not debug_log:
            st.write("No debug items returned.")
        else:
            for i, item in enumerate(debug_log[:60], start=1):
                st.markdown(f"### Debug Item {i}")
                st.write(f"**Source:** {item.get('source', '')}")
                st.write(f"**Text:** {item.get('text', '')}")
                st.write(f"**Score:** {item.get('score', '')}")
                st.write(f"**Likely:** {item.get('likely', False)}")
                st.write(f"**Player Detected:** {item.get('player_name', '')}")
                st.write(f"**Player Found:** {item.get('player_found', False)}")

                reasons = item.get("reasons", [])
                st.write(f"**Reasons:** {', '.join(reasons) if reasons else 'None'}")

                api_status_code = item.get("api_status_code", "")
                api_error_text = item.get("api_error_text", "")

                if api_status_code:
                    st.write(f"**API Status Code:** {api_status_code}")

                if api_error_text:
                    st.code(api_error_text)

                st.divider()

    except Exception as e:
        st.error(f"process_tweets(debug=True) FAILED ❌: {e}")
