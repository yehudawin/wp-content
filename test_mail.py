import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# טען משתני סביבה מה-.env
load_dotenv()

# שלוף נתונים מהסביבה
email_host = os.getenv('EMAIL_HOST')
email_port = int(os.getenv('EMAIL_PORT', 587))
email_user = os.getenv('EMAIL_HOST_USER')
email_password = os.getenv('EMAIL_HOST_PASSWORD')
email_receiver = os.getenv('EMAIL_RECEIVER')

if not all([email_host, email_port, email_user, email_password, email_receiver]):
    raise ValueError("❌ One or more required environment variables are missing")

# צור קובץ CSV לבדיקה
test_csv_path = 'test_upload.csv'
with open(test_csv_path, 'w', encoding='utf-8') as f:
    f.write("Title,Link\n")
    f.write("Example Post,https://example.com/post-1\n")

# צור הודעת מייל
msg = EmailMessage()
msg['Subject'] = '✅ בדיקת שליחה עם קובץ CSV מצורף - Gmail SMTP'
msg['From'] = email_user
msg['To'] = email_receiver
msg.set_content("שלום,\n\nמצורף קובץ CSV לבדיקה. אם אתה רואה את המייל הזה עם הקובץ – הכול עובד כראוי.\n\nPromptBot")

# צרף את קובץ ה־CSV
with open(test_csv_path, 'rb') as f:
    file_data = f.read()
    msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename='test_upload.csv')

# נסה לשלוח את המייל
try:
    print(f"[TEST MAIL] Connecting to {email_host}:{email_port} as {email_user}")
    with smtplib.SMTP(email_host, email_port) as server:
        server.starttls()
        server.login(email_user, email_password)
        server.send_message(msg)
        print("✅ Test email with CSV sent successfully!")
except Exception as e:
    print(f"❌ Failed to send test email: {e}")
