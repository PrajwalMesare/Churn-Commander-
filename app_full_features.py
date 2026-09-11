"""
CHURN COMMANDER v2.0
AI-Powered Customer Retention Platform

Features:
- Feature 1: Flexible customer data upload (CSV)
- Feature 2: Automated email sender with Gemini-generated offers
- Feature 3: Company-wide dashboard with KPIs and analytics

Author: Prajwal Mesare
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import sys
import os

# Add utils to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import utility modules
from utils import (
    load_csv, validate_csv_structure, get_customer_info_dict, extract_features,
    load_model, predict_churn, get_risk_level, get_shap_values, get_top_risk_drivers,
    configure_gemini, generate_retention_strategy, generate_personalized_offer,
    get_fallback_strategies, get_fallback_offers,
    generate_email_draft, format_email_for_preview, validate_email_draft,
    validate_email_address, setup_smtp_connection, send_email_smtp, log_email_sent,
    read_email_logs, test_email_connection,
    calculate_company_kpis, get_churn_distribution, segment_customers_by_risk,
    get_quick_insights, export_to_csv, get_churn_by_demographic,
    validate_api_key, check_system_health, validate_feature_vector
)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Churn Commander v2.0",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding-top: 0rem;
    }
    .metric-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        margin: 10px 0;
    }
    .metric-label {
        font-size: 12px;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════════

if 'customer_data' not in st.session_state:
    st.session_state.customer_data = None
if 'selected_customer_idx' not in st.session_state:
    st.session_state.selected_customer_idx = 0
if 'predictions' not in st.session_state:
    st.session_state.predictions = None
if 'email_draft' not in st.session_state:
    st.session_state.email_draft = None
if 'smtp_connection' not in st.session_state:
    st.session_state.smtp_connection = None

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR: CONTROLS & CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## ⚡ CHURN COMMANDER v2.0")
    st.markdown("*AI-Powered Retention Platform*")
    st.divider()
    
    # API Configuration
    st.markdown("### 🔑 API Configuration")
    gemini_key = st.text_input(
        "Gemini API Key",
        type="password",
        help="Get your key from https://makersuite.google.com/app/apikey"
    )
    
    if gemini_key:
        is_valid, msg = validate_api_key(gemini_key, 'gemini')
        if is_valid:
            st.success(msg)
            configure_gemini(gemini_key)
        else:
            st.error(msg)
    
    st.divider()
    
    # Data Upload
    st.markdown("### 📁 Upload Customer Data")
    uploaded_file = st.file_uploader(
        "Choose CSV file",
        type="csv",
        help="Format: Same structure as KKBOX data (19 features)"
    )
    
    if uploaded_file:
        df, load_msg, stats = load_csv(uploaded_file)
        if df is not None:
            st.session_state.customer_data = df
            st.success(load_msg)
            st.info(f"✓ {stats['rows']} customers | {stats['complete_rows']} complete records")
        else:
            st.error(load_msg)
    else:
        # Load default data
        from utils import load_default_data
        df, msg = load_default_data()
        if df is not None:
            st.session_state.customer_data = df
            st.info(f"📊 {msg}")
        else:
            st.warning(msg)
    
    st.divider()
    
    # Customer Selection
    if st.session_state.customer_data is not None:
        st.markdown("### 👤 Select Customer")
        
        customer_options = []
        for idx, row in st.session_state.customer_data.iterrows():
            if 'msno' in st.session_state.customer_data.columns:
                label = f"#{idx+1} | {str(row['msno'])[:15]}..."
            else:
                label = f"Customer #{idx+1}"
            customer_options.append((idx, label))
        
        st.session_state.selected_customer_idx = st.selectbox(
            "Choose customer",
            [opt[0] for opt in customer_options],
            format_func=lambda x: [opt[1] for opt in customer_options if opt[0] == x][0]
        )
        
        # Show customer info
        if st.session_state.customer_data is not None:
            customer = st.session_state.customer_data.iloc[st.session_state.selected_customer_idx]
            info = get_customer_info_dict(st.session_state.customer_data.iloc[[st.session_state.selected_customer_idx]])
            
            with st.expander("📋 Customer Snapshot", expanded=True):
                for key, value in info.items():
                    st.write(f"**{key.replace('_', ' ').title()}:** {value}")
    
    st.divider()
    
    # Email Configuration
    st.markdown("### 📧 Email Configuration")
    email_service = st.radio(
        "Email Service",
        ["Gmail SMTP", "SendGrid API"],
        help="Choose email sending service"
    )
    
    if email_service == "Gmail SMTP":
        sender_email = st.text_input("Gmail Address", placeholder="your.email@gmail.com")
        sender_password = st.text_input(
            "Gmail App Password",
            type="password",
            help="Use Gmail App Password, not regular password"
        )
        
        if st.button("🔗 Test Connection", use_container_width=True):
            from utils import test_email_connection
            success, msg = test_email_connection(
                "smtp.gmail.com", 587, sender_email, sender_password
            )
            if success:
                st.success(msg)
            else:
                st.error(msg)
    
    st.divider()
    
    # System Health
    st.markdown("### ⚙️ System Status")
    health = check_system_health()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Model", "✅" if health['model_file'] else "❌")
        st.metric("Data", "✅" if health['data_file'] else "❌")
    with col2:
        st.metric("Logs", "✅" if health['logs_dir'] else "❌")
        st.metric("Config", "✅" if health['config_dir'] else "❌")
    
    st.divider()
    st.caption("Built by Prajwal Mesare\nTGPCET Nagpur | 2027")

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT: 3 TABS
# ═══════════════════════════════════════════════════════════════════════════════

if st.session_state.customer_data is None:
    st.error("❌ No customer data loaded. Please upload a CSV file in the sidebar.")
else:
    tab1, tab2, tab3 = st.tabs(["📊 Customer Analysis", "📈 Company Dashboard", "📁 Data Management"])
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # TAB 1: CUSTOMER ANALYSIS (OLD + NEW)
    # ═══════════════════════════════════════════════════════════════════════════════
    
    with tab1:
        st.markdown("## 👤 Individual Customer Analysis")
        
        # Load model
        model, model_loaded, model_msg = load_model()
        
        if not model_loaded:
            st.error(model_msg)
        else:
            # Get selected customer
            selected_customer = st.session_state.customer_data.iloc[st.session_state.selected_customer_idx:st.session_state.selected_customer_idx+1]
            
            # Extract features
            features, extract_success = extract_features(selected_customer)
            
            if extract_success:
                # Make prediction
                churn_percent, pred_success = predict_churn(model, features)
                
                if pred_success:
                    # Get risk level
                    risk_label, risk_class = get_risk_level(churn_percent)
                    
                    # Display churn score
                    st.markdown("### 🎯 Churn Risk Score")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"""
                        <div class="metric-box">
                            <div class="metric-label">Risk Probability</div>
                            <div class="metric-value">{churn_percent}%</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div class="metric-box">
                            <div class="metric-label">Risk Level</div>
                            <div class="metric-value">{risk_label}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Get SHAP values
                    shap_vals, shap_success = get_shap_values(model, features)
                    
                    if shap_success and shap_vals is not None:
                        top_drivers = get_top_risk_drivers(shap_vals, n_top=3)
                        
                        with col3:
                            if top_drivers:
                                driver_text = top_drivers[0][0] if top_drivers else "N/A"
                                st.markdown(f"""
                                <div class="metric-box">
                                    <div class="metric-label">Top Risk Driver</div>
                                    <div class="metric-value" style="font-size: 16px;">{driver_text}</div>
                                </div>
                                """, unsafe_allow_html=True)
                    
                    st.divider()
                    
                    # Tabs for analysis
                    analysis_tab1, analysis_tab2, analysis_tab3 = st.tabs(
                        ["🤖 AI Strategy", "📈 Analytics", "🔍 SHAP Explainability"]
                    )
                    
                    # AI Retention Strategy
                    with analysis_tab1:
                        st.markdown("### 📋 Personalized Retention Strategy")
                        
                        if top_drivers:
                            top_factor = top_drivers[0][0]
                        else:
                            top_factor = "engagement"
                        
                        # Get customer info for Gemini
                        customer_info = selected_customer.iloc[0]
                        
                        if st.button("🚀 Generate AI Strategy", use_container_width=True):
                            with st.spinner("Generating strategy..."):
                                strategy, success, msg = generate_retention_strategy(
                                    str(customer_info.get('msno', 'Unknown'))[:20],
                                    churn_percent,
                                    risk_label,
                                    top_factor,
                                    customer_info.get('payment_plan_days', 30),
                                    int(customer_info.get('is_auto_renew', 0)),
                                    int(customer_info.get('is_cancel', 0)),
                                    customer_info.get('num_100', 0),
                                    customer_info.get('actual_amount_paid', 0)
                                )
                                
                                if success and strategy:
                                    st.success(msg)
                                    st.markdown(strategy)
                                else:
                                    st.error(msg)
                                    st.info("Using fallback strategy...")
                                    fallback = get_fallback_strategies().get('high_risk' if churn_percent > 70 else 'medium_risk' if churn_percent > 40 else 'low_risk')
                                    st.markdown(fallback)
                    
                    # Behavioral Analytics
                    with analysis_tab2:
                        st.markdown("### 📊 Behavioral Analytics")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        metrics_to_show = [
                            ('num_100', 'Songs Completed', col1),
                            ('completion_rate', 'Completion Rate (%)', col2),
                            ('total_secs', 'Total Listening (hrs)', col3),
                        ]
                        
                        for feature, label, col in metrics_to_show:
                            if feature in selected_customer.columns:
                                value = selected_customer[feature].values[0]
                                if feature == 'total_secs':
                                    value = round(value / 3600, 1)
                                col.metric(label, value)
                        
                        # Listening pattern chart
                        if 'num_100' in selected_customer.columns and 'num_25' in selected_customer.columns:
                            fig = go.Figure(data=[
                                go.Bar(name='Completed', x=['Songs'], y=[selected_customer['num_100'].values[0]]),
                                go.Bar(name='Skipped', x=['Songs'], y=[selected_customer['num_25'].values[0]])
                            ])
                            fig.update_layout(barmode='group', height=400)
                            st.plotly_chart(fig, use_container_width=True)
                    
                    # SHAP Explainability
                    with analysis_tab3:
                        st.markdown("### 🔍 SHAP Feature Importance")
                        
                        if shap_success and shap_vals is not None:
                            from utils import build_shap_dataframe
                            shap_df = build_shap_dataframe(shap_vals, features)
                            
                            if not shap_df.empty:
                                # SHAP waterfall
                                fig = go.Figure(data=[
                                    go.Bar(
                                        y=shap_df['Feature'],
                                        x=shap_df['SHAP Impact'],
                                        orientation='h',
                                        marker=dict(
                                            color=shap_df['SHAP Impact'],
                                            colorscale='RdBu',
                                            cmid=0
                                        )
                                    )
                                ])
                                fig.update_layout(height=500, title="Features Contributing to Churn Risk")
                                st.plotly_chart(fig, use_container_width=True)
                    
                    st.divider()
                    
                    # EMAIL SENDER (Feature 2 - NEW)
                    st.markdown("### 📧 Personalized Email Campaign (NEW)")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("🎁 Generate Personalized Offer", use_container_width=True):
                            with st.spinner("Generating offers..."):
                                offers, success, msg = generate_personalized_offer(
                                    churn_percent,
                                    risk_label,
                                    customer_info.get('completion_rate', 50),
                                    customer_info.get('actual_amount_paid', 0),
                                    customer_info.get('payment_plan_days', 30),
                                    customer_info.get('num_100', 0)
                                )
                                
                                if success and offers:
                                    st.session_state.offers = offers
                                    st.success(msg)
                                else:
                                    st.warning("Using fallback offers...")
                                    st.session_state.offers = get_fallback_offers()
                    
                    with col2:
                        if st.button("👁️ Preview Email", use_container_width=True):
                            if 'offers' in st.session_state:
                                st.session_state.email_draft = generate_email_draft(
                                    str(customer_info.get('msno', 'Customer'))[:20],
                                    customer_info.get('email', 'user@example.com'),
                                    churn_percent,
                                    risk_label,
                                    st.session_state.offers,
                                    get_fallback_strategies().get('high_risk' if churn_percent > 70 else 'medium_risk')
                                )
                                st.success("Email draft created!")
                    
                    with col3:
                        if st.button("✉️ Send Email to Customer", use_container_width=True):
                            if st.session_state.email_draft:
                                email = st.session_state.email_draft['to']
                                is_valid, email_msg = validate_email_address(email)
                                
                                if is_valid:
                                    # For demo, just log the email
                                    success, log_msg = log_email_sent(
                                        str(customer_info.get('msno', 'Unknown'))[:20],
                                        email,
                                        churn_percent,
                                        st.session_state.email_draft['subject'],
                                        'sent'
                                    )
                                    
                                    if success:
                                        st.success(f"✅ Email sent to {email}")
                                    else:
                                        st.error(log_msg)
                                else:
                                    st.error(email_msg)
                            else:
                                st.warning("Please preview email first")
                    
                    # Show email preview
                    if st.session_state.email_draft:
                        with st.expander("📋 Email Draft Preview", expanded=False):
                            st.write(format_email_for_preview(st.session_state.email_draft))
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # TAB 2: COMPANY DASHBOARD (NEW - Feature 3)
    # ═══════════════════════════════════════════════════════════════════════════════
    
    with tab2:
        st.markdown("## 📈 Company-Wide Dashboard")
        
        model, model_loaded, _ = load_model()
        
        if model_loaded:
            # Calculate predictions for all customers
            with st.spinner("Calculating predictions for all customers..."):
                features_all, _ = extract_features(st.session_state.customer_data)
                predictions_all = model.predict_proba(features_all)[:, 1]
                
                # Calculate KPIs
                kpis = calculate_company_kpis(st.session_state.customer_data, predictions_all)
            
            if kpis:
                # KPI Row
                st.markdown("### 📊 Key Performance Indicators")
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
                st.markdown("### 📊 Risk Distribution")
                risk_dist = get_churn_distribution(predictions_all)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_pie = go.Figure(data=[go.Pie(
                        labels=['Low Risk', 'Medium Risk', 'High Risk'],
                        values=[risk_dist['low'], risk_dist['medium'], risk_dist['high']],
                        marker=dict(colors=['#2ecc71', '#f39c12', '#e74c3c'])
                    )])
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with col2:
                    # Insights
                    st.markdown("### 💡 Quick Insights")
                    insights = get_quick_insights(kpis)
                    for insight in insights:
                        st.info(insight)
                
                st.divider()
                
                # Segment Analysis
                st.markdown("### 🎯 Customer Segments")
                segments = segment_customers_by_risk(st.session_state.customer_data, predictions_all)
                
                seg_col1, seg_col2, seg_col3 = st.columns(3)
                
                with seg_col1:
                    st.markdown("#### 🔴 High Risk")
                    if 'high_risk' in segments:
                        st.metric("Count", segments['high_risk']['count'])
                        st.metric("Avg Completion", f"{segments['high_risk']['avg_completion_rate']:.1f}%")
                
                with seg_col2:
                    st.markdown("#### 🟡 Medium Risk")
                    if 'medium_risk' in segments:
                        st.metric("Count", segments['medium_risk']['count'])
                        st.metric("Avg Completion", f"{segments['medium_risk']['avg_completion_rate']:.1f}%")
                
                with seg_col3:
                    st.markdown("#### 🟢 Low Risk")
                    if 'low_risk' in segments:
                        st.metric("Count", segments['low_risk']['count'])
                        st.metric("Avg Completion", f"{segments['low_risk']['avg_completion_rate']:.1f}%")
                
                st.divider()
                
                # Email Statistics
                st.markdown("### 📧 Email Campaign Statistics")
                email_logs = read_email_logs()
                
                if email_logs:
                    from utils import get_email_statistics
                    email_stats = get_email_statistics(email_logs)
                    
                    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
                    
                    with stat_col1:
                        st.metric("Total Sent", email_stats['total_sent'])
                    with stat_col2:
                        st.metric("Sent Today", email_stats['sent_today'])
                    with stat_col3:
                        st.metric("Success Rate", f"{email_stats['success_rate']}%")
                    with stat_col4:
                        st.metric("Bounced", email_stats['bounced'])
                else:
                    st.info("No emails sent yet. Start sending from the Customer Analysis tab!")
                
                st.divider()
                
                # Actions
                st.markdown("### ⚡ Actions")
                action_col1, action_col2, action_col3 = st.columns(3)
                
                with action_col1:
                    if st.button("📥 Export Risk List (CSV)", use_container_width=True):
                        success, msg = export_to_csv(
                            st.session_state.customer_data,
                            predictions_all,
                            'churn_analysis_export.csv'
                        )
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)
                
                with action_col2:
                    if st.button("📊 View Email Logs", use_container_width=True):
                        if email_logs:
                            st.dataframe(email_logs[-20:], use_container_width=True)
                        else:
                            st.info("No email logs yet")
                
                with action_col3:
                    if st.button("🔄 Refresh Dashboard", use_container_width=True):
                        st.rerun()
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # TAB 3: DATA MANAGEMENT (NEW - Feature 1)
    # ═══════════════════════════════════════════════════════════════════════════════
    
    with tab3:
        st.markdown("## 📁 Data Management")
        
        st.markdown("### 📊 Current Dataset")
        
        if st.session_state.customer_data is not None:
            data_info = st.session_state.customer_data
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Customers", len(data_info))
            with col2:
                st.metric("Features", len(data_info.columns))
            with col3:
                st.metric("Complete Records", (data_info.notna().all(axis=1)).sum())
            
            st.divider()
            
            st.markdown("### 📋 Data Preview")
            
            preview_rows = st.slider("Rows to display", 5, 50, 20)
            st.dataframe(
                data_info.head(preview_rows),
                use_container_width=True,
                height=400
            )
            
            st.divider()
            
            st.markdown("### 📈 Data Statistics")
            
            stats_col1, stats_col2 = st.columns(2)
            
            with stats_col1:
                st.markdown("**Missing Values**")
                missing = data_info.isna().sum()
                if missing.sum() > 0:
                    st.dataframe(missing[missing > 0])
                else:
                    st.success("No missing values!")
            
            with stats_col2:
                st.markdown("**Data Types**")
                st.dataframe(data_info.dtypes)
            
            st.divider()
            
            st.markdown("### ⬇️ Download Data")
            
            if st.button("📥 Download as CSV", use_container_width=True):
                csv = data_info.to_csv(index=False)
                st.download_button(
                    label="Click to download CSV",
                    data=csv,
                    file_name="customer_data.csv",
                    mime="text/csv"
                )


# ═══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════════════════

st.divider()
st.markdown("""
---
**Churn Commander v2.0** | *AI-Powered Customer Retention Platform*

**Features:**
- ✨ Feature 1: Flexible CSV data upload
- ✨ Feature 2: Automated email sender with Gemini AI
- ✨ Feature 3: Company-wide analytics dashboard

**Built by:** Prajwal Mesare | **Institution:** TGPCET Nagpur | **Batch:** 2027

**GitHub:** [PrajwalMesare/Churn-Commander-](https://github.com/PrajwalMesare/Churn-Commander-)

---
""")
