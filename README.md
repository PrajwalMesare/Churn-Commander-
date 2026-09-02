# 🎵 CHURN COMMANDER v2.0
## AI-Powered Customer Retention Platform

![Version](https://img.shields.io/badge/version-2.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-green.svg)
![Status](https://img.shields.io/badge/status-active-brightgreen.svg)

---

## ✨ **NEW IN v2.0 - 3 MAJOR FEATURES**

### **Feature 1: Flexible Customer Data Upload** 📁
- Upload any CSV with customer data
- Supports 970K+ KKBOX dataset or your own customers
- Automatic validation and feature extraction
- Real-time scaling capabilities

### **Feature 2: Personalized Email Sender** ✉️
- Gemini AI generates 3 personalized offers
- HTML + Plain text email templates  
- Direct SMTP sending (Gmail or SendGrid)
- Automatic email logging and tracking
- GDPR-compliant unsubscribe links

### **Feature 3: Company Dashboard** 📊
- Real-time KPIs (customers, churn risk, revenue at risk)
- Risk distribution and customer segmentation
- Email campaign performance tracking
- Export analysis as CSV
- Quick actionable insights

### **Existing Features** ✅
- Individual customer churn prediction (96% accuracy)
- SHAP feature explainability
- AI retention strategy generation
- Behavioral analytics

---

## 🚀 **Quick Start (3 Steps)**

### **1. Clone & Install**
```bash
git clone https://github.com/PrajwalMesare/Churn-Commander-.git
cd Churn-Commander-
pip install -r requirements.txt
```

### **2. Setup Secrets**
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit with your API keys:
# - GEMINI_API_KEY from https://makersuite.google.com
# - EMAIL_SENDER & EMAIL_PASSWORD for Gmail
```

### **3. Run App**
```bash
streamlit run app.py
```

---

## 📊 **Model Performance**

| Metric | Value |
|--------|-------|
| Accuracy | 96.41% |
| Precision | 0.85 |
| Recall | 0.73 |
| F1-Score | 0.79 |
| Dataset | 970,960 customers |

---

## 🏗️ **Architecture**

```
Churn Commander v2.0
├── app.py (3 Tabs: Analysis | Dashboard | Data)
├── utils/ (7 modules for separation of concerns)
│   ├── data_loader.py
│   ├── prediction_engine.py
│   ├── ai_strategy.py
│   ├── email_generator.py
│   ├── mail_service.py
│   ├── dashboard_analytics.py
│   └── validators.py
├── models/
│   └── churn_model.pkl (XGBoost)
└── data/
    └── ui_data.csv (100-970K customers)
```

---

## 📖 **Usage**

### **Tab 1: Customer Analysis**
1. Upload CSV or use default data
2. Select customer
3. View churn risk, AI strategy, analytics, SHAP explanation
4. **Generate & send personalized email** ⭐ NEW

### **Tab 2: Company Dashboard** ⭐ NEW
- View company-wide KPIs
- Risk distribution across customers
- Email campaign stats
- Export risk lists

### **Tab 3: Data Management** ⭐ NEW
- Upload your own customer CSV
- View data preview & statistics
- Download processed data

---

## 📧 **Email Setup**

### **Gmail SMTP**
1. Enable 2FA on Gmail
2. Create App Password: https://myaccount.google.com/apppasswords
3. Add to secrets.toml:
```toml
EMAIL_SENDER = "your.email@gmail.com"
EMAIL_PASSWORD = "your-app-password"
```

### **SendGrid** (Production)
1. Create account at sendgrid.com
2. Generate API Key
3. Add to secrets.toml:
```toml
SENDGRID_API_KEY = "SG.xxxxx"
```

---

## 📁 **Project Structure**

```
Churn-Commander-/
├── app.py                          # Main app (v2.0)
├── utils/                          # 7 utility modules
│   ├── data_loader.py
│   ├── prediction_engine.py
│   ├── ai_strategy.py
│   ├── email_generator.py
│   ├── mail_service.py
│   ├── dashboard_analytics.py
│   └── validators.py
├── .streamlit/
│   ├── config.toml
│   ├── secrets.toml (ignored)
│   └── secrets.toml.example
├── models/
│   └── churn_model.pkl
├── data/
│   └── ui_data.csv
├── logs/
│   └── email_sent.log
├── requirements.txt                # All dependencies
└── README.md
```

---

## 🛠️ **Tech Stack**

- **Frontend:** Streamlit 1.31.0
- **ML:** XGBoost 2.0.3, SHAP 0.43.0
- **AI:** Google Generative AI (Gemini)
- **Email:** SMTP (Gmail) / SendGrid API
- **Data:** Pandas, NumPy, Plotly
- **Validation:** email-validator, cryptography

---

## 🧪 **Features Checklist**

**Old Features (v1.0)** ✅
- [x] Churn prediction (96.41% accuracy)
- [x] SHAP explainability
- [x] AI retention strategy (Gemini)
- [x] Behavioral analytics

**New Features (v2.0)** ⭐
- [x] Flexible CSV data upload (Feature 1)
- [x] Personalized email sender (Feature 2)
- [x] Company dashboard (Feature 3)
- [x] Email logging & tracking
- [x] Rate limiting & error handling
- [x] Input validation & sanitization
- [x] 7 modular utility files
- [x] Comprehensive documentation

---

## 🚢 **Deployment**

### **Streamlit Cloud** (Recommended)
1. Push to GitHub
2. Go to share.streamlit.io
3. Connect repo and deploy
4. Add secrets in Settings

### **Docker**
```bash
docker build -t churn-commander .
docker run -p 8501:8501 churn-commander
```

### **Local**
```bash
streamlit run app.py
```

---

## 🐛 **Troubleshooting**

| Issue | Solution |
|-------|----------|
| Model not loading | Check churn_model.pkl exists |
| Gemini errors | Verify API key in secrets.toml |
| Email not sending | Test connection, check App Password |
| CSV upload fails | Ensure 12 required columns |

---

## 👨‍💼 **Author**

**Prajwal Mesare**  
- B.Tech Computer Science (Data Science)  
- TGPCET Nagpur | Batch 2027
- GitHub: [@PrajwalMesare](https://github.com/PrajwalMesare)
- LinkedIn: [Profile](https://linkedin.com/in/prajwal-mesare-700678263)

---

## 📝 **License**

MIT License

---

**Version:** 2.0 | **Status:** ✅ Production Ready | **Last Updated:** Sep 2, 2024
