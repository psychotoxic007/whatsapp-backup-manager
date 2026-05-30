"""Database Viewer - Interactive viewer for WhatsApp database contents."""

from typing import Dict, List, Optional
import logging
from .whatsapp_db_reader import WhatsAppDatabaseReader
from .message_extractor import MessageExtractor
from .contact_extractor import ContactExtractor
from .media_extractor import MediaExtractor

logger = logging.getLogger(__name__)


class DatabaseViewer:
    """Provides comprehensive viewing and analysis of WhatsApp database."""

    def __init__(self, db_path: str):
        """Initialize Database Viewer.
        
        Args:
            db_path: Path to WhatsApp database file
        """
        self.db_reader = WhatsAppDatabaseReader(db_path)
        if not self.db_reader.connect():
            raise ConnectionError(f"Failed to connect to database: {db_path}")
        
        self.message_extractor = MessageExtractor(self.db_reader)
        self.contact_extractor = ContactExtractor(self.db_reader)
        self.media_extractor = MediaExtractor(self.db_reader)
        logger.info("DatabaseViewer initialized successfully")

    def get_overview(self) -> Dict:
        """Get complete database overview.
        
        Returns:
            Dictionary with complete overview
        """
        try:
            return {
                'database_info': self.db_reader.get_database_info(),
                'message_stats': self.message_extractor.get_message_statistics(),
                'contact_stats': self.contact_extractor.get_contact_statistics(),
                'media_stats': self.media_extractor.get_media_statistics()
            }
        except Exception as e:
            logger.error(f"Error getting overview: {e}")
            return {}

    def search_all(self, keyword: str) -> Dict:
        """Search across messages, contacts, and media.
        
        Args:
            keyword: Search term
            
        Returns:
            Dictionary with search results from all sources
        """
        try:
            return {
                'messages': self.message_extractor.search_messages(keyword),
                'contacts': self.contact_extractor.get_contact_by_name(keyword),
            }
        except Exception as e:
            logger.error(f"Error searching all: {e}")
            return {'messages': [], 'contacts': []}

    def export_all(self, output_dir: str, formats: List[str] = None) -> Dict:
        """Export all data to files.
        
        Args:
            output_dir: Directory to save exports
            formats: List of formats (json, csv, html, vcard)
            
        Returns:
            Dictionary with export results
        """
        if formats is None:
            formats = ['json', 'csv']
        
        try:
            from pathlib import Path
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            results = {
                'messages': {},
                'contacts': {},
                'media': {}
            }
            
            # Export messages
            for fmt in formats:
                msg_path = output_path / f"messages.{fmt}"
                if self.message_extractor.export_messages(str(msg_path), fmt):
                    results['messages'][fmt] = str(msg_path)
            
            # Export contacts
            for fmt in formats:
                if fmt == 'csv':
                    contact_path = output_path / f"contacts.{fmt}"
                    if self.contact_extractor.export_contacts(str(contact_path), fmt):
                        results['contacts'][fmt] = str(contact_path)
                elif fmt == 'json':
                    contact_path = output_path / f"contacts.{fmt}"
                    if self.contact_extractor.export_contacts(str(contact_path), fmt):
                        results['contacts'][fmt] = str(contact_path)
            
            # Export media metadata
            for fmt in formats:
                if fmt in ['json', 'csv']:
                    media_path = output_path / f"media.{fmt}"
                    if self.media_extractor.export_media_metadata(str(media_path), fmt):
                        results['media'][fmt] = str(media_path)
            
            logger.info(f"Exported all data to {output_dir}")
            return results
        except Exception as e:
            logger.error(f"Error exporting all: {e}")
            return {}

    def close(self) -> None:
        """Close database connection."""
        self.db_reader.disconnect()
        logger.info("DatabaseViewer closed")
