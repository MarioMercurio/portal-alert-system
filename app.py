import streamlit as st
import time
from tweet_parser import extract_player_name
from superfile_loader import load_superfile, find_player
from sms_sender import send_sms
from email_sender import send_email_alert
from format_alert import format_portal_alert
from portal_rules import is_likely_portal_tweet
from twitter_monitor import process_tweets

st.set_page_config(page_title="Portal Alert System", page_icon="🚨")

st.title("Portal Alert System")


@st.cache_data
def get_superfile():
    return load_superfile()


def row_to_dict(player):
    if player is None:
        return None

    if hasattr(player, "to_dict"):
        return player.to_dict()

    if isinstance(player, dict):
        return player

    return None


df = get_superfile()

# -----------------------------
# SAMPLE TWEET INPUT
# -----------------------------
st.subheader("Paste a sample portal tweet")

sample_tweet = st.text_area(
    "Paste a sample portal tweet",
    value="A.J. Storr has entered the transfer portal, source tells @GoodmanHoops.",
    height=120,
    label_visibility="collapsed"
)

author_username = st.text_input(
    "Reporter username",
    value="GoodmanHoops"
)

author_name = st.text_input(
    "Reporter display name",
    value="Jeff Goodman"
)

st.divider()

# -----------------------------
# SCORING
# -----------------------------
st.subheader("Portal Tweet Score")

if st.button("Score Tweet"):
    try:
        likely, score, reasons = is_likely_portal_tweet(
            tweet_text=sample_tweet,
            author_username=author_username,
            author_name=author_name,
            min_score=4
        )

        st.write(f"**Likely portal tweet:** {likely}")
        st.write(f"**Score:** {score}")
        st.write(f"**Reasons:** {', '.join(reasons) if reasons else 'None'}")
    except Exception as e:
        st.error(f"Scoring failed: {e}")

st.divider()

# -----------------------------
# PARSER + MATCH
# -----------------------------
st.subheader("Tweet Parser + Player Match")

if st.button("Test Tweet Parser"):
    try:
        player_name = extract_player_name(sample_tweet)

        if not player_name:
            st.error("No player name detected.")
        else:
            st.write(f"Detected player: {player_name}")

            player = find_player(df, player_name)
            player_data = row_to_dict(player)

            if player_data is None:
                st.warning("Player not found in SuperFile.")
            else:
                st.success("Player found!")
                st.write(f"**Full Name:** {player_data.get('Full Name', '')}")
                st.write(f"**School:** {player_data.get('2025-2026 School', '')}")
                st.write(f"**HDI Rating:** {player_data.get('RATING', '')}")
                st.write(f"**Height:** {player_data.get('Height', '')}")
                st.write(f"**Age:** {player_data.get('Age', '')}")
    except Exception as e:
        st.error(f"Parser failed: {e}")

st.divider()

# -----------------------------
# ALERT TESTS
# -----------------------------
st.subheader("Alert Tests")

if st.button("Send Test SMS"):
    try:
        sid = send_sms("Portal Alert System test 🚨")
        st.success(f"SMS sent! SID: {sid}")
    except Exception as e:
        st.error(f"SMS failed: {e}")

if st.button("Send Test Email From Tweet"):
    try:
        likely, score, reasons = is_likely_portal_tweet(
            tweet_text=sample_tweet,
            author_username=author_username,
            author_name=author_name,
            min_score=4
        )

        if not likely:
            st.error(
                f"Tweet score too low. Score: {score}. "
                f"Reasons: {', '.join(reasons) if reasons else 'None'}"
            )
        else:
            player_name = extract_player_name(sample_tweet)

            if not player_name:
                st.error("No player name detected.")
            else:
                player = find_player(df, player_name)
                player_data = row_to_dict(player)

                if player_data is None:
                    st.error("Player not found in SuperFile.")
                else:
                    subject, body = format_portal_alert(
                        player_name=player_data.get("Full Name", player_name),
                        school=player_data.get("2025-2026 School", ""),
                        hdi=player_data.get("RATING", ""),
                        reporter=author_username,
                        tweet_url="https://x.com/example",
                        report_url="https://portalapp.com/reports/example.png"
                    )

                    send_email_alert(subject, body)
                    st.success(f"Email sent! Score: {score}")

    except Exception as e:
        st.error(f"Email failed: {e}")

st.divider()

# -----------------------------
# AUTO LIVE MONITOR (5 MIN)
# -----------------------------
st.subheader("Live Twitter Monitor")

AUTO_MODE = st.checkbox("Enable Auto Monitor (runs every 5 minutes)", value=True)

INTERVAL_SECONDS = 300  # 5 minutes

if AUTO_MODE:
    st.success("Auto monitor is running every 5 minutes...")

    while True:
        try:
            alerts = process_tweets(debug=False)

            if alerts:
                st.success(f"Sent {len(alerts)} alert(s)")
            else:
                st.info("No new alerts")

        except Exception as e:
            st.error(f"Monitor error: {e}")

        time.sleep(INTERVAL_SECONDS)
