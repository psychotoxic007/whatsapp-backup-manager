"""Analytics Manager for WhatsApp database analysis and contact lookup."""

import sqlite3
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class AnalyticsManager:
    """Parses decrypted WhatsApp SQLite databases and crosses names with wa.db sync data."""
    
    def __init__(self, db_path: str):
        """Initialize Analytics Manager.
        
        Args:
            db_path: Path to decrypted WhatsApp database file
        """
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database file not found at: {db_path}")
            
        # Target the parallel contact file path
        self.wa_db_path = self.db_path.parent / "wa_decrypted.db"
    
    def get_basic_stats(self) -> dict:
        """Fetch general statistics from the database.
        
        Returns:
            Dictionary with message and chat statistics
        """
        stats = {}
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM message")
            stats['total_messages'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM chat")
            stats['total_chats'] = cursor.fetchone()[0]
            
            try:
                cursor.execute("""
                    SELECT 
                        SUM(CASE WHEN message_type = 0 THEN 1 ELSE 0 END) as text_msgs,
                        SUM(CASE WHEN message_type != 0 THEN 1 ELSE 0 END) as media_msgs
                    FROM message
                """)
                row = cursor.fetchone()
                stats['text_messages'] = row[0] or 0
                stats['media_messages'] = row[1] or 0
            except sqlite3.Error:
                stats['text_messages'] = "N/A"
                stats['media_messages'] = "N/A"
            
            conn.close()
            return stats
        except sqlite3.Error as e:
            logger.error(f"SQLite error running stats: {e}")
            raise

    def get_top_contacts(self, limit: int = -1) -> list:
        """Fetch active conversations with contact name resolution.
        
        Joins with wa_decrypted.db to resolve contact names.
        
        Args:
            limit: Number of contacts to return (-1 for all)
            
        Returns:
            List of tuples (contact_name, message_count)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # ATTACH the contact database if it exists locally
            has_contacts = False
            if self.wa_db_path.exists():
                cursor.execute(f"ATTACH DATABASE '{str(self.wa_db_path)}' AS wa_db")
                has_contacts = True
            
            limit_clause = f"LIMIT {limit}" if limit > 0 else ""
            
            # If we have wa.db, join it to resolve contact names
            if has_contacts:
                query = f"""
                    SELECT 
                        COALESCE(chat.subject, wa_db.wa_contacts.display_name, wa_db.wa_contacts.given_name, jid.user, 'Unknown Thread') as chat_name,
                        COUNT(message._id) as msg_count 
                    FROM message 
                    JOIN chat ON message.chat_row_id = chat._id
                    LEFT JOIN jid ON chat.jid_row_id = jid._id
                    LEFT JOIN wa_db.wa_contacts ON jid.user = wa_db.wa_contacts.jid
                    GROUP BY message.chat_row_id
                    ORDER BY msg_count DESC
                    {limit_clause}
                """
            else:
                # Fallback to standard jid fields if wa.db isn't found yet
                query = f"""
                    SELECT 
                        COALESCE(chat.subject, jid.user, 'Unknown Thread') as chat_name,
                        COUNT(message._id) as msg_count 
                    FROM message 
                    JOIN chat ON message.chat_row_id = chat._id
                    LEFT JOIN jid ON chat.jid_row_id = jid._id
                    GROUP BY message.chat_row_id
                    ORDER BY msg_count DESC
                    {limit_clause}
                """
                
            cursor.execute(query)
            results = cursor.fetchall()
            conn.close()
            return results
        except sqlite3.Error as e:
            logger.error(f"Failed to resolve contact names: {e}")
            return [("Active Thread", 0)]

    def get_chat_messages(self, search_name: str, limit: int = 20) -> list:
        """Fetch recent messages with contact book lookup support.
        
        Args:
            search_name: Name or JID to search for
            limit: Number of messages to return
            
        Returns:
            List of tuples (from_me, message_text, timestamp)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            has_contacts = False
            if self.wa_db_path.exists():
                cursor.execute(f"ATTACH DATABASE '{str(self.wa_db_path)}' AS wa_db")
                has_contacts = True
                
            if has_contacts:
                cursor.execute("""
                    SELECT chat._id FROM chat 
                    LEFT JOIN jid ON chat.jid_row_id = jid._id
                    LEFT JOIN wa_db.wa_contacts ON jid.user = wa_db.wa_contacts.jid
                    WHERE chat.subject LIKE ? 
                       OR jid.user LIKE ? 
                       OR wa_db.wa_contacts.display_name LIKE ?
                    LIMIT 1
                """, (f"%{search_name}%", f"%{search_name}%", f"%{search_name}%"))
            else:
                cursor.execute("""
                    SELECT _id FROM chat 
                    WHERE subject LIKE ? OR jid_row_id IN (SELECT _id FROM jid WHERE user LIKE ?)
                    LIMIT 1
                """, (f"%{search_name}%", f"%{search_name}%"))
            
            chat_row = cursor.fetchone()
            if not chat_row:
                return []
                
            chat_id = chat_row[0]
            
            cursor.execute("PRAGMA table_info(message)")
            columns = [col[1] for col in cursor.fetchall()]
            text_column = "text_data" if "text_data" in columns else "message_text"
            
            query = f"""
                SELECT from_me, {text_column}, timestamp 
                FROM message 
                WHERE chat_row_id = ? AND {text_column} IS NOT NULL
                ORDER BY _id DESC 
                LIMIT ?
            """
            cursor.execute(query, (chat_id, limit))
            messages = cursor.fetchall()
            conn.close()
            return list(reversed(messages))
        except sqlite3.Error as e:
            logger.error(f"Error reading chat history: {e}")
            return []
