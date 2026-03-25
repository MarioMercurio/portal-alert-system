from twitter_monitor import process_tweets
from email_sender import send_email_alert
from format_alert import format_portal_alert


def main():
    try:
        alerts = process_tweets(debug=False)
        print(f"Alerts found: {len(alerts)}")

        sent_count = 0

        for alert in alerts:
            try:
                player = alert.get("player", "Unknown Player")
                school = alert.get("school", "")
                hdi = alert.get("hdi", "")
                reporter = alert.get("reporter", "unknown")
                tweet_url = alert.get("tweet_url", "")
                report_url = alert.get("report_url", "")

                subject, body = format_portal_alert(
                    player_name=player,
                    school=school,
                    hdi=hdi,
                    reporter=reporter,
                    tweet_url=tweet_url,
                    report_url=report_url,
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
