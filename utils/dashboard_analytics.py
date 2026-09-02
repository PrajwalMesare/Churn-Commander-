"""
Dashboard Analytics Module
Calculates company-wide KPIs and analytics for executive dashboard
"""

import pandas as pd
import numpy as np
from typing import Tuple, dict


def calculate_company_kpis(df: pd.DataFrame, predictions: np.ndarray) -> dict:
    """
    Calculate key performance indicators for company dashboard
    Returns: dict with all KPIs
    """
    
    try:
        # Convert predictions to percentage
        churn_probs = predictions * 100
        
        total_customers = len(df)
        avg_churn_risk = np.mean(churn_probs)
        
        # Risk segments
        high_risk = np.sum(churn_probs > 70)
        medium_risk = np.sum((churn_probs >= 40) & (churn_probs <= 70))
        low_risk = np.sum(churn_probs < 40)
        
        # Revenue at risk
        high_risk_mask = churn_probs > 70
        revenue_at_risk = 0
        if 'actual_amount_paid' in df.columns:
            revenue_at_risk = df.loc[high_risk_mask, 'actual_amount_paid'].sum()
        
        # Premium/Free split (if available)
        total_premium = 0
        if 'plan_list_price' in df.columns:
            total_premium = np.sum(df['plan_list_price'] > 0)
        
        kpis = {
            'total_customers': int(total_customers),
            'avg_churn_risk': round(float(avg_churn_risk), 2),
            'high_risk_count': int(high_risk),
            'medium_risk_count': int(medium_risk),
            'low_risk_count': int(low_risk),
            'high_risk_percent': round(float(high_risk / total_customers * 100), 1) if total_customers > 0 else 0,
            'revenue_at_risk': round(float(revenue_at_risk), 2),
            'total_revenue': round(float(df['actual_amount_paid'].sum()) if 'actual_amount_paid' in df.columns else 0, 2),
            'premium_customers': int(total_premium),
            'free_customers': int(total_customers - total_premium)
        }
        
        return kpis
        
    except Exception as e:
        print(f"Error calculating KPIs: {e}")
        return {}


def get_churn_distribution(predictions: np.ndarray) -> dict:
    """
    Get churn probability distribution
    Returns: dict with distribution data
    """
    
    try:
        churn_probs = predictions * 100
        
        distribution = {
            'low': np.sum(churn_probs < 40),      # < 40%
            'medium': np.sum((churn_probs >= 40) & (churn_probs < 70)),  # 40-70%
            'high': np.sum(churn_probs >= 70)      # >= 70%
        }
        
        return distribution
        
    except Exception as e:
        print(f"Error getting distribution: {e}")
        return {'low': 0, 'medium': 0, 'high': 0}


def get_top_risk_drivers(df: pd.DataFrame, predictions: np.ndarray, n_top: int = 5) -> list:
    """
    Get top N features driving churn across company
    Returns: list of (feature, avg_importance) tuples
    """
    
    try:
        import shap
        import xgboost as xgb
        import joblib
        
        # Load model
        model = joblib.load('churn_model.pkl')
        
        # Get feature importance from model
        feature_importance = model.feature_importances_
        
        features = [
            'city', 'bd', 'registered_via', 'num_100', 'num_25',
            'total_secs', 'completion_rate', 'payment_plan_days',
            'plan_list_price', 'actual_amount_paid', 'is_auto_renew', 'is_cancel'
        ]
        
        top_features = sorted(
            zip(features, feature_importance),
            key=lambda x: x[1],
            reverse=True
        )[:n_top]
        
        return [(f[0].replace('_', ' ').title(), round(f[1] * 100, 1)) for f in top_features]
        
    except Exception as e:
        print(f"Error getting top drivers: {e}")
        return []


def segment_customers_by_risk(df: pd.DataFrame, predictions: np.ndarray) -> dict:
    """
    Segment customers into risk categories with details
    Returns: dict with segment details
    """
    
    try:
        churn_probs = predictions * 100
        
        high_risk_indices = np.where(churn_probs > 70)[0]
        medium_risk_indices = np.where((churn_probs >= 40) & (churn_probs <= 70))[0]
        low_risk_indices = np.where(churn_probs < 40)[0]
        
        def get_segment_stats(indices):
            if len(indices) == 0:
                return {
                    'count': 0,
                    'avg_completion_rate': 0,
                    'avg_revenue': 0,
                    'avg_plan_days': 0
                }
            
            segment_df = df.iloc[indices]
            
            stats = {
                'count': len(indices),
                'avg_completion_rate': round(segment_df['completion_rate'].mean(), 2) if 'completion_rate' in segment_df.columns else 0,
                'avg_revenue': round(segment_df['actual_amount_paid'].mean(), 2) if 'actual_amount_paid' in segment_df.columns else 0,
                'avg_plan_days': round(segment_df['payment_plan_days'].mean(), 1) if 'payment_plan_days' in segment_df.columns else 0,
                'auto_renew_enabled': int(segment_df['is_auto_renew'].sum()) if 'is_auto_renew' in segment_df.columns else 0
            }
            
            return stats
        
        segments = {
            'high_risk': get_segment_stats(high_risk_indices),
            'medium_risk': get_segment_stats(medium_risk_indices),
            'low_risk': get_segment_stats(low_risk_indices)
        }
        
        return segments
        
    except Exception as e:
        print(f"Error segmenting customers: {e}")
        return {}


def get_churn_by_demographic(df: pd.DataFrame, predictions: np.ndarray, column: str = 'city') -> list:
    """
    Get average churn risk by demographic (city, etc.)
    Returns: list of (demographic, avg_churn_risk) tuples
    """
    
    try:
        churn_probs = predictions * 100
        
        if column not in df.columns:
            return []
        
        df_copy = df.copy()
        df_copy['churn_prob'] = churn_probs
        
        by_demo = df_copy.groupby(column)['churn_prob'].agg(['mean', 'count'])
        by_demo = by_demo[by_demo['count'] >= 10]  # Filter for groups with 10+ customers
        by_demo = by_demo.sort_values('mean', ascending=False)
        
        result = [(str(idx), round(row['mean'], 1)) for idx, row in by_demo.head(10).iterrows()]
        
        return result
        
    except Exception as e:
        print(f"Error getting demographic data: {e}")
        return []


def calculate_retention_potential(df: pd.DataFrame, predictions: np.ndarray) -> dict:
    """
    Calculate potential revenue if we retain high-risk customers
    Returns: dict with retention metrics
    """
    
    try:
        churn_probs = predictions * 100
        high_risk_mask = churn_probs > 70
        
        if 'actual_amount_paid' in df.columns:
            revenue_at_risk = df.loc[high_risk_mask, 'actual_amount_paid'].sum()
            
            # Assume different retention rates
            retention_scenarios = {
                'pessimistic': revenue_at_risk * 0.30,  # 30% retention
                'realistic': revenue_at_risk * 0.60,    # 60% retention
                'optimistic': revenue_at_risk * 0.85    # 85% retention
            }
            
            return retention_scenarios
        
        return {}
        
    except Exception as e:
        print(f"Error calculating retention potential: {e}")
        return {}


def get_quick_insights(kpis: dict) -> list:
    """
    Generate quick actionable insights from KPIs
    Returns: list of insight strings
    """
    
    insights = []
    
    if kpis.get('avg_churn_risk', 0) > 50:
        insights.append("🔴 Average churn risk is CRITICAL (>50%). Immediate action needed.")
    elif kpis.get('avg_churn_risk', 0) > 40:
        insights.append("🟡 Average churn risk is ELEVATED (40-50%). Focus on top drivers.")
    
    high_risk = kpis.get('high_risk_count', 0)
    if high_risk > kpis.get('total_customers', 1) * 0.25:
        insights.append(f"⚠️ {high_risk} customers ({kpis.get('high_risk_percent', 0)}%) at HIGH risk. Prioritize outreach.")
    
    revenue_at_risk = kpis.get('revenue_at_risk', 0)
    total_revenue = kpis.get('total_revenue', 1)
    if revenue_at_risk > total_revenue * 0.20:
        insights.append(f"💰 ${revenue_at_risk:,.0f} revenue at risk ({(revenue_at_risk/total_revenue*100):.1f}% of total).")
    
    if not insights:
        insights.append("✅ Churn risk is stable and manageable. Continue monitoring.")
    
    return insights


def export_to_csv(df: pd.DataFrame, predictions: np.ndarray, filename: str = 'churn_analysis.csv') -> Tuple[bool, str]:
    """
    Export customer data with predictions to CSV
    Returns: (success, message)
    """
    
    try:
        export_df = df.copy()
        export_df['churn_risk_percent'] = predictions * 100
        export_df['risk_level'] = export_df['churn_risk_percent'].apply(
            lambda x: 'HIGH' if x > 70 else ('MEDIUM' if x >= 40 else 'LOW')
        )
        
        export_df.to_csv(filename, index=False)
        
        return True, f"✅ Exported {len(export_df)} customers to {filename}"
        
    except Exception as e:
        return False, f"❌ Export failed: {str(e)}"
