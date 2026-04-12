import streamlit as st
import pandas as pd
import joblib
import shap
import google.generativeai as genai
import os
import ssl
import certifi
import plotly.express as px
import numpy as np

# --- 1. CORE CONFIGURATION ---
os.environ['SSL_CERT_FILE'] = certifi.where()
ssl._create_default_https_context = ssl._create_unverified_context

# Initialize the UI Theme
st.set_page_config(page_title="Churn Commander", layout="wide", page_icon="⚡")

# --- PREMIUM CSS STYLING ---
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 95%; }
    h1, h2, h3 { font-family: 'Inter', sans-serif; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; font-size: 16px; font-weight: 600; }
    /* Updated AI Box with dark text color (#0F172A) so it's visible in Dark Mode */
    .ai-box { background: linear-gradient(145deg, #F8FAFC, #EFF6FF); border-left: 4px solid #3B82F6; padding: 20px; border-radius: 8px; color: #0F172A; }
    </style>
""", unsafe_allow_html=True)

# --- 2. DATA ARCHITECTURE ---
@st.cache_resource(show_spinner=False)
def load_production_assets():
    model = joblib.load('churn_model.pkl')
    df = pd.read_csv('ui_data.csv')
    return model, df

# --- 3. SIDEBAR NAVIGATION & API INPUT ---
with st.sidebar:
    st.title("⚡ Commander Hub")
    
    # NEW: Secure API Key Input UI
    st.markdown("### 🔑 System Config")
    user_api_key = st.text_input("Google Gemini API Key", type="password", placeholder="Paste key here...", help="Get this from Google AI Studio")
    
    # Configure GenAI dynamically if the user types a key
    if user_api_key:
        genai.configure(api_key=user_api_key)

    st.markdown("---")
    
    # Target Selection
    st.markdown("### 🎯 Target Selection")
    xgb_model, ui_data = load_production_assets()
    selected_index = st.selectbox(
        "Select Target Account", 
        ui_data.index, 
        format_func=lambda x: f"ID: {str(ui_data.iloc[x]['msno'])[:10]}..."
    )
    
    st.markdown("---")
    
    # Quick Summary in Sidebar
    current_customer = ui_data.iloc[[selected_index]]
    account_id = current_customer['msno'].values[0]
    st.caption("Active Account Details:")
    st.write(f"**Tenure:** {current_customer['payment_plan_days'].values[0]} days")
    st.write(f"**Auto-Renew:** {'Yes' if current_customer['is_auto_renew'].values[0] == 1 else 'No'}")

# --- 4. FIXING THE AI AGENT ---
def generate_retention_strategy(account_id, risk_score, top_driver):
    # Updated error message to point to the new sidebar UI
    if not user_api_key:
        return "🛑 **API KEY MISSING:** Please paste your Google Gemini API Key into the sidebar panel on the left to activate the AI Agent."

    system_prompt = f"""
    You are an elite Customer Success AI. Analyze this user and provide a 3-step retention plan.
    Target Account: {account_id}
    Churn Probability: {risk_score}%
    Primary Risk Factor Identified: {top_driver}
    
    Format output strictly as:
    ### 📊 Risk Diagnosis
    (1-2 sentences)
    ### 🎯 Tactical Action Plan
    * **Action 1:** (Specific offer/nudge)
    * **Action 2:** (Specific communication)
    * **Action 3:** (Follow-up timeline)
    """
    
    # Updated to the newer model tier to prevent 404 errors
    llm = genai.GenerativeModel('gemini-2.5-flash')
    response = llm.generate_content(system_prompt)
    return response.text

# --- 5. DATA PROCESSING & INFERENCE ---
FEATURES = [
    'city', 'bd', 'registered_via', 'num_100', 'num_25', 
    'total_secs', 'completion_rate', 'payment_plan_days', 
    'plan_list_price', 'actual_amount_paid', 'is_auto_renew', 'is_cancel'
]

input_vector = current_customer[FEATURES].apply(pd.to_numeric, errors='coerce')
churn_prob = xgb_model.predict_proba(input_vector)[0][1]
risk_percentage = round(float(churn_prob) * 100, 2)

explainer = shap.TreeExplainer(xgb_model)
shap_values = explainer.shap_values(input_vector)
vals = shap_values[0][:, 1] if len(shap_values.shape) == 3 else shap_values[0]
top_risk_feature = FEATURES[vals.argmax()]

# --- 6. DASHBOARD HEADER ---
st.markdown(f"<h1>Customer Intelligence Hub</h1>", unsafe_allow_html=True)
st.write(f"Analyzing behavioral telemetry for account `{account_id}`")
st.markdown("<br>", unsafe_allow_html=True)

# Top Metrics Row
col1, col2, col3 = st.columns(3)
with col1:
    with st.container(border=True):
        st.metric(label="Predicted Churn Risk", value=f"{risk_percentage}%", delta="Critical" if risk_percentage > 50 else "Stable", delta_color="inverse")
        st.progress(int(risk_percentage))

with col2:
    with st.container(border=True):
        st.metric(label="Primary Churn Driver", value=top_risk_feature.replace('_', ' ').title())
        st.caption("Highest impact feature via SHAP analysis")

with col3:
    with st.container(border=True):
        paid = current_customer['actual_amount_paid'].values[0]
        st.metric(label="Customer LTV Contribution", value=f"${paid}")
        st.caption("Total revenue generated this period")

st.markdown("<br>", unsafe_allow_html=True)

# --- 7. DETAILED TABS ---
tab1, tab2 = st.tabs(["🤖 AI Strategy Generation", "📈 Behavioral Telemetry"])

with tab1:
    st.markdown("### Prescriptive Intervention")
    st.write("Deploy the Gemini generative engine to build a custom retention campaign for this specific user.")
    
    if st.button("⚡ Generate AI Strategy Plan", type="primary", use_container_width=False):
        with st.spinner("Connecting to Gemini Engine... Analyzing SHAP vectors..."):
            strategy_output = generate_retention_strategy(
                account_id=account_id,
                risk_score=risk_percentage,
                top_driver=top_risk_feature
            )
        st.markdown(f'<div class="ai-box">{strategy_output}</div>', unsafe_allow_html=True)

with tab2:
    st.markdown("### Engagement Trajectory")
    st.write("Simulated recent activity based on completion rates.")
    
    mock_dates = pd.date_range(end=pd.Timestamp.today(), periods=7)
    mock_engagement = np.random.uniform(low=20, high=100, size=(7,)) * (current_customer['completion_rate'].values[0] + 0.1)
    
    chart_data = pd.DataFrame({"Date": mock_dates, "Engagement Score": mock_engagement})
    fig = px.line(chart_data, x="Date", y="Engagement Score", markers=True, line_shape="spline")
    
    # Fixed chart colors to look better in dark mode
    fig.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="#334155")
    
    st.plotly_chart(fig, use_container_width=True)