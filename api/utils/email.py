from api.core.config import settings
from email.message import EmailMessage
import smtplib

def send_email(subject: str, to: str, body: str):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from
    msg["To"] = to
    msg.set_content(body)

    with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port) as server:
        server.login(settings.smtp_user, settings.smtp_pass)
        server.send_message(msg)
