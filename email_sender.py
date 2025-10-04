import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_CONFIG

def send_email(recipient_email, subject, body):
    """Sends an email using the configuration from config.py."""
    
    sender_email = EMAIL_CONFIG['sender_email']
    password = EMAIL_CONFIG['sender_password']
    
    if not recipient_email:
        print(f"Skipping email to {subject} target: No recipient email provided.")
        return False

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = recipient_email

    # Attach the body of the email as plain text.
    message.attach(MIMEText(body, "plain"))

    # Create a secure SSL context
    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'], context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, recipient_email, message.as_string())
            print(f"✅ Email alert sent successfully to {recipient_email}")
            return True
    except Exception as e:
        print(f"❌ Failed to send email to {recipient_email}. Error: {e}")
        return False