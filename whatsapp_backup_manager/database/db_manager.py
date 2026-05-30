"""Database Manager for handling backup metadata and cache."""

from pathlib import Path
import sqlite3
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database for storing backup metadata."""

    def __init__(self, db_path: str):
        """Initialize DatabaseManager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = None
        self.init_database()

    def init_database(self) -> None:
        """Initialize database tables."""
        try:
            self.connection = sqlite3.connect(str(self.db_path))
            cursor = self.connection.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS backups (
                    id TEXT PRIMARY KEY,
                    path TEXT NOT NULL,
                    created_at TIMESTAMP,
                    size INTEGER,
                    status TEXT,
                    metadata TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS media (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    backup_id TEXT NOT NULL,
                    file_path TEXT,
                    file_type TEXT,
                    size INTEGER,
                    created_at TIMESTAMP,
                    FOREIGN KEY (backup_id) REFERENCES backups(id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    backup_id TEXT NOT NULL,
                    analysis_type TEXT,
                    results TEXT,
                    created_at TIMESTAMP,
                    FOREIGN KEY (backup_id) REFERENCES backups(id)
                )
            ''')
            
            self.connection.commit()
            logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")

    def close(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
