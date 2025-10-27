from os import environ
import smtplib
from email.message import EmailMessage


def send_otp_code(receiver: str, code: str):
    msg = EmailMessage()
    msg.set_content(
        f"Код подтверждения: {code}\n\n\n\n\nДанное сообщение отправлено автоматически. Отвечать на него не нужно.\nCipher"
    )
    msg["Subject"] = f"Код подтверждения"
    msg["From"] = environ.get("EMAILER_MAIL")
    msg["To"] = f"{receiver}"
    smtpObj = smtplib.SMTP("smtp.gmail.com:587")
    smtpObj.ehlo()
    smtpObj.starttls()
    smtpObj.login(environ.get("EMAILER_MAIL"), environ.get("EMAILER_PASS"))
    smtpObj.send_message(msg)
    smtpObj.quit()
