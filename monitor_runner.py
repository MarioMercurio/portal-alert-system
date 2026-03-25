from twitter_monitor import process_tweets
from email_sender import send_email_alert


def main():
    try:
        alerts = process_tweets(debug=False)
        print(f"Alerts found: {len(alerts)}")

        sent_count = 0

        for alert in alerts:
            try:
                player = alert.get("player", "Unknown Player")
                text = alert.get("text", "")
                reporter = alert.get("reporter", "unknown")
                score = alert.get("score", "")

                subject = f"Portal Alert: {player}"
                body = (
                    f"Player: {player}\n"
                    f"Reporter: {reporter}\n"
                    f"Score: {score}\n\n"
                    f"Tweet:\n{text}"
                )

                print(f"Sending email for: {player}")
                send_email_alert(subject=subject, body=body)
                print("Email sent successfully")
                sent_count += 1

            except Exception as e:
                print(f"Email failed for {alert.get('player', 'Unknown Player')}: {e}")

        print(f"Run complete. Alerts sent: {sent_count}")

    except Exception as e:
        print(f"ERROR: {e}")
        raise


if __name__ == "__main__":
    main()
