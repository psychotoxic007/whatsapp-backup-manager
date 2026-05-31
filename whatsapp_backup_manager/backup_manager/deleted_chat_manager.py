"""Deleted Chat Manager for accessing deleted conversations."""

import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class DeletedChatManager:
    """Manages access to deleted chats and messages."""
    
    def __init__(self, db_path: str):
        """Initialize Deleted Chat Manager.
        
        Args:
            db_path: Path to decrypted WhatsApp database
        """
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {db_path}")
        
        logger.info(f"DeletedChatManager initialized with database: {db_path}")
    
    def get_deleted_chats(self) -> List[Dict]:
        """Get all deleted chat threads.
        
        Returns:
            List of deleted chat information
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Query for deleted chats (marked with delete flag)
            query = """
                SELECT 
                    chat._id,
                    chat.subject,
                    chat.creation,
                    chat.last_message_table_id,
                    jid.user,
                    jid.agent,
                    jid.device,
                    COUNT(DISTINCT message._id) as message_count
                FROM chat
                LEFT JOIN jid ON chat.jid_row_id = jid._id
                LEFT JOIN message ON message.chat_row_id = chat._id
                WHERE chat.hidden = 1 OR chat.deleted = 1
                GROUP BY chat._id
                ORDER BY chat.last_message_table_id DESC
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            deleted_chats = []
            for row in rows:
                deleted_chats.append({
                    'id': row['_id'],
                    'name': row['subject'] or row['user'] or f"Chat_{row['_id']}",
                    'jid': row['user'],
                    'creation_time': row['creation'],
                    'message_count': row['message_count'] or 0
                })
            
            conn.close()
            logger.info(f"Found {len(deleted_chats)} deleted chats")
            return deleted_chats
        
        except sqlite3.Error as e:
            logger.error(f"Error retrieving deleted chats: {e}")
            raise
    
    def get_deleted_messages(self, chat_id: Optional[int] = None, limit: int = 100) -> List[Dict]:
        """Get deleted messages from chats.
        
        Args:
            chat_id: Optional specific chat ID
            limit: Maximum messages to retrieve
            
        Returns:
            List of deleted messages
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Messages marked as deleted (status = -1) or from hidden chats
            if chat_id:
                query = """
                    SELECT 
                        message._id,
                        message.chat_row_id,
                        message.from_me,
                        message.timestamp,
                        message.text_data,
                        message.status,
                        message.message_type,
                        message.media_name,
                        message.media_url,
                        chat.subject,
                        jid.user
                    FROM message
                    JOIN chat ON message.chat_row_id = chat._id
                    LEFT JOIN jid ON chat.jid_row_id = jid._id
                    WHERE message.chat_row_id = ? AND (message.status = -1 OR chat.hidden = 1)
                    ORDER BY message.timestamp DESC
                    LIMIT ?
                """
                cursor.execute(query, (chat_id, limit))
            else:
                query = """
                    SELECT 
                        message._id,
                        message.chat_row_id,
                        message.from_me,
                        message.timestamp,
                        message.text_data,
                        message.status,
                        message.message_type,
                        message.media_name,
                        message.media_url,
                        chat.subject,
                        jid.user
                    FROM message
                    JOIN chat ON message.chat_row_id = chat._id
                    LEFT JOIN jid ON chat.jid_row_id = jid._id
                    WHERE message.status = -1 OR chat.hidden = 1
                    ORDER BY message.timestamp DESC
                    LIMIT ?
                """
                cursor.execute(query, (limit,))
            
            rows = cursor.fetchall()
            
            deleted_messages = []
            for row in rows:
                deleted_messages.append({
                    'id': row['_id'],
                    'chat_id': row['chat_row_id'],
                    'chat_name': row['subject'] or row['user'] or 'Unknown',
                    'from_me': row['from_me'],
                    'timestamp': row['timestamp'],
                    'text': row['text_data'],
                    'status': row['status'],
                    'message_type': row['message_type'],
                    'media_name': row['media_name'],
                    'media_url': row['media_url'],
                    'date': datetime.fromtimestamp(row['timestamp'] / 1000).isoformat() if row['timestamp'] else None
                })
            
            conn.close()
            logger.info(f"Found {len(deleted_messages)} deleted messages")
            return deleted_messages
        
        except sqlite3.Error as e:
            logger.error(f"Error retrieving deleted messages: {e}")
            raise
    
    def restore_deleted_chat_info(self, chat_id: int) -> Dict:
        """Restore information about a deleted chat.
        
        Args:
            chat_id: Chat ID to restore
            
        Returns:
            Dictionary with restored chat information
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    chat._id,
                    chat.subject,
                    chat.creation,
                    chat.last_message_table_id,
                    jid.user,
                    COUNT(DISTINCT message._id) as message_count,
                    MIN(message.timestamp) as first_message,
                    MAX(message.timestamp) as last_message
                FROM chat
                LEFT JOIN jid ON chat.jid_row_id = jid._id
                LEFT JOIN message ON message.chat_row_id = chat._id
                WHERE chat._id = ?
                GROUP BY chat._id
            """, (chat_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return {}
            
            return {
                'id': row['_id'],
                'name': row['subject'] or row['user'] or f"Chat_{row['_id']}",
                'jid': row['user'],
                'creation_time': row['creation'],
                'message_count': row['message_count'] or 0,
                'first_message_time': row['first_message'],
                'last_message_time': row['last_message'],
                'date_created': datetime.fromtimestamp(row['creation'] / 1000).isoformat() if row['creation'] else None,
                'date_first_msg': datetime.fromtimestamp(row['first_message'] / 1000).isoformat() if row['first_message'] else None,
                'date_last_msg': datetime.fromtimestamp(row['last_message'] / 1000).isoformat() if row['last_message'] else None
            }
        
        except sqlite3.Error as e:
            logger.error(f"Error restoring chat info: {e}")
            return {}
    
    def export_deleted_chats(self, output_file: str, format: str = 'json') -> bool:
        """Export deleted chats to file.
        
        Args:
            output_file: Output file path
            format: Export format (json, csv)
            
        Returns:
            True if successful
        """
        try:
            import json
            import csv
            
            deleted_chats = self.get_deleted_chats()
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if format == 'json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(deleted_chats, f, indent=2, ensure_ascii=False, default=str)
                logger.info(f"Exported {len(deleted_chats)} deleted chats to {output_file}")
            
            elif format == 'csv':
                if not deleted_chats:
                    logger.warning("No deleted chats to export")
                    return False
                
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=deleted_chats[0].keys())
                    writer.writeheader()
                    writer.writerows(deleted_chats)
                logger.info(f"Exported {len(deleted_chats)} deleted chats to {output_file}")
            
            return True
        
        except Exception as e:
            logger.error(f"Error exporting deleted chats: {e}")
            return False
    
    def export_deleted_messages(self, output_file: str, chat_id: Optional[int] = None,
                               format: str = 'json', limit: int = 10000) -> bool:
        """Export deleted messages to file.
        
        Args:
            output_file: Output file path
            chat_id: Optional specific chat
            format: Export format (json, csv)
            limit: Maximum messages
            
        Returns:
            True if successful
        """
        try:
            import json
            import csv
            
            deleted_messages = self.get_deleted_messages(chat_id, limit)
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if format == 'json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(deleted_messages, f, indent=2, ensure_ascii=False, default=str)
                logger.info(f"Exported {len(deleted_messages)} deleted messages to {output_file}")
            
            elif format == 'csv':
                if not deleted_messages:
                    logger.warning("No deleted messages to export")
                    return False
                
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=deleted_messages[0].keys())
                    writer.writeheader()
                    writer.writerows(deleted_messages)
                logger.info(f"Exported {len(deleted_messages)} deleted messages to {output_file}")
            
            return True
        
        except Exception as e:
            logger.error(f"Error exporting deleted messages: {e}")
            return False
