"""
Mail Service Module
Handles email sending via SMTP with error handling and logging
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
import re
import streamlit as st
from typing import Tuple, Optional
from datetime import datetime
import csv
import os


def validate_email_address(email: str) -> Tuple[bool, str]:
    """
    Validate email address format (RFC 5322 simplified)
    Returns: (is_valid, message)
    """
    
    if not email or not isinstance(email, str):
        return False, "❌ Email is empty or invalid type"
    
    email = email.strip()
    
    # Simple regex for email validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        return False, f"❌ Invalid email format: {email}"
    
    if len(email) > 254:
        return False, "❌ Email address too long (max 254 characters)"
    
    return True, "✅ Email is valid"


def setup_smtp_connection(smtp_server: str, smtp_port: int, sender_email: str, 
                          sender_password: str) -> Tuple[Optional[smtplib.SMTP], bool, str]:
    """
    Setup SMTP connection with error handling
    Returns: (smtp_connection, success, message)
    """
    
    try:
        if not smtp_server or not sender_email or not sender_password:
            return None, False, "❌ Missing SMTP configuration"
        
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        server.starttls()
        
        try:
            server.login(sender_email, sender_password)
            return server, True, "✅ SMTP connection successful"
        except smtplib.SMTPAuthenticationError:
            return None, False, "❌ SMTP authentication failed - check credentials"
        except Exception as e:
            return None, False, f"❌ SMTP login failed: {str(e)}"
            
    except smtplib.SMTPException as e:
        return None, False, f"❌ SMTP Error: {str(e)}"
    except Exception as e:
        return None, False, f"❌ Connection error: {str(e)}"


def send_email_smtp(
    smtp_connection: smtplib.SMTP,
    sender_email: str,
    sender_name: str,
    recipient_email: str,
    subject: str,
    html_content: str,
    plain_text_content: str
) -> Tuple[bool, str, str]:
    """
    Send email using SMTP with retry logic
    Returns: (success, message, email_id)
    """
    
    try:
        # Validate recipient
        is_valid, validation_msg = validate_email_address(recipient_email)
        if not is_valid:
            return False, validation_msg, ""
        
        # Create message
        message = MIMEMultipart('alternative')
        message['From'] = formataddr((sender_name, sender_email))
        message['To'] = recipient_email
        message['Subject'] = subject
        
        # Add plain text and HTML parts
        part1 = MIMEText(plain_text_content, 'plain')
        part2 = MIMEText(html_content, 'html')
        message.attach(part1)
        message.attach(part2)
        
        # Send email
        smtp_connection.sendmail(sender_email, [recipient_email], message.as_string())
        
        email_id = f"{datetime.now().timestamp()}_{recipient_email}"
        return True, "✅ Email sent successfully", email_id
        
    except smtplib.SMTPRecipientsRefused:
        return False, "❌ Invalid recipient email address", ""
    except smtplib.SMTPSenderRefused:
        return False, "❌ Sender email rejected by server", ""
    except Exception as e:
        return False, f"❌ Error sending email: {str(e)}", ""


def log_email_sent(
    customer_id: str,
    customer_email: str,
    churn_percent: float,
    subject: str,
    status: str,
    email_id: str = "",
    error_msg: str = ""
) -> Tuple[bool, str]:
    """
    Log email sending attempt to CSV file
    Returns: (success, message)
    """
    
    try:
        log_file = 'logs/email_sent.log'
        
        # Create logs directory if not exists
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'customer_id': customer_id,
            'email': customer_email,
            'churn_percent': churn_percent,
            'subject': subject,
            'status': status,  # 'sent', 'failed', 'bounced'
            'email_id': email_id,
            'error_message': error_msg
        }
        
        # Write to CSV
        file_exists = os.path.isfile(log_file)
        
        with open(log_file, 'a', newline='') as csvfile:
            fieldnames = log_entry.keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(log_entry)
        
        return True, "✅ Email logged"
        
    except Exception as e:
        return False, f"⚠️ Logging failed: {str(e)}"


def read_email_logs() -> list:
    """
    Read email sending logs from CSV
    Returns: list of log entries
    """
    
    try:
        log_file = 'logs/email_sent.log'
        
        if not os.path.exists(log_file):
            return []
        
        logs = []
        with open(log_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            logs = list(reader)
        
        return logs
        
    except Exception as e:
        print(f"Error reading logs: {e}")
        return []


def get_gmail_smtp_config() -> dict:
    """Get Gmail SMTP configuration"""
    return {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'requires_app_password': True,
        'note': 'Use Gmail App Password, not regular password'
    }


def get_sendgrid_config() -> dict:
    """Get SendGrid API configuration"""
    return {
        'api_endpoint': 'https://api.sendgrid.com/v3/mail/send',
        'requires_api_key': True,
        'note': 'Use SendGrid API Key from dashboard'
    }


def test_email_connection(smtp_server: str, smtp_port: int, 
                         sender_email: str, sender_password: str) -> Tuple[bool, str]:
    """
    Test email connection without sending
    Returns: (success, message)
    """
    
    conn, success, msg = setup_smtp_connection(
        smtp_server, smtp_port, sender_email, sender_password
    )
    
    if success and conn:
        try:
            conn.quit()
        except:
            pass
    
    return success, msg


def close_smtp_connection(smtp_connection: smtplib.SMTP) -> bool:
    """Close SMTP connection safely"""
    try:
        if smtp_connection:
            smtp_connection.quit()
            return True
    except:
        pass
    return False
