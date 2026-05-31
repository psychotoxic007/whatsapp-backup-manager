"""Media Manager for extracting and exporting media files from WhatsApp databases."""

import sqlite3
import os
import logging
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MediaManager:
    """Manages extraction and export of media files from WhatsApp databases."""
    
    # Media type mappings
    MEDIA_TYPES = {
        0: 'text',
        1: 'image',
        2: 'video',
        3: 'audio',
        4: 'document',
        5: 'location',
        6: 'contact',
        7: 'sticker'
    }
    
    def __init__(self, db_path: str, backup_path: str = None):
        """Initialize Media Manager.
        
        Args:
            db_path: Path to decrypted WhatsApp database
            backup_path: Optional path to WhatsApp backup directory
        """
        self.db_path = Path(db_path)
        self.backup_path = Path(backup_path) if backup_path else None
        
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {db_path}")
        
        logger.info(f"MediaManager initialized with database: {db_path}")
    
    def get_all_media(self, include_deleted: bool = True) -> List[Dict]:
        """Get all media files from database.
        
        Args:
            include_deleted: Include deleted media
            
        Returns:
            List of media file dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Check available columns
            cursor.execute("PRAGMA table_info(message)")
            columns = {col[1]: col[2] for col in cursor.fetchall()}
            
            # Build query with available columns
            media_query = """
                SELECT 
                    message._id,
                    message.chat_row_id,
                    message.from_me,
                    message.timestamp,
                    message.media_name,
                    message.media_url,
                    message.media_size,
                    message.file_path,
                    message.message_type,
                    message.text_data,
                    chat.subject,
                    jid.user
                FROM message
                JOIN chat ON message.chat_row_id = chat._id
                LEFT JOIN jid ON chat.jid_row_id = jid._id
                WHERE message.message_type IN (1, 2, 3, 4, 5, 6, 7)
            """
            
            if not include_deleted:
                media_query += " AND message.status != -1"
            
            media_query += " ORDER BY message.timestamp DESC"
            
            cursor.execute(media_query)
            rows = cursor.fetchall()
            
            media_list = []
            for row in rows:
                media_list.append({
                    'id': row['_id'],
                    'chat_row_id': row['chat_row_id'],
                    'from_me': row['from_me'],
                    'timestamp': row['timestamp'],
                    'media_name': row['media_name'],
                    'media_url': row['media_url'],
                    'media_size': row['media_size'],
                    'file_path': row['file_path'],
                    'media_type': row['message_type'],
                    'media_type_name': self.MEDIA_TYPES.get(row['message_type'], 'unknown'),
                    'caption': row['text_data'],
                    'chat_name': row['subject'] or row['user'] or 'Unknown',
                    'jid': row['user']
                })
            
            conn.close()
            logger.info(f"Found {len(media_list)} media files (include_deleted={include_deleted})")
            return media_list
        
        except sqlite3.Error as e:
            logger.error(f"Error retrieving media: {e}")
            raise
    
    def get_media_by_type(self, media_type: str, include_deleted: bool = True) -> List[Dict]:
        """Get media files of specific type.
        
        Args:
            media_type: Type name (image, video, audio, document, etc.)
            include_deleted: Include deleted media
            
        Returns:
            List of media files of that type
        """
        media_type_id = None
        for type_id, type_name in self.MEDIA_TYPES.items():
            if type_name == media_type.lower():
                media_type_id = type_id
                break
        
        if media_type_id is None:
            logger.warning(f"Unknown media type: {media_type}")
            return []
        
        all_media = self.get_all_media(include_deleted)
        return [m for m in all_media if m['media_type'] == media_type_id]
    
    def get_media_statistics(self, include_deleted: bool = True) -> Dict:
        """Get media statistics.
        
        Args:
            include_deleted: Include deleted media in stats
            
        Returns:
            Dictionary with media statistics
        """
        media = self.get_all_media(include_deleted)
        
        stats = {
            'total_media': len(media),
            'total_size': 0,
            'by_type': {},
            'by_chat': {}
        }
        
        for media_type_name in self.MEDIA_TYPES.values():
            stats['by_type'][media_type_name] = 0
        
        for item in media:
            media_type_name = item['media_type_name']
            stats['by_type'][media_type_name] = stats['by_type'].get(media_type_name, 0) + 1
            
            if item['media_size']:
                stats['total_size'] += item['media_size']
            
            chat_name = item['chat_name']
            if chat_name not in stats['by_chat']:
                stats['by_chat'][chat_name] = 0
            stats['by_chat'][chat_name] += 1
        
        return stats
    
    def export_media_metadata(self, output_file: str, format: str = 'json', 
                             include_deleted: bool = True) -> bool:
        """Export media metadata to file.
        
        Args:
            output_file: Output file path
            format: Export format (json, csv)
            include_deleted: Include deleted media
            
        Returns:
            True if successful
        """
        try:
            import json
            import csv
            
            media = self.get_all_media(include_deleted)
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if format == 'json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(media, f, indent=2, ensure_ascii=False, default=str)
                logger.info(f"Exported {len(media)} media metadata to {output_file}")
            
            elif format == 'csv':
                if not media:
                    logger.warning("No media to export")
                    return False
                
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=media[0].keys())
                    writer.writeheader()
                    writer.writerows(media)
                logger.info(f"Exported {len(media)} media metadata to {output_file}")
            
            return True
        
        except Exception as e:
            logger.error(f"Error exporting metadata: {e}")
            return False
    
    def export_media_files(self, output_dir: str, media_type: Optional[str] = None,
                          include_deleted: bool = True, backup_dir: Optional[str] = None) -> Dict:
        """Export actual media files to directory.
        
        Args:
            output_dir: Output directory path
            media_type: Optional filter by type (image, video, audio, etc.)
            include_deleted: Include deleted media
            backup_dir: Alternative media backup directory
            
        Returns:
            Dictionary with export results
        """
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            if media_type:
                media = self.get_media_by_type(media_type, include_deleted)
            else:
                media = self.get_all_media(include_deleted)
            
            results = {
                'total_files': len(media),
                'exported': 0,
                'failed': 0,
                'skipped': 0,
                'files': []
            }
            
            for item in media:
                file_path = item.get('file_path') or item.get('media_url')
                
                if not file_path:
                    results['skipped'] += 1
                    continue
                
                # Try to find the file
                source_path = None
                if Path(file_path).exists():
                    source_path = Path(file_path)
                elif backup_dir and Path(backup_dir, file_path).exists():
                    source_path = Path(backup_dir, file_path)
                elif self.backup_path and (self.backup_path / file_path).exists():
                    source_path = self.backup_path / file_path
                
                if not source_path:
                    logger.warning(f"Media file not found: {file_path}")
                    results['failed'] += 1
                    continue
                
                try:
                    # Create chat subdirectory
                    chat_dir = output_path / self._sanitize_name(item['chat_name'])
                    chat_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Create destination with timestamp
                    timestamp = datetime.fromtimestamp(item['timestamp'] / 1000) if item['timestamp'] else datetime.now()
                    filename = source_path.name
                    dest_path = chat_dir / f"{timestamp.strftime('%Y%m%d_%H%M%S')}_{filename}"
                    
                    # Copy file
                    shutil.copy2(source_path, dest_path)
                    
                    results['exported'] += 1
                    results['files'].append({
                        'source': str(source_path),
                        'destination': str(dest_path),
                        'chat': item['chat_name'],
                        'type': item['media_type_name'],
                        'size': item['media_size']
                    })
                    
                    logger.info(f"Exported: {dest_path}")
                
                except Exception as e:
                    logger.error(f"Failed to export {source_path}: {e}")
                    results['failed'] += 1
            
            logger.info(f"Media export complete: {results['exported']} exported, {results['failed']} failed, {results['skipped']} skipped")
            return results
        
        except Exception as e:
            logger.error(f"Error exporting media files: {e}")
            raise
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize filename/directory name."""
        invalid_chars = r'<>:"/\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        return name[:255]
