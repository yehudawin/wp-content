import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# טען משתנים מ-.env
load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
APP_PASSWORD = os.getenv("APP_PASSWORD")

if not EMAIL_ADDRESS or not APP_PASSWORD:
    raise ValueError("❌ EMAIL_ADDRESS or APP_PASSWORD is missing from .env")

# צור קובץ CSV לבדיקה
csv_filename = "test_upload.csv"
with open(csv_filename, 'w', encoding='utf-8') as f:
    f.write("Title,Link\n")
    f.write("Example Post,https://example.com/post-1\n")

# בנה את הודעת המייל
msg = EmailMessage()
msg['Subject'] = '✅ Gmail SMTP Test with CSV Attachment'
msg['From'] = EMAIL_ADDRESS
msg['To'] = EMAIL_ADDRESS
msg.set_content("הודעת בדיקה: מצורף קובץ CSV לבדיקה.\n\nאם אתה רואה את המייל הזה עם הקובץ – הכל פועל כשורה.\n\nבברכה,\nPromptBot")

# צרף את הקובץ
with open(csv_filename, 'rb') as f:
    msg.add_attachment(f.read(), maintype='application', subtype='octet-stream', filename=csv_filename)

# שליחה בפועל
try:
    print(f"[TEST MAIL] Connecting to smtp.gmail.com:587 as {EMAIL_ADDRESS}")
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_ADDRESS, APP_PASSWORD)
        smtp.send_message(msg)
        print("✅ Email with CSV sent successfully from Gmail.")
except Exception as e:
    print(f"❌ Failed to send test email: {e}")
