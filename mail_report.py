import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import logging

load_dotenv()

# Configure logger
logger = logging.getLogger(__name__)

def send_report_email(filepath: str):
    """
    Sends an email with the upload report as a CSV attachment via Gmail SMTP.
    Uses environment variables:
    - EMAIL_HOST_USER: Gmail address (verified with App Password)
    - EMAIL_HOST_PASSWORD: App Password generated from Gmail
    - EMAIL_RECEIVER: Recipient
    """
    # כתובת השרת של Gmail תמיד זהה
    email_host = 'smtp.gmail.com'
    email_port = 587
    email_user = os.getenv('EMAIL_HOST_USER')
    email_password = os.getenv('APP_PASSWORD')
    email_receiver = os.getenv('EMAIL_RECEIVER')

    if not all([email_user, email_password, email_receiver]):
        logger.error("[MAIL REPORT] Missing .env values for Gmail sending.")
        raise ValueError("Missing .env values for email sending.")

    logger.info(f"[MAIL REPORT] Starting to send report to: {email_receiver}")
    msg = EmailMessage()
    msg['Subject'] = 'WordPress Upload Report'
    msg['From'] = email_user
    msg['To'] = email_receiver
    msg.set_content("Hi,\n\nAttached is the upload report with all published post URLs.\n\nRegards,\nYour WordPress Bot")

    # Always attach as 'upload_report.csv'
    with open(filepath, 'rb') as f:
        file_data = f.read()
        filename = 'upload_report.csv'
        msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=filename)

    try:
        logger.info(f"[MAIL REPORT] Connecting to Gmail SMTP: {email_host}:{email_port}")
        with smtplib.SMTP(email_host, email_port) as server:
            server.starttls()
            server.login(email_user, email_password)
            logger.info("[MAIL REPORT] Sending email...")
            server.send_message(msg)
            logger.info("[MAIL REPORT] Email sent successfully via Gmail!")
    except Exception as e:
        logger.error(f"[MAIL REPORT] Failed to send email: {e}")
