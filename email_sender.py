import os
import smtplib
import time
from email.mime.text import MIMEText


EMAIL_USER = os.getenv("EMAIL_USER") or os.getenv("EMAIL_USERNAME")
EMAIL_PASS = os.getenv("EMAIL_PASS") or os.getenv("EMAIL_PASSWORD")
DEFAULT_TO_EMAIL = EMAIL_USER


def send_email(subject, body, to_email=None):
    recipient = to_email or DEFAULT_TO_EMAIL

    if not EMAIL_USER:
        raise ValueError("Missing EMAIL_USER / EMAIL_USERNAME environment variable")

    if not EMAIL_PASS:
        raise ValueError("Missing EMAIL_PASS / EMAIL_PASSWORD environment variable")

    if not recipient:
        raise ValueError("Missing recipient email address")

    for attempt in range(3):
        try:
            print(f"Connecting to Gmail... attempt {attempt + 1}/3")

            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = EMAIL_USER
            msg["To"] = recipient

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(EMAIL_USER, EMAIL_PASS)
                print("Sending email...")
                server.sendmail(EMAIL_USER, recipient, msg.as_string())

            print("Email sent successfully")
            return True

        except Exception as e:
            print(f"Email failed (attempt {attempt + 1}/3): {e}")

            if attempt < 2:
                time.sleep(10)
            else:
                raise

    return False


def send_email_alert(subject, body):
    return send_email(subject=subject, body=body, to_email=DEFAULT_TO_EMAIL)
