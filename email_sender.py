import smtplib
from email.message import EmailMessage
import streamlit as st


def send_email_alert(subject: str, body: str):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    sender_email = st.secrets["ALERT_EMAIL_ADDRESS"]
    sender_password = st.secrets["ALERT_EMAIL_APP_PASSWORD"]
    recipient_email = st.secrets["ALERT_RECIPIENT_EMAIL"]

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg.set_content(body)

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)

    return True
