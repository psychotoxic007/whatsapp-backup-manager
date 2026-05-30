"""WhatsApp Database Reader - Access and parse WhatsApp database files."""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class WhatsAppDatabaseReader:
    """Reads and manages WhatsApp database files."""

    # Common WhatsApp database filenames
    COMMON_DB_NAMES = {
        'messages': ['msgstore.db', 'messages.db'],
        'contacts': ['contacts.db', 'wa.db'],
        'chat_list': ['chat_list.db'],
        'groups': ['groups.db']
    }

    def __init__(self, db_path: str):
        """Initialize WhatsApp Database Reader.
        
        Args:
            db_path: Path to the WhatsApp database file (.db or decrypted)
        """
        self.db_path = Path(db_path)
        self.connection = None
        self.cursor = None
        self.db_type = self._detect_db_type()
        
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database file not found: {db_path}")
        
        logger.info(f"WhatsAppDatabaseReader initialized for: {db_path}")

    def connect(self) -> bool:
        """Connect to the database.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.connection = sqlite3.connect(str(self.db_path))
            self.connection.row_factory = sqlite3.Row  # Access columns by name
            self.cursor = self.connection.cursor()
            logger.info(f"Connected to database: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False

    def disconnect(self) -> None:
        """Disconnect from the database."""
        if self.connection:
            self.connection.close()
            logger.info("Disconnected from database")

    def get_tables(self) -> List[str]:
        """Get list of all tables in the database.
        
        Returns:
            List of table names
        """
        try:
            self.cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = [row[0] for row in self.cursor.fetchall()]
            logger.info(f"Found {len(tables)} tables")
            return tables
        except Exception as e:
            logger.error(f"Error getting tables: {e}")
            return []

    def get_table_schema(self, table_name: str) -> Dict:
        """Get schema information for a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dictionary with column information
        """
        try:
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            columns = self.cursor.fetchall()
            
            schema = {
                'table_name': table_name,
                'columns': []
            }
            
            for col in columns:
                schema['columns'].append({
                    'name': col[1],
                    'type': col[2],
                    'not_null': bool(col[3]),
                    'default': col[4],
                    'primary_key': bool(col[5])
                })
            
            return schema
        except Exception as e:
            logger.error(f"Error getting table schema: {e}")
            return {}

    def query_table(self, table_name: str, limit: Optional[int] = None) -> List[Dict]:
        """Query all rows from a table.
        
        Args:
            table_name: Name of the table
            limit: Maximum number of rows to return
            
        Returns:
            List of row dictionaries
        """
        try:
            if limit:
                self.cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
            else:
                self.cursor.execute(f"SELECT * FROM {table_name}")
            
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error querying table {table_name}: {e}")
            return []

    def search_in_table(self, table_name: str, column: str, 
                       value: str, exact_match: bool = False) -> List[Dict]:
        """Search for values in a table.
        
        Args:
            table_name: Name of the table
            column: Column to search in
            value: Value to search for
            exact_match: If True, use exact match; else use LIKE
            
        Returns:
            List of matching rows
        """
        try:
            if exact_match:
                query = f"SELECT * FROM {table_name} WHERE {column} = ?"
                self.cursor.execute(query, (value,))
            else:
                query = f"SELECT * FROM {table_name} WHERE {column} LIKE ?"
                self.cursor.execute(query, (f"%{value}%",))
            
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error searching table {table_name}: {e}")
            return []

    def get_table_row_count(self, table_name: str) -> int:
        """Get number of rows in a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Number of rows
        """
        try:
            self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            return self.cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error counting rows in {table_name}: {e}")
            return 0

    def export_table_to_json(self, table_name: str, output_path: str) -> bool:
        """Export table to JSON file.
        
        Args:
            table_name: Name of the table
            output_path: Path to save JSON file
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            import json
            rows = self.query_table(table_name)
            
            # Convert datetime objects to strings
            for row in rows:
                for key, value in row.items():
                    if isinstance(value, datetime):
                        row[key] = value.isoformat()
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(rows, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(rows)} rows from {table_name} to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting table to JSON: {e}")
            return False

    def export_table_to_csv(self, table_name: str, output_path: str) -> bool:
        """Export table to CSV file.
        
        Args:
            table_name: Name of the table
            output_path: Path to save CSV file
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            import csv
            rows = self.query_table(table_name)
            
            if not rows:
                logger.warning(f"No data to export from {table_name}")
                return False
            
            # Get column names
            columns = list(rows[0].keys())
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=columns)
                writer.writeheader()
                writer.writerows(rows)
            
            logger.info(f"Exported {len(rows)} rows from {table_name} to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting table to CSV: {e}")
            return False

    def get_database_info(self) -> Dict:
        """Get comprehensive database information.
        
        Returns:
            Dictionary with database metadata
        """
        try:
            tables = self.get_tables()
            info = {
                'file_path': str(self.db_path),
                'file_size': self.db_path.stat().st_size,
                'type': self.db_type,
                'tables': {},
                'total_rows': 0
            }
            
            for table in tables:
                row_count = self.get_table_row_count(table)
                info['tables'][table] = {
                    'row_count': row_count,
                    'schema': self.get_table_schema(table)
                }
                info['total_rows'] += row_count
            
            return info
        except Exception as e:
            logger.error(f"Error getting database info: {e}")
            return {}

    def _detect_db_type(self) -> str:
        """Detect the type of WhatsApp database.
        
        Returns:
            Database type identifier
        """
        filename = self.db_path.name.lower()
        
        if 'msgstore' in filename or 'messages' in filename:
            return 'messages'
        elif 'contact' in filename:
            return 'contacts'
        elif 'chat_list' in filename:
            return 'chat_list'
        elif 'groups' in filename:
            return 'groups'
        else:
            return 'unknown'
