import streamlit as st
from tweet_parser import extract_player_name

st.set_page_config(page_title="Portal Alert System", page_icon="🚨")

st.title("Portal Alert System")

tweet_text = st.text_area(
    "Paste a sample portal tweet",
    "A.J. Storr has entered the transfer portal, source tells @GoodmanHoops."
)

if st.button("Test Tweet Parser"):
    player_name = extract_player_name(tweet_text)
    st.write("Detected player:", player_name)
