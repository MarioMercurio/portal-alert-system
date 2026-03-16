from twilio.rest import Client
import streamlit as st


def send_sms(message: str):

    account_sid = st.secrets["TWILIO_ACCOUNT_SID"]
    auth_token = st.secrets["TWILIO_AUTH_TOKEN"]
    from_number = st.secrets["TWILIO_FROM_NUMBER"]
    to_number = st.secrets["TWILIO_TO_NUMBER"]

    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=message,
        from_=from_number,
        to=to_number
    )

    return message.sid
