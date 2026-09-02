"""
Data Loader Module
Handles CSV upload, validation, and customer data parsing
"""

import pandas as pd
import numpy as np
import streamlit as st
from typing import Tuple, Optional

REQUIRED_FEATURES = [
    'city', 'bd', 'registered_via', 'num_100', 'num_25',
    'total_secs', 'completion_rate', 'payment_plan_days',
    'plan_list_price', 'actual_amount_paid', 'is_auto_renew', 'is_cancel'
]

OPTIONAL_FEATURES = ['msno', 'email', 'gender', 'membership_expire_date', 
                      'registration_init_time', 'transaction_date']


def validate_csv_structure(df: pd.DataFrame) -> Tuple[bool, str]:
    """
    Validate CSV structure and content
    Returns: (is_valid, message)
    """
    
    # Check if dataframe is empty
    if df.empty:
        return False, "❌ CSV is empty. Please upload a file with customer data."
    
    # Check required columns
    missing_cols = [col for col in REQUIRED_FEATURES if col not in df.columns]
    if missing_cols:
        return False, f"❌ Missing required columns: {', '.join(missing_cols)}"
    
    # Check data types
    for col in REQUIRED_FEATURES:
        if col in df.columns:
            if not pd.api.types.is_numeric_dtype(df[col]):
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except:
                    return False, f"❌ Column '{col}' contains non-numeric values"
    
    # Check for all NaN rows
    if df[REQUIRED_FEATURES].isna().all(axis=1).any():
        return False, "❌ Some rows have all missing values"
    
    return True, "✅ CSV structure valid"


def load_csv(uploaded_file) -> Tuple[Optional[pd.DataFrame], str, dict]:
    """
    Load and validate CSV file
    Returns: (dataframe, message, stats)
    """
    
    try:
        df = pd.read_csv(uploaded_file)
        
        # Validate structure
        is_valid, validation_msg = validate_csv_structure(df)
        
        if not is_valid:
            return None, validation_msg, {}
        
        # Convert required columns to numeric
        for col in REQUIRED_FEATURES:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Generate stats
        stats = {
            'rows': len(df),
            'columns': len(df.columns),
            'missing_percent': (df.isna().sum().sum() / (len(df) * len(df.columns)) * 100),
            'complete_rows': (df[REQUIRED_FEATURES].notna().all(axis=1)).sum()
        }
        
        return df, "✅ CSV loaded successfully", stats
        
    except Exception as e:
        return None, f"❌ Error loading CSV: {str(e)}", {}


def get_customer_by_index(df: pd.DataFrame, index: int) -> pd.DataFrame:
    """Get single customer by index"""
    if index < 0 or index >= len(df):
        return None
    return df.iloc[[index]]


def get_customer_by_id(df: pd.DataFrame, customer_id: str) -> Optional[pd.DataFrame]:
    """Get single customer by ID"""
    if 'msno' not in df.columns:
        return None
    
    result = df[df['msno'] == customer_id]
    return result if not result.empty else None


def extract_features(customer_data: pd.DataFrame) -> Tuple[pd.DataFrame, bool]:
    """
    Extract and prepare features for model prediction
    Returns: (feature_vector, success)
    """
    
    try:
        features = customer_data[REQUIRED_FEATURES].copy()
        
        # Handle NaN values (fill with median)
        for col in features.columns:
            if features[col].isna().any():
                features[col].fillna(features[col].median(), inplace=True)
        
        # Convert to numeric
        features = features.apply(pd.to_numeric, errors='coerce')
        
        return features, True
        
    except Exception as e:
        print(f"Error extracting features: {e}")
        return None, False


def get_customer_info_dict(customer_data: pd.DataFrame) -> dict:
    """Convert customer row to dictionary for display"""
    
    info = {}
    
    # Basic info
    if 'msno' in customer_data.columns:
        info['customer_id'] = str(customer_data['msno'].values[0])[:20]
    if 'email' in customer_data.columns:
        info['email'] = customer_data['email'].values[0]
    if 'gender' in customer_data.columns:
        info['gender'] = customer_data['gender'].values[0]
    
    # Subscription info
    if 'payment_plan_days' in customer_data.columns:
        plan_days = customer_data['payment_plan_days'].values[0]
        info['plan_days'] = int(plan_days) if not np.isnan(plan_days) else 'N/A'
    if 'is_auto_renew' in customer_data.columns:
        auto_renew = customer_data['is_auto_renew'].values[0]
        info['auto_renew'] = '✅ Yes' if auto_renew == 1 else '❌ No'
    if 'is_cancel' in customer_data.columns:
        is_cancel = customer_data['is_cancel'].values[0]
        info['cancelled'] = '⚠️ Yes' if is_cancel == 1 else '✅ No'
    
    # Behavior
    if 'completion_rate' in customer_data.columns:
        completion = customer_data['completion_rate'].values[0]
        info['completion_rate'] = round(completion, 2) if not np.isnan(completion) else 'N/A'
    if 'num_100' in customer_data.columns:
        num_100 = customer_data['num_100'].values[0]
        info['songs_completed'] = int(num_100) if not np.isnan(num_100) else 'N/A'
    
    # Revenue
    if 'actual_amount_paid' in customer_data.columns:
        paid = customer_data['actual_amount_paid'].values[0]
        info['amount_paid'] = round(paid, 2) if not np.isnan(paid) else 'N/A'
    
    return info


@st.cache_data(ttl=3600)
def load_default_data():
    """Load default KKBOX data if available"""
    try:
        df = pd.read_csv('ui_data.csv')
        return df, f"✅ Loaded default data ({len(df)} customers)"
    except:
        return None, "⚠️ Default data not found"
