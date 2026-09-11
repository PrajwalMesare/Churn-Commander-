# 📁 Repository Structure

## 🎯 Active Codebase (Root Level)

```
Churn-Commander/
├── app.py                          # ⭐ Main Streamlit application
├── requirements.txt                # 📦 Dependencies
├── README.md                       # 📖 Documentation
├── .gitignore                      # 🔒 Git ignore rules
├── .streamlit/                     # ⚙️ Streamlit configuration
│   ├── config.toml
│   └── secrets.toml.example
│
├── utils/                          # 🛠️ Utility modules
│   ├── __init__.py
│   ├── data_loader.py
│   ├── prediction_engine.py
│   ├── ai_strategy.py
│   ├── email_generator.py
│   ├── mail_service.py
│   ├── dashboard_analytics.py
│   └── validators.py
│
├── models/                         # 🤖 ML Models
│   └── churn_model.pkl            (XGBoost, 96% accuracy)
│
├── data/                           # 📊 Sample Data
│   └── ui_data.csv                (100 customer samples)
│
└── logs/                           # 📝 Application Logs
    └── email_sent.log
```

## 📦 Archive Folder (Legacy - Not Used)

```
archive/
├── README.md                        # Archive documentation
├── customer-retention-analytics.ipynb  # Original notebook (reference only)
└── config_examples/                 # Example config files
```

## 🎯 Key Points

- **Root level:** Only essential files needed to run the app
- **utils/:** All utility modules for clean code organization
- **models/:** Pre-trained ML models
- **data/:** Sample customer data
- **logs/:** Application logs and tracking
- **archive/:** Legacy files not needed for running the app

## 🚀 For Deployment

Only these folders/files are needed:
- ✅ `app.py`
- ✅ `utils/`
- ✅ `models/`
- ✅ `data/`
- ✅ `requirements.txt`
- ✅ `.streamlit/`
- ✅ `README.md`

The `archive/` folder can be safely ignored for deployment.

