"""
Prediction Engine Module
Handles model loading, churn prediction, and SHAP explainability
"""

import joblib
import numpy as np
import pandas as pd
import streamlit as st
from typing import Tuple

FEATURES = [
    'city', 'bd', 'registered_via', 'num_100', 'num_25',
    'total_secs', 'completion_rate', 'payment_plan_days',
    'plan_list_price', 'actual_amount_paid', 'is_auto_renew', 'is_cancel'
]


@st.cache_resource(show_spinner=False)
def load_model():
    """Load pre-trained XGBoost model"""
    try:
        model = joblib.load('churn_model.pkl')
        return model, True, "✅ Model loaded successfully"
    except FileNotFoundError:
        return None, False, "❌ Model file not found: churn_model.pkl"
    except Exception as e:
        return None, False, f"❌ Error loading model: {str(e)}"


def predict_churn(model, customer_features: pd.DataFrame) -> Tuple[float, bool]:
    """
    Predict churn probability for customer
    Returns: (churn_probability_percent, success)
    """
    try:
        if customer_features.empty:
            return 0, False
        
        # Get probability of churn (class 1)
        churn_prob = model.predict_proba(customer_features)[0][1]
        churn_percent = round(float(churn_prob) * 100, 2)
        
        return churn_percent, True
        
    except Exception as e:
        print(f"Error in prediction: {e}")
        return 0, False


def get_risk_level(churn_percent: float) -> Tuple[str, str]:
    """
    Categorize risk level based on churn probability
    Returns: (risk_label, risk_class)
    """
    
    if churn_percent >= 70:
        return "🔴 HIGH RISK", "risk-high"
    elif churn_percent >= 40:
        return "🟡 MEDIUM RISK", "risk-medium"
    else:
        return "🟢 LOW RISK", "risk-low"


def get_shap_values(model, customer_features: pd.DataFrame) -> Tuple[np.ndarray, bool]:
    """
    Calculate SHAP values for feature importance
    Returns: (shap_values, success)
    """
    try:
        import shap
        
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(customer_features)
        
        # Handle different SHAP output formats
        if len(shap_values.shape) == 3:
            vals = shap_values[0][:, 1]  # For binary classification
        else:
            vals = shap_values[0]
        
        return vals, True
        
    except Exception as e:
        print(f"Error calculating SHAP: {e}")
        return None, False


def get_top_risk_drivers(shap_vals: np.ndarray, n_top: int = 3) -> list:
    """
    Get top N features driving churn risk
    Returns: list of (feature_name, importance_percent) tuples
    """
    
    try:
        feature_importance = list(zip(FEATURES, np.abs(shap_vals)))
        feature_importance.sort(key=lambda x: x[1], reverse=True)
        
        top_drivers = [
            (feat.replace('_', ' ').title(), round(imp * 100, 1))
            for feat, imp in feature_importance[:n_top]
        ]
        
        return top_drivers
        
    except Exception as e:
        print(f"Error getting top drivers: {e}")
        return []


def get_shap_interpretation(shap_vals: np.ndarray, feature_values: pd.DataFrame) -> dict:
    """
    Get interpretable SHAP explanation
    Returns: dictionary with feature impact explanation
    """
    
    interpretation = {
        'positive_features': [],  # Increase churn risk
        'negative_features': []   # Decrease churn risk
    }
    
    try:
        for i, feature in enumerate(FEATURES):
            if i < len(shap_vals):
                shap_val = shap_vals[i]
                feat_val = feature_values[feature].values[0] if feature in feature_values.columns else 0
                
                impact = {
                    'feature': feature.replace('_', ' ').title(),
                    'value': round(feat_val, 2),
                    'impact': round(float(shap_val), 4),
                    'direction': '↑ Increases' if shap_val > 0 else '↓ Decreases'
                }
                
                if shap_val > 0:
                    interpretation['positive_features'].append(impact)
                else:
                    interpretation['negative_features'].append(impact)
        
        return interpretation
        
    except Exception as e:
        print(f"Error in SHAP interpretation: {e}")
        return interpretation


def build_shap_dataframe(shap_vals: np.ndarray, feature_values: pd.DataFrame) -> pd.DataFrame:
    """
    Build DataFrame for SHAP visualization
    Returns: DataFrame with features, impacts, and directions
    """
    
    try:
        shap_df = pd.DataFrame({
            'Feature': [f.replace('_', ' ').title() for f in FEATURES],
            'SHAP Impact': [float(v) for v in shap_vals],
            'Direction': ['↑ Increases Churn' if v > 0 else '↓ Reduces Churn' for v in shap_vals]
        })
        
        shap_df = shap_df.sort_values('SHAP Impact', key=abs, ascending=True)
        return shap_df
        
    except Exception as e:
        print(f"Error building SHAP dataframe: {e}")
        return pd.DataFrame()


def model_performance_metrics() -> dict:
    """Get model performance metrics"""
    return {
        'accuracy': '96.41%',
        'precision': '0.85',
        'recall': '0.73',
        'f1_score': '0.79',
        'training_samples': '776,768',
        'test_samples': '194,192',
        'total_dataset': '970,960'
    }
