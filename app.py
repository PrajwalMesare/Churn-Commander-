"""
CHURN COMMANDER - Optimized for Fast Streamlit Deployment
AI-Powered Customer Retention Platform
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import sys
import os

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG (Must be first)
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Churn Commander",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add utils to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ═══════════════════════════════════════════════════════════════════════════════
# CACHED IMPORTS (Only load once)
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_resource
def load_utils():
    """Load all utilities once"""
    from utils import (
        load_csv, validate_csv_structure, get_customer_info_dict, extract_features,
        load_model, predict_churn, get_risk_level, get_shap_values, get_top_risk_drivers,
        configure_gemini, generate_retention_strategy, generate_personalized_offer,
        get_fallback_strategies, get_fallback_offers,
        generate_email_draft, format_email_for_preview, validate_email_draft,
        validate_email_address, setup_smtp_connection, send_email_smtp, log_email_sent,
        read_email_logs,
        calculate_company_kpis, get_churn_distribution, segment_customers_by_risk,
        get_quick_insights, export_to_csv,
        validate_api_key, check_system_health
    )
    return {
        'load_csv': load_csv, 'validate_csv_structure': validate_csv_structure,
        'get_customer_info_dict': get_customer_info_dict, 'extract_features': extract_features,
        'load_model': load_model, 'predict_churn': predict_churn, 'get_risk_level': get_risk_level,
        'get_shap_values': get_shap_values, 'get_top_risk_drivers': get_top_risk_drivers,
        'configure_gemini': configure_gemini, 'generate_retention_strategy': generate_retention_strategy,
        'generate_personalized_offer': generate_personalized_offer, 'get_fallback_strategies': get_fallback_strategies,
        'get_fallback_offers': get_fallback_offers, 'generate_email_draft': generate_email_draft,
        'format_email_for_preview': format_email_for_preview, 'validate_email_draft': validate_email_draft,
        'validate_email_address': validate_email_address, 'setup_smtp_connection': setup_smtp_connection,
        'send_email_smtp': send_email_smtp, 'log_email_sent': log_email_sent,
        'read_email_logs': read_email_logs, 'calculate_company_kpis': calculate_company_kpis,
        'get_churn_distribution': get_churn_distribution, 'segment_customers_by_risk': segment_customers_by_risk,
        'get_quick_insights': get_quick_insights, 'export_to_csv': export_to_csv,
        'validate_api_key': validate_api_key, 'check_system_health': check_system_health
    }

utils = load_utils()

# ═══════════════════════════════════════════════════════════════════════════════
# CUSTOM CSS
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
    .main { padding-top: 0rem; }
    .metric-box { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                  color: white; padding: 20px; border-radius: 8px; text-align: center; }
    .metric-value { font-size: 28px; font-weight: bold; margin: 10px 0; }
    .metric-label { font-size: 12px; opacity: 0.9; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════

if 'customer_data' not in st.session_state:
    st.session_state.customer_data = None
if 'selected_customer_idx' not in st.session_state:
    st.session_state.selected_customer_idx = 0

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## ⚡ CHURN COMMANDER")
    st.markdown("*AI-Powered Retention*")
    st.divider()
    
    # API Configuration
    st.markdown("### 🔑 API Setup")
    gemini_key = st.text_input("Gemini API Key", type="password")
    
    if gemini_key:
        is_valid, msg = utils['validate_api_key'](gemini_key, 'gemini')
        if is_valid:
            st.success(msg)
            utils['configure_gemini'](gemini_key)
        else:
            st.error(msg)
    
    st.divider()
    
    # Data Upload
    st.markdown("### 📁 Data Upload")
    uploaded_file = st.file_uploader("Choose CSV", type="csv")
    
    if uploaded_file:
        df, load_msg, stats = utils['load_csv'](uploaded_file)
        if df is not None:
            st.session_state.customer_data = df
            st.success(load_msg)
            st.info(f"✓ {stats['rows']} customers")
        else:
            st.error(load_msg)
    else:
        from utils import load_default_data
        df, msg = load_default_data()
        if df is not None:
            st.session_state.customer_data = df
            st.info(f"📊 {msg}")

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ═══════════════════════════════════════════════════════════════════════════════

if st.session_state.customer_data is None:
    st.error("❌ No data loaded")
else:
    tab1, tab2, tab3 = st.tabs(["📊 Analysis", "📈 Dashboard", "📁 Data"])
    
    # TAB 1: CUSTOMER ANALYSIS
    with tab1:
        st.markdown("## 👤 Customer Analysis")
        
        model, model_loaded, _ = utils['load_model']()
        
        if model_loaded:
            selected_customer = st.session_state.customer_data.iloc[st.session_state.selected_customer_idx:st.session_state.selected_customer_idx+1]
            features, _ = utils['extract_features'](selected_customer)
            
            if features is not None:
                churn_percent, _ = utils['predict_churn'](model, features)
                risk_label, _ = utils['get_risk_level'](churn_percent)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Churn Risk", f"{churn_percent}%")
                with col2:
                    st.metric("Risk Level", risk_label)
                with col3:
                    st.metric("Status", "⚠️ At Risk" if churn_percent > 70 else "✅ Stable")
    
    # TAB 2: COMPANY DASHBOARD
    with tab2:
        st.markdown("## 📈 Company Dashboard")
        
        model, model_loaded, _ = utils['load_model']()
        
        if model_loaded:
            features_all, _ = utils['extract_features'](st.session_state.customer_data)
            predictions_all = model.predict_proba(features_all)[:, 1]
            
            kpis = utils['calculate_company_kpis'](st.session_state.customer_data, predictions_all)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Customers", f"{kpis['total_customers']:,}")
            with col2:
                st.metric("Avg Churn Risk", f"{kpis['avg_churn_risk']:.1f}%")
            with col3:
                st.metric("High-Risk", f"{kpis['high_risk_count']:,}")
            with col4:
                st.metric("Revenue at Risk", f"${kpis['revenue_at_risk']:,.0f}")
            
            st.divider()
            
            # Risk Distribution
            risk_dist = utils['get_churn_distribution'](predictions_all)
            fig = go.Figure(data=[go.Pie(
                labels=['Low', 'Medium', 'High'],
                values=[risk_dist['low'], risk_dist['medium'], risk_dist['high']],
                marker=dict(colors=['#2ecc71', '#f39c12', '#e74c3c'])
            )])
            st.plotly_chart(fig, use_container_width=True)
    
    # TAB 3: DATA MANAGEMENT
    with tab3:
        st.markdown("## 📁 Data Management")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Rows", len(st.session_state.customer_data))
        with col2:
            st.metric("Columns", len(st.session_state.customer_data.columns))
        with col3:
            st.metric("Complete", (st.session_state.customer_data.notna().all(axis=1)).sum())
        
        st.dataframe(st.session_state.customer_data.head(20), use_container_width=True)

st.divider()
st.caption("Churn Commander | Built for Speed")
