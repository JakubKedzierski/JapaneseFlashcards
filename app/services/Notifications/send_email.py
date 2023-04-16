import os
from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import load_dotenv
load_dotenv('.env')

# credentials from https://mailtrap.io/

class Envs:
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = os.getenv('MAIL_PORT')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_STARTTLS = os.getenv('MAIL_STARTTLS')
    MAIL_SSL_TLS = os.getenv('MAIL_SSL_TLS')
    MAIL_FROM = os.getenv('MAIL_FROM')
    

conf = ConnectionConfig(
    MAIL_SERVER=  Envs.MAIL_SERVER,
    MAIL_PORT = Envs.MAIL_PORT,
    MAIL_USERNAME = Envs.MAIL_USERNAME,
    MAIL_PASSWORD = Envs.MAIL_PASSWORD,
    MAIL_STARTTLS = Envs.MAIL_STARTTLS,
    MAIL_SSL_TLS = Envs.MAIL_SSL_TLS,
    MAIL_FROM = Envs.MAIL_FROM,
)

async def send_email_async(subject: str, email_to: str, body: str):
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=body,
        subtype='html',
    )

    fast_mail = FastMail(conf)

    print("Send Email to {}".format(email_to))
    await fast_mail.send_message(message)


