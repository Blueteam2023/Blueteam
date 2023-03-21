import smtplib
import ssl
from email.message import EmailMessage


def send_mail(alert, email):
    port = 587
    user = "blueteamdevops2023@gmail.com"
    password = "yz6sSkdrCwYUBJcq"
    context = ssl.create_default_context()
    msg = EmailMessage()
    msg['Subject'] = 'Gan Shmuel - New Alert!'
    msg['From'] = "blueteamdevops2023@gmail.com"
    msg['To'] = email
    msg.set_content(f'New alert regard: {alert}')
    with smtplib.SMTP_SSL("smtp-relay.sendinblue.com", port, context=context) as server:
        server.login(user, password)
        server.send_message(msg)
        server.quit()