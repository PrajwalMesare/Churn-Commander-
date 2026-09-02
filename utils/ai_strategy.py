"""
AI Strategy Module
Handles Gemini AI integration for personalized retention strategies
"""

import google.generativeai as genai
import streamlit as st
from typing import Tuple, Optional


def configure_gemini(api_key: str) -> Tuple[bool, str]:
    """
    Configure Gemini API with user's API key
    Returns: (success, message)
    """
    try:
        if not api_key or len(api_key) < 10:
            return False, "❌ Invalid API key format"
        
        genai.configure(api_key=api_key)
        return True, "✅ Gemini API configured"
        
    except Exception as e:
        return False, f"❌ Error configuring API: {str(e)}"


def generate_retention_strategy(
    account_id: str,
    churn_percent: float,
    risk_label: str,
    top_risk_factor: str,
    plan_days: float,
    auto_renew: int,
    is_cancel: int,
    songs_completed: float,
    amount_paid: float
) -> Tuple[Optional[str], bool, str]:
    """
    Generate 3-step retention strategy using Gemini AI
    Returns: (strategy_text, success, message)
    """
    
    try:
        system_prompt = f"""
You are an elite Customer Success AI for a music streaming platform.
Analyze this at-risk customer and provide a precise, actionable 3-step retention plan.

Customer Data:
- Account ID: {account_id}
- Churn Probability: {churn_percent}%
- Risk Level: {risk_label}
- Primary Risk Factor: {top_risk_factor}
- Plan Duration: {int(plan_days) if not isinstance(plan_days, float) or plan_days == plan_days else 'Unknown'} days
- Auto-Renew: {'Enabled' if auto_renew == 1 else 'DISABLED - Critical risk factor'}
- Has Cancelled Before: {'Yes' if is_cancel == 1 else 'No'}
- Songs Completed: {int(songs_completed) if not isinstance(songs_completed, float) or songs_completed == songs_completed else 'Unknown'}
- Revenue Contribution: ${round(amount_paid, 2) if isinstance(amount_paid, (int, float)) else 'Unknown'}

Format your response EXACTLY as follows (no preamble):

### 📊 Risk Diagnosis
(2-3 sentences explaining why this customer is at risk based on the data)

### 🎯 Tactical Action Plan
* **Action 1 (Immediate - 0-24hrs):** (Specific offer or nudge)
* **Action 2 (Short-term - 2-3 days):** (Specific communication)
* **Action 3 (Follow-up - Day 7):** (Retention confirmation step)

### 💡 Key Insight
(One sentence on the single most important thing to fix)
"""
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(system_prompt)
        
        return response.text, True, "✅ Strategy generated"
        
    except Exception as e:
        return None, False, f"❌ Error: {str(e)}"


def generate_personalized_offer(
    churn_percent: float,
    risk_label: str,
    completion_rate: float,
    amount_paid: float,
    plan_days: float,
    songs_completed: float
) -> Tuple[Optional[str], bool, str]:
    """
    Generate 3 personalized offer options using Gemini AI
    Returns: (offers_text, success, message)
    """
    
    try:
        offer_prompt = f"""
You are a retention specialist for a music streaming service.
Based on this customer's profile, generate 3 specific, compelling offers to prevent churn.

Customer Profile:
- Churn Risk: {churn_percent}%
- Risk Level: {risk_label}
- Completion Rate: {completion_rate}%
- Songs Completed: {int(songs_completed) if isinstance(songs_completed, (int, float)) else 0}
- Amount Paid: ${round(amount_paid, 2) if isinstance(amount_paid, (int, float)) else 0}
- Subscription Length: {int(plan_days) if isinstance(plan_days, (int, float)) else 30} days

Generate 3 DISTINCT offers. Format exactly as:

### Offer 1: [Title - e.g., "Premium Loyalty Discount"]
💰 **Offer:** [Specific deal, e.g., "50% off next month"]
⏰ **Valid Until:** [e.g., "7 days"]
📌 **Why This Works:** [1 sentence on why this appeals to them]

### Offer 2: [Title]
💰 **Offer:** [Specific deal]
⏰ **Valid Until:** [e.g., "14 days"]
📌 **Why This Works:** [1 sentence]

### Offer 3: [Title]
💰 **Offer:** [Specific deal]
⏰ **Valid Until:** [e.g., "30 days"]
📌 **Why This Works:** [1 sentence]

Make offers realistic, specific, and urgency-driven.
"""
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(offer_prompt)
        
        return response.text, True, "✅ Offers generated"
        
    except Exception as e:
        return None, False, f"❌ Error generating offers: {str(e)}"


def get_fallback_strategies() -> dict:
    """
    Get fallback strategies if Gemini API fails
    Returns: Pre-built strategy templates
    """
    
    return {
        'high_risk': """
### 📊 Risk Diagnosis
This high-risk customer shows critical churn signals. Immediate intervention required.

### 🎯 Tactical Action Plan
* **Action 1 (Immediate - 0-24hrs):** Offer 50% discount on next month + 7-day free trial of premium features
* **Action 2 (Short-term - 2-3 days):** Personal outreach from customer success team with exclusive playlist or new feature access
* **Action 3 (Follow-up - Day 7):** Send follow-up offer with lifetime 20% discount if renewed today

### 💡 Key Insight
Urgency and exclusivity are critical - make the offer time-limited and personalized.
""",
        
        'medium_risk': """
### 📊 Risk Diagnosis
This customer shows moderate churn risk. Proactive engagement can improve retention.

### 🎯 Tactical Action Plan
* **Action 1 (Immediate - 0-24hrs):** Send special 30% discount offer with 14-day validity window
* **Action 2 (Short-term - 2-3 days):** Recommend personalized playlists based on their listening history
* **Action 3 (Follow-up - Day 7):** Check-in via email with success metrics (songs saved, artists discovered)

### 💡 Key Insight
Re-engagement through personalization - show them value they're missing.
""",
        
        'low_risk': """
### 📊 Risk Diagnosis
This customer is low-risk but can benefit from appreciation and rewards.

### 🎯 Tactical Action Plan
* **Action 1 (Immediate - 0-24hrs):** Send loyalty appreciation message with 10% discount bonus
* **Action 2 (Short-term - 2-3 days):** Invite to exclusive artist events or new feature beta testing
* **Action 3 (Follow-up - Day 7):** Send monthly exclusive content or feature updates

### 💡 Key Insight
Nurture loyalty with exclusive benefits - make them feel valued and special.
"""
    }


def get_fallback_offers() -> str:
    """Get fallback offers if Gemini API fails"""
    return """
### Offer 1: Premium Loyalty Discount
💰 **Offer:** 40% off on next 3 months of premium subscription
⏰ **Valid Until:** 7 days
📌 **Why This Works:** Locks in long-term value while giving significant immediate savings

### Offer 2: Feature Upgrade Bonus
💰 **Offer:** Free upgrade to Premium Plus (ad-free + offline downloads) for 1 month
⏰ **Valid Until:** 14 days
📌 **Why This Works:** Lets them experience premium features risk-free

### Offer 3: Referral Rewards
💰 **Offer:** Invite 3 friends = 2 free months of premium + $10 credit
⏰ **Valid Until:** 30 days
📌 **Why This Works:** Engages them with friends while providing value
"""
