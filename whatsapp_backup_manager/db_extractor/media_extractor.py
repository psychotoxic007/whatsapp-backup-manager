"""Media Extractor - Extract media information from WhatsApp database."""

from typing import Dict, List, Optional
import logging
from .whatsapp_db_reader import WhatsAppDatabaseReader

logger = logging.getLogger(__name__)


class MediaExtractor:
    """Extracts and processes media information from WhatsApp databases."""

    MEDIA_TYPES = {
        'image': 1,
        'video': 2,
        'audio': 3,
        'document': 4,
        'location': 5,
        'contact': 6,
        'sticker': 7
    }

    def __init__(self, db_reader: WhatsAppDatabaseReader):
        """Initialize Media Extractor.
        
        Args:
            db_reader: WhatsAppDatabaseReader instance
        """
        self.db_reader = db_reader
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_all_media(self, limit: Optional[int] = None) -> List[Dict]:
        """Get all media records from database.
        
        Args:
            limit: Maximum number of records to retrieve
            
        Returns:
            List of media dictionaries
        """
        try:
            # Common media table names
            media_tables = ['media', 'message_media', 'wa_media', 'messages']
            
            for table_name in media_tables:
                tables = self.db_reader.get_tables()
                if table_name in tables:
                    all_data = self.db_reader.query_table(table_name, limit)
                    # Filter for media records
                    media = [m for m in all_data if self._is_media_record(m)]
                    if media:
                        return media
            
            return []
        except Exception as e:
            self.logger.error(f"Error getting all media: {e}")
            return []

    def get_media_by_type(self, media_type: str) -> List[Dict]:
        """Get media of a specific type.
        
        Args:
            media_type: Type of media (image, video, audio, document, etc.)
            
        Returns:
            List of media of that type
        """
        try:
            media = self.get_all_media()
            media_type_id = self.MEDIA_TYPES.get(media_type.lower())
            
            if media_type_id:
                filtered = []
                for m in media:
                    if m.get('media_type') == media_type_id or m.get('type') == media_type_id:
                        filtered.append(m)
                return filtered
            
            return []
        except Exception as e:
            self.logger.error(f"Error getting media by type: {e}")
            return []

    def get_media_by_contact(self, contact_id: str) -> List[Dict]:
        """Get media from a specific contact.
        
        Args:
            contact_id: Contact JID or phone number
            
        Returns:
            List of media from that contact
        """
        try:
            media = self.get_all_media()
            
            filtered = []
            for m in media:
                if (m.get('from_jid') == contact_id or 
                    m.get('contact_id') == contact_id or
                    contact_id in str(m.get('jid', ''))):
                    filtered.append(m)
            
            return filtered
        except Exception as e:
            self.logger.error(f"Error getting media by contact: {e}")
            return []

    def get_media_statistics(self) -> Dict:
        """Get statistics about media in the database.
        
        Returns:
            Dictionary with media statistics
        """
        try:
            media = self.get_all_media()
            
            stats = {
                'total_media': len(media),
                'by_type': {k: 0 for k in self.MEDIA_TYPES.keys()},
                'total_file_size': 0,
                'media_with_captions': 0,
                'media_sent': 0,
                'media_received': 0
            }
            
            for m in media:
                # Count by type
                media_type_id = m.get('media_type') or m.get('type')
                for type_name, type_id in self.MEDIA_TYPES.items():
                    if media_type_id == type_id:
                        stats['by_type'][type_name] += 1
                        break
                
                # File size
                if 'file_size' in m:
                    stats['total_file_size'] += m['file_size']
                
                # Captions
                if m.get('caption') or m.get('text'):
                    stats['media_with_captions'] += 1
                
                # Direction
                if m.get('status') == 1:
                    stats['media_sent'] += 1
                else:
                    stats['media_received'] += 1
            
            return stats
        except Exception as e:
            self.logger.error(f"Error getting media statistics: {e}")
            return {}

    def get_media_file_paths(self) -> List[str]:
        """Get list of media file paths.
        
        Returns:
            List of file paths
        """
        try:
            media = self.get_all_media()
            paths = []
            
            for m in media:
                # Try common file path column names
                for col in ['file_path', 'path', 'local_path', 'media_path', 'file_name']:
                    if col in m and m[col]:
                        paths.append(m[col])
                        break
            
            return list(set(paths))  # Remove duplicates
        except Exception as e:
            self.logger.error(f"Error getting media file paths: {e}")
            return []

    def export_media_metadata(self, output_path: str, format: str = 'json') -> bool:
        """Export media metadata to file.
        
        Args:
            output_path: Path to save exported metadata
            format: Export format (json, csv)
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            media = self.get_all_media()
            
            if format == 'json':
                import json
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(media, f, indent=2, ensure_ascii=False, default=str)
                
                self.logger.info(f"Exported {len(media)} media records to {output_path}")
                return True
            
            elif format == 'csv':
                import csv
                if not media:
                    return False
                
                columns = list(media[0].keys())
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=columns)
                    writer.writeheader()
                    writer.writerows(media)
                
                self.logger.info(f"Exported {len(media)} media records to {output_path}")
                return True
            
            return False
        except Exception as e:
            self.logger.error(f"Error exporting media metadata: {e}")
            return False

    def _is_media_record(self, record: Dict) -> bool:
        """Check if a record represents media.
        
        Args:
            record: Database record
            
        Returns:
            True if record is media, False otherwise
        """
        media_indicators = [
            'media_type', 'file_path', 'file_name', 'file_size',
            'media_path', 'thumbnail', 'url'
        ]
        
        return any(key in record for key in media_indicators)
