from email_sender import send_email_alert

alerts = process_tweets()

print(f"Alerts found: {len(alerts)}")

sent_count = 0

for alert in alerts:
    try:
        print(f"Sending email for: {alert['player']}")

        send_email(
            subject=f"Portal Alert: {alert['player']}",
            body=alert["text"],
            to_email=EMAIL_USER  # send to yourself for now
        )

        print("Email sent successfully")
        sent_count += 1

    except Exception as e:
        print(f"Email failed: {e}")

print(f"Run complete. Alerts sent: {sent_count}")
