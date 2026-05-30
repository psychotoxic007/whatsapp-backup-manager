"""Configuration settings loader."""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict


def load_config() -> Dict:
    """Load configuration from environment variables.
    
    Returns:
        Configuration dictionary
    """
    # Load .env file
    env_file = Path(__file__).parent.parent / '.env'
    if env_file.exists():
        load_dotenv(env_file)
    else:
        load_dotenv()
    
    config = {
        # Google Drive
        'GOOGLE_DRIVE_CREDENTIALS_PATH': os.getenv('GOOGLE_DRIVE_CREDENTIALS_PATH', './credentials.json'),
        'GOOGLE_DRIVE_ENABLED': os.getenv('GOOGLE_DRIVE_ENABLED', 'false').lower() == 'true',
        
        # Storage
        'BACKUP_STORAGE_PATH': os.getenv('BACKUP_STORAGE_PATH', './backups'),
        'MEDIA_STORAGE_PATH': os.getenv('MEDIA_STORAGE_PATH', './media'),
        'REPORT_STORAGE_PATH': os.getenv('REPORT_STORAGE_PATH', './reports'),
        
        # Database
        'DATABASE_PATH': os.getenv('DATABASE_PATH', './data/whatsapp.db'),
        'DATABASE_TIMEOUT': int(os.getenv('DATABASE_TIMEOUT', '30')),
        
        # Logging
        'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
        'LOG_FILE': os.getenv('LOG_FILE', './logs/app.log'),
        
        # Application
        'DEBUG': os.getenv('DEBUG', 'false').lower() == 'true',
        'MAX_WORKERS': int(os.getenv('MAX_WORKERS', '4')),
    }
    
    return config
