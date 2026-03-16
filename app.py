import streamlit as st
from tweet_parser import extract_player_name
from superfile_loader import load_superfile, find_player
from sms_sender import send_sms

st.set_page_config(page_title="Portal Alert System", page_icon="🚨")

st.title("Portal Alert System")

@st.cache_data
def get_superfile():
    return load_superfile()

df = get_superfile()

st.subheader("Paste a sample portal tweet")

sample_tweet = st.text_area(
    "Paste a sample portal tweet",
    value="A.J. Storr has entered the transfer portal, source tells @GoodmanHoops.",
    height=120,
    label_visibility="collapsed"
)

if st.button("Test Tweet Parser"):
    player_name = extract_player_name(sample_tweet)

    if not player_name:
        st.error("No player name detected.")
    else:
        st.write(f"Detected player: {player_name}")

        player = find_player(df, player_name)

        if not player:
            st.warning("Player not found in SuperFile.")
        else:
            st.success("Player found!")

            st.write(f"**Full Name:** {player.get('Full Name', '')}")
            st.write(f"**School:** {player.get('2025-2026 School', '')}")
            st.write(f"**HDI Rating:** {player.get('RATING', '')}")
            st.write(f"**Height:** {player.get('Height', '')}")
            st.write(f"**Age:** {player.get('Age', '')}")

st.divider()

st.subheader("SMS Test")

if st.button("Send Test SMS"):
    try:
        sid = send_sms("Portal Alert System test 🚨")
        st.success(f"SMS sent! SID: {sid}")
    except Exception as e:
        st.error(f"SMS failed: {e}")
