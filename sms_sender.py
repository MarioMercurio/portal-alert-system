import os
from twilio.rest import Client

def send_sms(message):

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_phone = os.getenv("TWILIO_PHONE")
    to_phone = os.getenv("ALERT_PHONE")

    client = Client(account_sid, auth_token)

    client.messages.create(
        body=message,
        from_=from_phone,
        to=to_phone
    )
