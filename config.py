# Configuration settings
DATABASE_CONFIG = {
    'db_name': 'student_database.db',
    'backup_enabled': True,
    'backup_path': 'backups/'
}

ML_MODEL_CONFIG = {
    'model_path': 'dropout_model.pkl',
    'retrain_interval_days': 30,
    'risk_threshold_high': 70,
    'risk_threshold_medium': 40
}

NOTIFICATION_CONFIG = {
    'send_mentor_alerts': True,
    'send_guardian_alerts': True,
    'alert_schedule': 'weekly',  # daily, weekly, monthly
    'min_risk_score_for_guardian': 70
}

DASHBOARD_CONFIG = {
    'refresh_interval': 300,  # seconds
    'max_students_display': 50,
    'enable_export': True
}
# Add this dictionary to your config.py file
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 465, # Port for SSL
    'sender_email': 'choudhuryankit97@gmail.com.com',  # <-- REPLACE with your Gmail address
    'sender_password': '' # <-- REPLACE with your 16-character App Password
}