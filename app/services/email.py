import os
import smtplib

from email.message import EmailMessage
from dotenv import load_dotenv


# Load .env from the Demo project root
load_dotenv()


EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "").strip()
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD", "").strip()

# Remove spaces if the Google App Password was copied as:
# xxxx xxxx xxxx xxxx
EMAIL_APP_PASSWORD = EMAIL_APP_PASSWORD.replace(" ", "")


def send_email(
    recipient: str,
    subject: str,
    body: str
) -> dict:

    if not EMAIL_ADDRESS:
        return {
            "success": False,
            "error": "EMAIL_ADDRESS is missing from .env"
        }

    if not EMAIL_APP_PASSWORD:
        return {
            "success": False,
            "error": "EMAIL_APP_PASSWORD is missing from .env"
        }

    try:

        message = EmailMessage()

        message["From"] = EMAIL_ADDRESS
        message["To"] = recipient
        message["Subject"] = subject

        message.set_content(body)

        # Gmail SMTP
        with smtplib.SMTP(
            "smtp.gmail.com",
            587,
            timeout=30
        ) as server:

            # Start encrypted connection
            server.starttls()

            # Login with Gmail + App Password
            server.login(
                EMAIL_ADDRESS,
                EMAIL_APP_PASSWORD
            )

            # Send email
            server.send_message(message)

        return {
            "success": True,
            "message": f"Email sent successfully to {recipient}"
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }