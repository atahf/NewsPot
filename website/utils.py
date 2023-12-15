from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import smtplib
from dotenv import load_dotenv

load_dotenv()


def send_mail(recipient, uuid, name, six_digit = "000000"):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = os.getenv("EMAIL_ADDRESS")
    smtp_pass = os.getenv("PASSWORD")
    sender_email = os.getenv("EMAIL_ADDRESS")
    recipient_email = recipient
    
    subject = "Password Recovery"
    link = f"127.0.0.1:5000/passwordReset/{uuid}"
    body = f"Hi {name}; \n\n\nBy clicking the link below you can reset your password.\n6 digit verification code: {six_digit}\n\n\n{link}"
        
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_pass)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
    except Exception as e:
        print("Email could not be sent.")