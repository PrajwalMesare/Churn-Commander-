# ⚡ Churn Commander
### AI-Powered Customer Churn Prediction & Retention Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat&logo=python)](https://python.org)
[![XGBoost](https://img.shields.io/badge/XGBoost-Classifier-orange?style=flat)](https://xgboost.readthedocs.io)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?style=flat&logo=streamlit)](https://streamlit.io)
[![Gemini](https://img.shields.io/badge/Google-Gemini_AI-4285F4?style=flat&logo=google)](https://ai.google.dev)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat)](LICENSE)

---

## 📌 Overview

**Churn Commander** is a production-grade machine learning system that predicts which customers are likely to cancel their subscription — and then uses **Generative AI** to prescribe a personalised retention strategy for each at-risk user.

Built on the **KKBOX Music Streaming dataset** (970,960 customers), it combines a high-accuracy **XGBoost predictive engine** with a **Google Gemini AI generative engine**, all deployed through an interactive **Streamlit dashboard**.

> 🎯 *"Don't just predict churn — prevent it."*

---

## 🏆 Model Performance

| Metric | Score |
|--------|-------|
| ✅ Accuracy | **96.41%** |
| 🎯 Precision (Churn Class) | **0.85** |
| 📊 Recall (Churn Class) | **0.73** |
| 📈 F1-Score (Churn Class) | **0.79** |
| 🗃️ Training Samples | **776,768** |
| 🧪 Test Samples | **194,192** |
| 📦 Total Dataset Size | **970,960 customers** |

### 🔍 Top Churn Drivers (SHAP Feature Importance)

| Feature | Importance |
|---------|-----------|
| `payment_plan_days` | 51.52% |
| `is_cancel` | 40.20% |
| `is_auto_renew` | 4.73% |
| Other features | 3.55% |

---

## 🏗️ System Architecture

```
Raw Data (KKBOX)
      │
      ▼
┌─────────────────────┐
│   Phase 1: ETL      │  ← Load members, transactions, user logs
│   Master Table      │  ← 970,960 users × 19 features
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Phase 2: Feature   │  ← Completion rate, payment plan days,
│  Engineering        │     cancellation flags, auto-renew status
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Phase 3: XGBoost   │  ← 80/20 train-test split
│  Model Training     │     n_estimators=100, max_depth=6
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Phase 4: SHAP      │  ← Explainability per prediction
│  Explainability     │     Why is THIS customer leaving?
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Phase 5: Gemini AI │  ← Personalised 3-step retention plan
│  Retention Agent    │     per at-risk customer
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Streamlit Dashboard│  ← Real-time inference + AI strategy
│  (Production UI)    │     deploy & interact
└─────────────────────┘
```

---

## ✨ Features

- 🔮 **Real-time Churn Prediction** — instant risk score for any customer
- 🧠 **SHAP Explainability** — understand *why* each customer is flagged
- 🤖 **Gemini AI Retention Agent** — auto-generates personalised 3-step intervention plans
- 📊 **Interactive Dashboard** — built with Streamlit + Plotly
- 📈 **Feature Importance Visualisation** — bar charts ranking churn drivers
- 💰 **LTV Contribution Display** — revenue at risk per customer

---

## 🛠️ Tech Stack

| Category | Tools |
|----------|-------|
| Language | Python 3.10+ |
| ML Model | XGBoost |
| Explainability | SHAP |
| GenAI | Google Gemini API, LangChain |
| Dashboard | Streamlit, Plotly |
| Data | Pandas, NumPy |
| Model Saving | Joblib |

---

## 📁 Project Structure

```
Churn-Commander/
├── customer-retention-analytics.ipynb   # Full ML pipeline (EDA → Training → SHAP)
├── app.py                               # Streamlit dashboard (production UI)
├── churn_model.pkl                      # Trained XGBoost model
├── ui_data.csv                          # Processed customer data for dashboard
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/PrajwalMesare/Churn-Commander-.git
cd Churn-Commander-
```

### 2. Install dependencies
```bash
pip install streamlit xgboost shap pandas numpy plotly joblib \
            google-generativeai langchain langchain-google-genai certifi
```

### 3. Set up your Gemini API key
Get a free key from [Google AI Studio](https://aistudio.google.com/app/apikey), then paste it into the sidebar when the app launches.

### 4. Run the dashboard
```bash
streamlit run app.py
```

---

## 📊 Dataset

- **Source:** [KKBOX Churn Prediction Challenge](https://www.kaggle.com/c/kkbox-churn-prediction-challenge) (Kaggle)
- **Size:** 970,960 customer records
- **Features:** 19 (demographics, listening behaviour, subscription details)
- **Target:** `is_churn` (binary — 1 = churned, 0 = retained)
- **Class imbalance:** ~18% churn rate

---

## 🤖 AI Retention Agent (Gemini)

For each at-risk customer, the agent receives:
- Customer ID
- Churn probability score
- Top SHAP-identified risk factor

And outputs a structured **3-step retention plan**:
```
### 📊 Risk Diagnosis
Customer shows high churn risk due to disabled auto-renewal.

### 🎯 Tactical Action Plan
* Action 1: Offer 20% loyalty discount if auto-renew re-enabled within 48hrs
* Action 2: Send personalised push notification highlighting premium features
* Action 3: Follow-up email at Day 7 if no action taken
```

---

## 👨‍💻 Author

**Prajwal Mesare**
B.Tech CSE (Data Science) — TGPCET, Nagpur | Graduating 2027

[![GitHub](https://img.shields.io/badge/GitHub-PrajwalMesare-181717?style=flat&logo=github)](https://github.com/PrajwalMesare)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat&logo=linkedin)](https://linkedin.com/in/prajwal-mesare)

---

## 📄 License

This project is licensed under the MIT License.
