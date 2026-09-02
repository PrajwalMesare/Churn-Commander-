"""
Email Generator Module
Creates personalized email templates for retention campaigns
"""

from datetime import datetime, timedelta
import streamlit as st
from typing import Tuple, Optional


def create_email_template(
    customer_name: str,
    customer_email: str,
    churn_percent: float,
    risk_label: str,
    offer_text: str,
    retention_strategy: str
) -> Tuple[str, str]:
    """
    Create HTML and plain text email templates
    Returns: (html_content, plain_text_content)
    """
    
    offer_date = (datetime.now() + timedelta(days=7)).strftime('%B %d, %Y')
    
    # HTML Template
    html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; background: #f9f9f9; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background: white; padding: 30px; }}
        .risk-badge {{ display: inline-block; padding: 8px 16px; border-radius: 20px; font-weight: bold; margin: 10px 0; }}
        .risk-high {{ background: #ffebee; color: #c62828; }}
        .risk-medium {{ background: #fff3e0; color: #e65100; }}
        .risk-low {{ background: #e8f5e9; color: #2e7d32; }}
        .offer-box {{ background: #f0f7ff; border-left: 4px solid #667eea; padding: 15px; margin: 20px 0; }}
        .cta-button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 15px 0; font-weight: bold; }}
        .footer {{ background: #f9f9f9; padding: 20px; text-align: center; font-size: 12px; color: #666; border-top: 1px solid #ddd; }}
        .unsubscribe {{ color: #667eea; text-decoration: none; font-size: 11px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎵 We Value You</h1>
            <p>We noticed you might be thinking about leaving. We'd love to keep you!</p>
        </div>
        
        <div class="content">
            <p>Hi {customer_name},</p>
            
            <p>We've analyzed your subscription and noticed a {churn_percent}% likelihood you might cancel soon. <span class="risk-badge risk-{risk_label.split()[0].lower()}">Risk: {risk_label}</span></p>
            
            <p>We want to make it right. Here are our best exclusive offers just for you:</p>
            
            <div class="offer-box">
                {offer_text.replace(chr(10), '<br>')}
            </div>
            
            <p><strong>Why we're offering these:</strong></p>
            <p>{retention_strategy.split('###')[1].split(chr(10))[1:3] if '###' in retention_strategy else 'You matter to us!'}</p>
            
            <p style="text-align: center;">
                <a href="https://churn-commander.com/redeem" class="cta-button">Redeem My Offer Now →</a>
            </p>
            
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            
            <p><small><strong>Why did you get this email?</strong> We use AI to identify at-risk customers so we can offer the right help at the right time. We never spam.</small></p>
        </div>
        
        <div class="footer">
            <p>Churn Commander Retention System</p>
            <p>© 2024 | <a href="#" class="unsubscribe">Unsubscribe</a> | <a href="#" class="unsubscribe">Preferences</a></p>
        </div>
    </div>
</body>
</html>
"""
    
    # Plain Text Template
    plain_text = f"""
🎵 WE VALUE YOU - SPECIAL OFFER INSIDE 🎵

Hi {customer_name},

We've analyzed your subscription and noticed a {churn_percent}% likelihood you might cancel soon.

Risk Level: {risk_label}

We want to make it right. Here are our best exclusive offers just for you:

{offer_text}

Valid Until: {offer_date}

Why we're offering these:
We've analyzed your listening patterns and want to ensure you get the most value from your subscription.

[Redeem My Offer] → https://churn-commander.com/redeem

---

IMPORTANT INFORMATION:
• This offer is valid for 7 days from today
• Use code in your account settings to apply
• Works on all subscription plans
• Questions? Contact support@churn-commander.com

---

Churn Commander Retention System
© 2024

Unsubscribe: [link]
Preferences: [link]

This email was sent to: {customer_email}
"""
    
    return html_template, plain_text


def generate_email_draft(
    customer_name: str,
    customer_email: str,
    churn_percent: float,
    risk_label: str,
    offer_text: str,
    retention_strategy: str
) -> dict:
    """
    Generate complete email draft with metadata
    Returns: dict with all email details
    """
    
    html, plain_text = create_email_template(
        customer_name, customer_email, churn_percent, 
        risk_label, offer_text, retention_strategy
    )
    
    draft = {
        'to': customer_email,
        'from': 'noreply@churn-commander.com',
        'subject': f'🎵 Special Offer Inside - {risk_label}',
        'html': html,
        'plain_text': plain_text,
        'created_at': datetime.now().isoformat(),
        'customer_name': customer_name,
        'churn_percent': churn_percent,
        'risk_label': risk_label,
        'status': 'draft'
    }
    
    return draft


def format_email_for_preview(email_draft: dict) -> str:
    """Format email draft for preview in Streamlit"""
    
    preview = f"""
📧 **EMAIL DRAFT**

**To:** {email_draft['to']}
**From:** {email_draft['from']}
**Subject:** {email_draft['subject']}

---

{email_draft['plain_text']}

---

**Status:** {email_draft['status'].upper()}
**Created:** {email_draft['created_at']}
"""
    
    return preview


def validate_email_draft(email_draft: dict) -> Tuple[bool, str]:
    """
    Validate email draft before sending
    Returns: (is_valid, message)
    """
    
    checks = {
        'has_to': bool(email_draft.get('to')),
        'has_subject': bool(email_draft.get('subject')),
        'has_html': bool(email_draft.get('html')),
        'valid_email': '@' in email_draft.get('to', ''),
        'has_content': len(email_draft.get('plain_text', '')) > 50
    }
    
    if not all(checks.values()):
        failed = [k for k, v in checks.items() if not v]
        return False, f"❌ Email validation failed: {', '.join(failed)}"
    
    return True, "✅ Email is ready to send"


def get_email_statistics(email_logs: list) -> dict:
    """
    Calculate email campaign statistics
    Returns: dict with stats
    """
    
    if not email_logs:
        return {
            'total_sent': 0,
            'sent_today': 0,
            'success_rate': 0,
            'bounced': 0,
            'failed': 0
        }
    
    total = len(email_logs)
    today = datetime.now().date()
    sent_today = sum(1 for e in email_logs if datetime.fromisoformat(e['sent_at']).date() == today)
    successful = sum(1 for e in email_logs if e['status'] == 'sent')
    bounced = sum(1 for e in email_logs if e['status'] == 'bounced')
    failed = sum(1 for e in email_logs if e['status'] == 'failed')
    
    return {
        'total_sent': total,
        'sent_today': sent_today,
        'success_rate': round((successful / total * 100), 1) if total > 0 else 0,
        'bounced': bounced,
        'failed': failed
    }
