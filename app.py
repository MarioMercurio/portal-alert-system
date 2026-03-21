import streamlit as st
import time
from datetime import datetime
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

st.subheader("Live Twitter Monitor")

if st.button("Run Diagnostic Check Now"):
    try:
        alerts, debug_log = process_tweets(debug=True)

        st.write(f"**Checked at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.write(f"**Alerts sent this run:** {len(alerts)}")
        st.write(f"**Debug items:** {len(debug_log)}")

        if alerts:
            st.success(f"Diagnostic run sent {len(alerts)} alert(s).")
            for alert in alerts:
                st.write(f"**Player:** {alert.get('player', '')}")
                st.write(f"**Reporter:** {alert.get('reporter', '')}")
                st.write(f"**Source:** {alert.get('source', '')}")
                st.write(f"**Score:** {alert.get('score', '')}")
                st.write(f"**Tweet:** {alert.get('text', '')}")
                st.divider()
        else:
            st.info("Diagnostic run sent no alerts.")

        st.subheader("Diagnostic Debug Log")

        for item in debug_log[:100]:
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
        st.error(f"Diagnostic run failed: {e}")

AUTO_MODE = st.checkbox("Enable Auto Monitor (runs every 5 minutes)", value=True)

INTERVAL_SECONDS = 300

if AUTO_MODE:
    st.success("Auto monitor is running every 5 minutes...")

    status_placeholder = st.empty()
    detail_placeholder = st.empty()

    while True:
        try:
            alerts, debug_log = process_tweets(debug=True)
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            status_placeholder.info(
                f"Checked at {now_str} | Alerts this run: {len(alerts)} | Debug items: {len(debug_log)}"
            )

            if alerts:
                detail_placeholder.success(f"Sent {len(alerts)} alert(s) on the last cycle.")
            else:
                detail_placeholder.write("No new alerts on the last cycle.")

        except Exception as e:
            status_placeholder.error(f"Monitor error: {e}")

        time.sleep(INTERVAL_SECONDS)
