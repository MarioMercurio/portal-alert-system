import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Portal Alert System", page_icon="🚨")

st.title("Portal Alert System - Minimal Diagnostic")

st.write("If you can see this page, the app is loading the new app.py file.")
st.write(f"Loaded at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if st.button("Test Button"):
    st.success("Button click worked.")

st.write("End of minimal diagnostic page.")
