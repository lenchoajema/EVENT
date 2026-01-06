import logging
import smtplib
import json
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .config import (
    SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD,
    SLACK_WEBHOOK_URL, ENABLE_EMAIL_ALERTS, ENABLE_SLACK_ALERTS
)

logger = logging.getLogger(__name__)

class NotificationManager:
    def __init__(self):
        pass

    def send_alert(self, subject: str, message: str, recipients: list = None):
        """Dispatch alerts to configured channels."""
        if ENABLE_EMAIL_ALERTS and recipients:
            self.send_email(subject, message, recipients)
        
        if ENABLE_SLACK_ALERTS:
            self.send_slack(f"*{subject}*\n{message}")

    def send_email(self, subject: str, body: str, recipients: list):
        try:
            msg = MIMEMultipart()
            msg['From'] = SMTP_USER
            msg['To'] = ", ".join(recipients)
            msg['Subject'] = f"[EVENT SYSTEM] {subject}"

            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            text = msg.as_string()
            server.sendmail(SMTP_USER, recipients, text)
            server.quit()
            logger.info("📧 Email alert sent successfully.")
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")

    def send_slack(self, message: str):
        if not SLACK_WEBHOOK_URL:
            return
            
        try:
            payload = {"text": message}
            response = requests.post(SLACK_WEBHOOK_URL, json=payload)
            if response.status_code == 200:
                logger.info("💬 Slack alert sent.")
            else:
                logger.error(f"Slack alert failed: {response.text}")
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")

notification_manager = NotificationManager()
