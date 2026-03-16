import streamlit as st
from format_alert import format_entry_alert

st.set_page_config(page_title="Portal Alert System", page_icon="🚨")

st.title("Portal Alert System")

sample_message = format_entry_alert(
    player="A.J. Storr",
    school="Wisconsin",
    hdi=87,
    reporter="GoodmanHoops",
    tweet_link="https://x.com/example_tweet",
    report_link="https://example.com/report.png"
)

st.subheader("Sample Alert Preview")
st.code(sample_message)
