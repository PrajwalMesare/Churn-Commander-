"""
Churn Commander Utils Package
Contains all utility modules for data processing, prediction, and email services
"""

from .data_loader import (
    load_csv, validate_csv_structure, get_customer_info_dict,
    extract_features, load_default_data
)

from .prediction_engine import (
    load_model, predict_churn, get_risk_level, get_shap_values,
    get_top_risk_drivers, model_performance_metrics
)

from .ai_strategy import (
    configure_gemini, generate_retention_strategy,
    generate_personalized_offer, get_fallback_strategies,
    get_fallback_offers
)

from .email_generator import (
    create_email_template, generate_email_draft,
    format_email_for_preview, validate_email_draft,
    get_email_statistics
)

from .mail_service import (
    validate_email_address, setup_smtp_connection,
    send_email_smtp, log_email_sent, read_email_logs,
    test_email_connection, close_smtp_connection,
    get_gmail_smtp_config, get_sendgrid_config
)

from .dashboard_analytics import (
    calculate_company_kpis, get_churn_distribution,
    get_top_risk_drivers, segment_customers_by_risk,
    calculate_retention_potential, get_quick_insights,
    export_to_csv, get_churn_by_demographic
)

from .validators import (
    validate_api_key, sanitize_input, validate_customer_id,
    validate_feature_range, check_system_health,
    validate_feature_vector, check_rate_limit,
    validate_bulk_operation
)

__all__ = [
    # data_loader
    'load_csv', 'validate_csv_structure', 'get_customer_info_dict',
    'extract_features', 'load_default_data',
    
    # prediction_engine
    'load_model', 'predict_churn', 'get_risk_level', 'get_shap_values',
    'get_top_risk_drivers', 'model_performance_metrics',
    
    # ai_strategy
    'configure_gemini', 'generate_retention_strategy',
    'generate_personalized_offer', 'get_fallback_strategies',
    'get_fallback_offers',
    
    # email_generator
    'create_email_template', 'generate_email_draft',
    'format_email_for_preview', 'validate_email_draft',
    'get_email_statistics',
    
    # mail_service
    'validate_email_address', 'setup_smtp_connection',
    'send_email_smtp', 'log_email_sent', 'read_email_logs',
    'test_email_connection', 'close_smtp_connection',
    'get_gmail_smtp_config', 'get_sendgrid_config',
    
    # dashboard_analytics
    'calculate_company_kpis', 'get_churn_distribution',
    'get_top_risk_drivers', 'segment_customers_by_risk',
    'calculate_retention_potential', 'get_quick_insights',
    'export_to_csv', 'get_churn_by_demographic',
    
    # validators
    'validate_api_key', 'sanitize_input', 'validate_customer_id',
    'validate_feature_range', 'check_system_health',
    'validate_feature_vector', 'check_rate_limit',
    'validate_bulk_operation'
]
