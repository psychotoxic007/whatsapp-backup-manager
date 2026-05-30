"""Message Extractor - Extract and analyze messages from WhatsApp database."""

from typing import Dict, List, Optional
import logging
from datetime import datetime
from .whatsapp_db_reader import WhatsAppDatabaseReader

logger = logging.getLogger(__name__)


class MessageExtractor:
    """Extracts and processes messages from WhatsApp databases."""

    def __init__(self, db_reader: WhatsAppDatabaseReader):
        """Initialize Message Extractor.
        
        Args:
            db_reader: WhatsAppDatabaseReader instance
        """
        self.db_reader = db_reader
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_all_messages(self, limit: Optional[int] = None) -> List[Dict]:
        """Get all messages from database.
        
        Args:
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of message dictionaries
        """
        try:
            # Common message table names
            message_tables = ['messages', 'message', 'chat_messages', 'wa_messages']
            
            for table_name in message_tables:
                tables = self.db_reader.get_tables()
                if table_name in tables:
                    return self.db_reader.query_table(table_name, limit)
            
            self.logger.warning("No message table found")
            return []
        except Exception as e:
            self.logger.error(f"Error getting all messages: {e}")
            return []

    def get_messages_by_contact(self, contact_id: str) -> List[Dict]:
        """Get all messages from a specific contact.
        
        Args:
            contact_id: Contact JID or phone number
            
        Returns:
            List of messages from that contact
        """
        try:
            message_tables = ['messages', 'message', 'chat_messages']
            
            for table_name in message_tables:
                tables = self.db_reader.get_tables()
                if table_name in tables:
                    # Try common column names
                    for col in ['from_jid', 'contact_id', 'remote_jid', 'from']:
                        results = self.db_reader.search_in_table(
                            table_name, col, contact_id, exact_match=True
                        )
                        if results:
                            return results
            
            return []
        except Exception as e:
            self.logger.error(f"Error getting messages by contact: {e}")
            return []

    def get_messages_by_date_range(self, start_date: datetime, 
                                   end_date: datetime) -> List[Dict]:
        """Get messages within a date range.
        
        Args:
            start_date: Start datetime
            end_date: End datetime
            
        Returns:
            List of messages in date range
        """
        try:
            message_tables = ['messages', 'message', 'chat_messages']
            all_messages = []
            
            for table_name in message_tables:
                tables = self.db_reader.get_tables()
                if table_name in tables:
                    messages = self.db_reader.query_table(table_name)
                    
                    # Filter by timestamp (try common column names)
                    for col in ['timestamp', 'date', 'created_at', 'time']:
                        filtered = []
                        for msg in messages:
                            if col in msg:
                                try:
                                    ts = int(msg[col]) / 1000  # Convert milliseconds
                                    msg_date = datetime.fromtimestamp(ts)
                                    if start_date <= msg_date <= end_date:
                                        filtered.append(msg)
                                except:
                                    pass
                        if filtered:
                            all_messages.extend(filtered)
            
            return all_messages
        except Exception as e:
            self.logger.error(f"Error getting messages by date range: {e}")
            return []

    def search_messages(self, keyword: str) -> List[Dict]:
        """Search messages by keyword.
        
        Args:
            keyword: Search keyword
            
        Returns:
            List of matching messages
        """
        try:
            message_tables = ['messages', 'message', 'chat_messages']
            results = []
            
            for table_name in message_tables:
                tables = self.db_reader.get_tables()
                if table_name in tables:
                    # Search in common text columns
                    for col in ['text', 'body', 'data', 'content', 'message']:
                        matches = self.db_reader.search_in_table(
                            table_name, col, keyword
                        )
                        results.extend(matches)
            
            return results
        except Exception as e:
            self.logger.error(f"Error searching messages: {e}")
            return []

    def get_message_statistics(self) -> Dict:
        """Get statistics about messages.
        
        Returns:
            Dictionary with message statistics
        """
        try:
            messages = self.get_all_messages()
            
            stats = {
                'total_messages': len(messages),
                'messages_with_media': 0,
                'messages_with_location': 0,
                'deleted_messages': 0,
                'forwarded_messages': 0
            }
            
            for msg in messages:
                if any(key in msg for key in ['media_url', 'media_path', 'file_url']):
                    stats['messages_with_media'] += 1
                
                if any(key in msg for key in ['latitude', 'longitude', 'location']):
                    stats['messages_with_location'] += 1
                
                if msg.get('status') == -1:
                    stats['deleted_messages'] += 1
                
                if msg.get('forwarded', 0) == 1:
                    stats['forwarded_messages'] += 1
            
            return stats
        except Exception as e:
            self.logger.error(f"Error getting message statistics: {e}")
            return {}

    def export_messages(self, output_path: str, format: str = 'json') -> bool:
        """Export messages to file.
        
        Args:
            output_path: Path to save exported messages
            format: Export format (json, csv, html)
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            message_tables = ['messages', 'message', 'chat_messages']
            
            for table_name in message_tables:
                tables = self.db_reader.get_tables()
                if table_name in tables:
                    if format == 'json':
                        return self.db_reader.export_table_to_json(table_name, output_path)
                    elif format == 'csv':
                        return self.db_reader.export_table_to_csv(table_name, output_path)
            
            return False
        except Exception as e:
            self.logger.error(f"Error exporting messages: {e}")
            return False
