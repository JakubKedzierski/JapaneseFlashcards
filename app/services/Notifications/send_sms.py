from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv('.env')

class SMS_EVNS:
    SID = os.getenv('SMS_SID')
    AUTH_TOKEN = os.getenv('SMS_AUTH_TOKEN')
    SMS_FROM = os.getenv('SMS_FROM')
    SMS_TO = os.getenv('SMS_TO')

def send_sms(msg):
    account_sid = SMS_EVNS.SID
    auth_token = SMS_EVNS.AUTH_TOKEN
    client_twilio = Client(account_sid, auth_token)

    message = client_twilio.messages.create(
            body=msg,
            from_=SMS_EVNS.SMS_FROM,
            to=SMS_EVNS.SMS_TO
        )

    print(message)