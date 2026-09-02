"""
Validators Module
Input validation, error checking, and data sanitization
"""

import re
from typing import Tuple, Optional


def validate_api_key(api_key: str, api_type: str = 'gemini') -> Tuple[bool, str]:
    """
    Validate API key format
    Returns: (is_valid, message)
    """
    
    if not api_key:
        return False, "❌ API key is empty"
    
    api_key = api_key.strip()
    
    if api_type.lower() == 'gemini':
        # Gemini keys typically start with specific patterns
        if len(api_key) < 30:
            return False, "❌ Gemini API key appears too short"
        if not re.match(r'^[A-Za-z0-9_-]+$', api_key):
            return False, "❌ API key contains invalid characters"
        return True, "✅ API key format valid"
    
    elif api_type.lower() == 'sendgrid':
        # SendGrid keys start with 'SG.'
        if not api_key.startswith('SG.'):
            return False, "❌ SendGrid key must start with 'SG.'"
        return True, "✅ SendGrid API key format valid"
    
    return True, "✅ API key format valid"


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input to prevent injection attacks
    Returns: sanitized text
    """
    
    if not isinstance(text, str):
        return ""
    
    # Truncate
    text = text[:max_length]
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', ';']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    return text.strip()


def validate_customer_id(customer_id: str) -> Tuple[bool, str]:
    """
    Validate customer ID format
    Returns: (is_valid, message)
    """
    
    if not customer_id or len(customer_id) == 0:
        return False, "❌ Customer ID is empty"
    
    if len(customer_id) > 100:
        return False, "❌ Customer ID is too long (max 100 chars)"
    
    # Allow alphanumeric and common special chars
    if not re.match(r'^[a-zA-Z0-9_\-\.]+$', customer_id):
        return False, "❌ Customer ID contains invalid characters"
    
    return True, "✅ Customer ID is valid"


def validate_feature_range(feature_name: str, value: float) -> Tuple[bool, str]:
    """
    Validate if feature value is within reasonable range
    Returns: (is_valid, message)
    """
    
    try:
        # Define reasonable ranges for each feature
        ranges = {
            'city': (1, 25),
            'bd': (1, 130),
            'registered_via': (1, 10),
            'num_100': (0, 100000),
            'num_25': (0, 100000),
            'total_secs': (0, 10000000),
            'completion_rate': (0, 100),
            'payment_plan_days': (1, 365),
            'plan_list_price': (0, 10000),
            'actual_amount_paid': (0, 10000),
            'is_auto_renew': (0, 1),
            'is_cancel': (0, 1)
        }
        
        if feature_name not in ranges:
            return True, "✅ Range not defined (skipping check)"
        
        min_val, max_val = ranges[feature_name]
        
        if value < min_val or value > max_val:
            return False, f"❌ {feature_name}: {value} is outside valid range [{min_val}, {max_val}]"
        
        return True, "✅ Value is within valid range"
        
    except Exception as e:
        return False, f"❌ Error validating range: {str(e)}"


def check_system_health() -> dict:
    """
    Check system health (model, data, API keys)
    Returns: dict with health status
    """
    
    import os
    import streamlit as st
    
    health = {
        'model_file': os.path.isfile('churn_model.pkl'),
        'data_file': os.path.isfile('ui_data.csv'),
        'logs_dir': os.path.isdir('logs'),
        'config_dir': os.path.isdir('config'),
        'has_gemini_key': 'GEMINI_API_KEY' in st.secrets,
        'has_email_config': 'EMAIL_SENDER' in st.secrets,
        'timestamp': __import__('datetime').datetime.now().isoformat()
    }
    
    return health


def validate_feature_vector(features_df) -> Tuple[bool, str]:
    """
    Validate feature vector before model prediction
    Returns: (is_valid, message)
    """
    
    try:
        required_features = [
            'city', 'bd', 'registered_via', 'num_100', 'num_25',
            'total_secs', 'completion_rate', 'payment_plan_days',
            'plan_list_price', 'actual_amount_paid', 'is_auto_renew', 'is_cancel'
        ]
        
        # Check all features present
        missing = [f for f in required_features if f not in features_df.columns]
        if missing:
            return False, f"❌ Missing features: {', '.join(missing)}"
        
        # Check for NaN values
        if features_df.isna().any().any():
            return False, "❌ Contains missing values (NaN)"
        
        # Check data types
        for col in required_features:
            if not __import__('pandas').api.types.is_numeric_dtype(features_df[col]):
                return False, f"❌ Feature '{col}' is not numeric"
        
        return True, "✅ Feature vector is valid"
        
    except Exception as e:
        return False, f"❌ Validation error: {str(e)}"


def check_rate_limit(operation: str, max_per_hour: int = 100) -> Tuple[bool, str]:
    """
    Check rate limiting for operations (emails, API calls, etc.)
    Returns: (is_allowed, message)
    """
    
    # Simple in-memory tracking (in production use Redis/database)
    if not hasattr(check_rate_limit, 'counters'):
        check_rate_limit.counters = {}
    
    from datetime import datetime, timedelta
    
    now = datetime.now()
    hour_key = f"{operation}_{now.strftime('%Y%m%d%H')}"
    
    if hour_key not in check_rate_limit.counters:
        check_rate_limit.counters[hour_key] = 0
    
    current_count = check_rate_limit.counters[hour_key]
    
    if current_count >= max_per_hour:
        return False, f"❌ Rate limit exceeded: {max_per_hour} {operation}s per hour"
    
    check_rate_limit.counters[hour_key] += 1
    
    return True, f"✅ {current_count + 1}/{max_per_hour} {operation}s this hour"


def validate_bulk_operation(customer_count: int, operation: str) -> Tuple[bool, str]:
    """
    Validate bulk operations (bulk email, etc.)
    Returns: (is_valid, message)
    """
    
    limits = {
        'bulk_email': 10000,  # Max 10k emails per operation
        'bulk_export': 100000,  # Max 100k exports per operation
        'batch_predict': 50000   # Max 50k predictions per operation
    }
    
    if operation not in limits:
        return False, f"❌ Unknown operation: {operation}"
    
    if customer_count > limits[operation]:
        return False, f"❌ Too many records for {operation}: {customer_count} (max {limits[operation]})"
    
    if customer_count <= 0:
        return False, f"❌ No customers selected for {operation}"
    
    return True, f"✅ Bulk {operation} valid for {customer_count} customers"
