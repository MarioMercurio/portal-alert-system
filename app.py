import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Portal Alert System", page_icon="🚨")

st.title("Step 1 - Import Test")

st.write("If this loads, base app is fine.")
st.write(f"Loaded at: {datetime.now()}")

# STEP 1: test import
try:
    from twitter_monitor import process_tweets
    st.success("twitter_monitor imported successfully ✅")
except Exception as e:
    st.error(f"twitter_monitor FAILED ❌: {e}")

if st.button("Test Button"):
    st.success("Button works")
