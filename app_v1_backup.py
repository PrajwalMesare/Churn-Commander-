import streamlit as st
import pandas as pd
import joblib
import shap
import google.generativeai as genai
import os
import ssl
import certifi
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- 1. CORE CONFIGURATION ---
os.environ['SSL_CERT_FILE'] = certifi.where()
ssl._create_default_https_context = ssl._create_unverified_context

st.set_page_config(page_title="Churn Commander", layout="wide", page_icon="⚡")

# --- PREMIUM CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 95%; }
    h1, h2, h3 { font-family: 'Inter', sans-serif; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; font-size: 15px; font-weight: 600; }
    .ai-box { background: linear-gradient(145deg, #F8FAFC, #EFF6FF); border-left: 4px solid #3B82F6; padding: 20px; border-radius: 8px; color: #0F172A; }
    .risk-high { background: linear-gradient(135deg, #FEE2E2, #FECACA); border-left: 4px solid #EF4444; padding: 12px 16px; border-radius: 8px; color: #7F1D1D; font-weight: 600; }
    .risk-medium { background: linear-gradient(135deg, #FEF3C7, #FDE68A); border-left: 4px solid #F59E0B; padding: 12px 16px; border-radius: 8px; color: #78350F; font-weight: 600; }
    .risk-low { background: linear-gradient(135deg, #D1FAE5, #A7F3D0); border-left: 4px solid #10B981; padding: 12px 16px; border-radius: 8px; color: #064E3B; font-weight: 600; }
    .stat-card { background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 16px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- 2. DATA & MODEL LOADING ---
@st.cache_resource(show_spinner=False)
def load_assets():
    model = joblib.load('churn_model.pkl')
    df = pd.read_csv('ui_data.csv')
    return model, df

# --- 3. SIDEBAR ---
with st.sidebar:
    st.markdown("## ⚡ Churn Commander")
    st.markdown("*AI-Powered Retention Intelligence*")
    st.markdown("---")

    st.markdown("### 🔑 Gemini API Key")
    user_api_key = st.text_input(
        "Google Gemini API Key",
        type="password",
        placeholder="Paste key from aistudio.google.com",
        help="Get free key at: https://aistudio.google.com/app/apikey"
    )
    if user_api_key:
        genai.configure(api_key=user_api_key)
        st.success("✅ AI Agent Ready")
    else:
        st.warning("⚠️ Add key to enable AI")

    st.markdown("---")

    xgb_model, ui_data = load_assets()

    st.markdown("### 🎯 Target Account")
    selected_index = st.selectbox(
        "Select Customer",
        ui_data.index,
        format_func=lambda x: f"#{x+1}  |  ID: {str(ui_data.iloc[x]['msno'])[:12]}..."
    )

    current_customer = ui_data.iloc[[selected_index]]

    st.markdown("---")
    st.markdown("### 📋 Account Snapshot")

    plan_days = current_customer['payment_plan_days'].values[0]
    auto_renew = current_customer['is_auto_renew'].values[0]
    is_cancel = current_customer['is_cancel'].values[0]
    completion = current_customer['completion_rate'].values[0]

    st.write(f"**Plan Duration:** {int(plan_days) if not np.isnan(plan_days) else 'N/A'} days")
    st.write(f"**Auto-Renew:** {'✅ Yes' if auto_renew == 1 else '❌ No'}")
    st.write(f"**Cancelled:** {'⚠️ Yes' if is_cancel == 1 else '✅ No'}")
    st.write(f"**Completion Rate:** {round(completion, 2) if not np.isnan(completion) else 'N/A'}%")

    st.markdown("---")
    st.caption("Built by Prajwal Mesare · TGPCET Nagpur")

# --- 4. FEATURE SETUP ---
FEATURES = [
    'city', 'bd', 'registered_via', 'num_100', 'num_25',
    'total_secs', 'completion_rate', 'payment_plan_days',
    'plan_list_price', 'actual_amount_paid', 'is_auto_renew', 'is_cancel'
]

input_vector = current_customer[FEATURES].apply(pd.to_numeric, errors='coerce')
churn_prob = xgb_model.predict_proba(input_vector)[0][1]
risk_percentage = round(float(churn_prob) * 100, 2)

# SHAP
explainer = shap.TreeExplainer(xgb_model)
shap_values = explainer.shap_values(input_vector)
vals = shap_values[0][:, 1] if len(shap_values.shape) == 3 else shap_values[0]
top_risk_feature = FEATURES[int(np.argmax(np.abs(vals)))]

# Risk level
if risk_percentage >= 70:
    risk_label = "🔴 HIGH RISK"
    risk_class = "risk-high"
elif risk_percentage >= 40:
    risk_label = "🟡 MEDIUM RISK"
    risk_class = "risk-medium"
else:
    risk_label = "🟢 LOW RISK"
    risk_class = "risk-low"

account_id = current_customer['msno'].values[0]

# --- 5. HEADER ---
st.markdown(f"## ⚡ Customer Intelligence Hub")
st.markdown(f"Analyzing account `{str(account_id)[:20]}...`")
st.markdown("---")

# --- 6. TOP METRICS ROW ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    with st.container(border=True):
        st.metric("🎯 Churn Risk Score", f"{risk_percentage}%",
                  delta="Critical" if risk_percentage > 50 else "Stable",
                  delta_color="inverse")
        st.progress(int(risk_percentage))
        st.markdown(f'<div class="{risk_class}">{risk_label}</div>', unsafe_allow_html=True)

with col2:
    with st.container(border=True):
        st.metric("🔍 Primary Risk Driver", top_risk_feature.replace('_', ' ').title())
        st.caption("Top SHAP feature impact")
        # Show all top 3 drivers
        feature_impacts = list(zip(FEATURES, np.abs(vals)))
        feature_impacts.sort(key=lambda x: x[1], reverse=True)
        for feat, imp in feature_impacts[:3]:
            st.caption(f"• {feat.replace('_',' ').title()}: {round(float(imp)*100, 1)}%")

with col3:
    with st.container(border=True):
        paid = current_customer['actual_amount_paid'].values[0]
        st.metric("💰 Revenue Contribution", f"${round(float(paid), 2) if not np.isnan(paid) else 'N/A'}")
        st.caption("Total amount paid this period")
        num100 = current_customer['num_100'].values[0]
        st.caption(f"🎵 Songs completed: {int(num100) if not np.isnan(num100) else 'N/A'}")

with col4:
    with st.container(border=True):
        expire_raw = current_customer['membership_expire_date'].values[0]
        if not np.isnan(expire_raw):
            expire_str = str(int(expire_raw))
            expire_fmt = f"{expire_str[:4]}-{expire_str[4:6]}-{expire_str[6:]}"
        else:
            expire_fmt = "N/A"
        st.metric("📅 Membership Expires", expire_fmt)
        st.caption("Subscription end date")
        reg_raw = current_customer['registration_init_time'].values[0]
        if not np.isnan(reg_raw):
            reg_str = str(int(reg_raw))
            reg_fmt = f"{reg_str[:4]}-{reg_str[4:6]}-{reg_str[6:]}"
            st.caption(f"📆 Member since: {reg_fmt}")

st.markdown("<br>", unsafe_allow_html=True)

# --- 7. TABS ---
tab1, tab2, tab3 = st.tabs(["🤖 AI Retention Strategy", "📊 Behavioral Analytics", "🔬 SHAP Explainability"])

# ── TAB 1: AI STRATEGY ──────────────────────────────────────────────────────
with tab1:
    st.markdown("### 🤖 Prescriptive Retention Engine")
    st.write("The Gemini AI agent analyses this customer's churn risk and top SHAP driver to generate a personalised 3-step intervention plan.")

    col_a, col_b = st.columns([2, 1])
    with col_a:
        if st.button("⚡ Generate AI Retention Plan", type="primary", use_container_width=True):
            if not user_api_key:
                st.error("🛑 Please paste your Google Gemini API Key in the sidebar to activate the AI Agent.")
            else:
                with st.spinner("🧠 Gemini is analysing churn vectors and crafting intervention strategy..."):
                    try:
                        system_prompt = f"""
You are an elite Customer Success AI for a music streaming platform.
Analyze this at-risk customer and provide a precise, actionable 3-step retention plan.

Customer Data:
- Account ID: {account_id}
- Churn Probability: {risk_percentage}%
- Risk Level: {risk_label}
- Primary Risk Factor: {top_risk_feature.replace('_', ' ').title()}
- Plan Duration: {int(plan_days) if not np.isnan(plan_days) else 'Unknown'} days
- Auto-Renew: {'Enabled' if auto_renew == 1 else 'DISABLED - Critical risk factor'}
- Has Cancelled Before: {'Yes' if is_cancel == 1 else 'No'}
- Songs Completed (num_100): {int(num100) if not np.isnan(num100) else 'Unknown'}
- Revenue Contribution: ${round(float(paid), 2) if not np.isnan(paid) else 'Unknown'}

Format your response strictly as:
### 📊 Risk Diagnosis
(2-3 sentences explaining why this customer is at risk based on the data)

### 🎯 Tactical Action Plan
* **Action 1 (Immediate - 0-24hrs):** (Specific offer or nudge)
* **Action 2 (Short-term - 2-3 days):** (Specific communication)
* **Action 3 (Follow-up - Day 7):** (Retention confirmation step)

### 💡 Key Insight
(One sentence on the single most important thing to fix)
"""
                        llm = genai.GenerativeModel('gemini-2.5-flash')
                        response = llm.generate_content(system_prompt)
                        st.markdown(f'<div class="ai-box">{response.text}</div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"AI Agent error: {str(e)}")

    with col_b:
        st.markdown("**Customer Risk Summary**")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=risk_percentage,
            title={'text': "Churn Risk %"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#EF4444" if risk_percentage > 70 else "#F59E0B" if risk_percentage > 40 else "#10B981"},
                'steps': [
                    {'range': [0, 40], 'color': "#D1FAE5"},
                    {'range': [40, 70], 'color': "#FEF3C7"},
                    {'range': [70, 100], 'color': "#FEE2E2"},
                ],
            }
        ))
        fig_gauge.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20),
                                paper_bgcolor="rgba(0,0,0,0)", font_color="#F1F5F9")
        st.plotly_chart(fig_gauge, use_container_width=True)

# ── TAB 2: BEHAVIORAL ANALYTICS ─────────────────────────────────────────────
with tab2:
    st.markdown("### 📊 Real Listening Behaviour Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # Real song completion data
        num_100 = float(current_customer['num_100'].values[0]) if not np.isnan(current_customer['num_100'].values[0]) else 0
        num_25 = float(current_customer['num_25'].values[0]) if not np.isnan(current_customer['num_25'].values[0]) else 0
        total_secs = float(current_customer['total_secs'].values[0]) if not np.isnan(current_customer['total_secs'].values[0]) else 0

        st.markdown("**🎵 Listening Activity Breakdown**")
        listen_df = pd.DataFrame({
            'Category': ['Completed (100%)', 'Skipped (25%)', 'Other'],
            'Count': [num_100, num_25, max(0, total_secs/240 - num_100 - num_25)]
        })
        fig_bar = px.bar(listen_df, x='Category', y='Count', color='Category',
                         color_discrete_map={'Completed (100%)': '#10B981', 'Skipped (25%)': '#EF4444', 'Other': '#94A3B8'},
                         title="Song Interaction Pattern")
        fig_bar.update_layout(height=300, showlegend=False,
                              paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              font_color="#F1F5F9")
        fig_bar.update_yaxes(gridcolor="#334155")
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        # Completion rate vs average
        avg_completion = float(ui_data['completion_rate'].mean())
        user_completion = float(current_customer['completion_rate'].values[0]) if not np.isnan(current_customer['completion_rate'].values[0]) else 0

        st.markdown("**📈 Completion Rate vs Platform Average**")
        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(name='This Customer', x=['Completion Rate'], y=[round(user_completion, 2)],
                                  marker_color='#3B82F6'))
        fig_comp.add_trace(go.Bar(name='Platform Average', x=['Completion Rate'], y=[round(avg_completion, 2)],
                                  marker_color='#94A3B8'))
        fig_comp.update_layout(height=300, barmode='group',
                               paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                               font_color="#F1F5F9", yaxis_gridcolor="#334155")
        st.plotly_chart(fig_comp, use_container_width=True)

    # Subscription health timeline
    st.markdown("**📅 Subscription Health Timeline**")
    reg_raw = current_customer['registration_init_time'].values[0]
    trans_raw = current_customer['transaction_date'].values[0]
    exp_raw = current_customer['membership_expire_date'].values[0]

    timeline_data = []
    if not np.isnan(reg_raw):
        timeline_data.append({"Event": "Registration", "Date": pd.to_datetime(str(int(reg_raw)), format='%Y%m%d'), "Type": "Start"})
    if not np.isnan(trans_raw):
        timeline_data.append({"Event": "Last Transaction", "Date": pd.to_datetime(str(int(trans_raw)), format='%Y%m%d'), "Type": "Transaction"})
    if not np.isnan(exp_raw):
        timeline_data.append({"Event": "Membership Expires", "Date": pd.to_datetime(str(int(exp_raw)), format='%Y%m%d'), "Type": "End"})

    if timeline_data:
        tl_df = pd.DataFrame(timeline_data).sort_values('Date')
        fig_tl = px.scatter(tl_df, x='Date', y='Event', color='Type', size=[20]*len(tl_df),
                            color_discrete_map={'Start': '#10B981', 'Transaction': '#3B82F6', 'End': '#EF4444'},
                            title="Customer Journey Timeline")
        fig_tl.update_layout(height=200, paper_bgcolor="rgba(0,0,0,0)",
                             plot_bgcolor="rgba(0,0,0,0)", font_color="#F1F5F9",
                             xaxis_gridcolor="#334155", showlegend=True)
        st.plotly_chart(fig_tl, use_container_width=True)
    else:
        st.info("Timeline data not available for this customer.")

# ── TAB 3: SHAP EXPLAINABILITY ───────────────────────────────────────────────
with tab3:
    st.markdown("### 🔬 Why Is This Customer At Risk?")
    st.write("SHAP (SHapley Additive exPlanations) shows the exact contribution of each feature to this customer's churn prediction.")

    # Build SHAP dataframe
    shap_df = pd.DataFrame({
        'Feature': [f.replace('_', ' ').title() for f in FEATURES],
        'SHAP Impact': [float(v) for v in vals],
        'Direction': ['↑ Increases Churn' if v > 0 else '↓ Reduces Churn' for v in vals]
    }).sort_values('SHAP Impact', key=abs, ascending=True)

    fig_shap = px.bar(shap_df, x='SHAP Impact', y='Feature', orientation='h',
                      color='Direction',
                      color_discrete_map={'↑ Increases Churn': '#EF4444', '↓ Reduces Churn': '#10B981'},
                      title=f"SHAP Feature Impact for This Customer")
    fig_shap.add_vline(x=0, line_dash="dash", line_color="#94A3B8")
    fig_shap.update_layout(height=450, paper_bgcolor="rgba(0,0,0,0)",
                           plot_bgcolor="rgba(0,0,0,0)", font_color="#F1F5F9",
                           xaxis_gridcolor="#334155")
    st.plotly_chart(fig_shap, use_container_width=True)

    # Feature values table
    st.markdown("**📋 Raw Feature Values for This Customer**")
    feature_table = pd.DataFrame({
        'Feature': [f.replace('_', ' ').title() for f in FEATURES],
        'Value': [str(round(float(v), 3)) if not np.isnan(float(v)) else 'N/A'
                  for v in input_vector.values[0]],
        'SHAP Impact': [f"{'+' if v > 0 else ''}{round(float(v), 4)}" for v in vals],
        'Effect': ['🔴 Risk' if v > 0 else '🟢 Safe' for v in vals]
    })
    st.dataframe(feature_table, use_container_width=True, hide_index=True)
