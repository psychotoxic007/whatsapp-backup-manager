"""Contact Extractor - Extract and analyze contacts from WhatsApp database."""

from typing import Dict, List, Optional
import logging
from .whatsapp_db_reader import WhatsAppDatabaseReader

logger = logging.getLogger(__name__)


class ContactExtractor:
    """Extracts and processes contacts from WhatsApp databases."""

    def __init__(self, db_reader: WhatsAppDatabaseReader):
        """Initialize Contact Extractor.
        
        Args:
            db_reader: WhatsAppDatabaseReader instance
        """
        self.db_reader = db_reader
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_all_contacts(self, limit: Optional[int] = None) -> List[Dict]:
        """Get all contacts from database.
        
        Args:
            limit: Maximum number of contacts to retrieve
            
        Returns:
            List of contact dictionaries
        """
        try:
            # Common contact table names
            contact_tables = ['contacts', 'contact', 'wa_contacts', 'chat_list']
            
            for table_name in contact_tables:
                tables = self.db_reader.get_tables()
                if table_name in tables:
                    return self.db_reader.query_table(table_name, limit)
            
            self.logger.warning("No contact table found")
            return []
        except Exception as e:
            self.logger.error(f"Error getting all contacts: {e}")
            return []

    def get_contact_by_phone(self, phone_number: str) -> Optional[Dict]:
        """Get contact by phone number.
        
        Args:
            phone_number: Phone number to search
            
        Returns:
            Contact dictionary or None
        """
        try:
            contact_tables = ['contacts', 'contact', 'wa_contacts']
            
            for table_name in contact_tables:
                tables = self.db_reader.get_tables()
                if table_name in tables:
                    # Try common column names
                    for col in ['phone', 'phone_number', 'jid', 'number']:
                        results = self.db_reader.search_in_table(
                            table_name, col, phone_number, exact_match=True
                        )
                        if results:
                            return results[0]
            
            return None
        except Exception as e:
            self.logger.error(f"Error getting contact by phone: {e}")
            return None

    def get_contact_by_name(self, name: str) -> List[Dict]:
        """Get contacts by name (partial match).
        
        Args:
            name: Name to search for
            
        Returns:
            List of matching contacts
        """
        try:
            contact_tables = ['contacts', 'contact', 'wa_contacts', 'chat_list']
            results = []
            
            for table_name in contact_tables:
                tables = self.db_reader.get_tables()
                if table_name in tables:
                    # Try common name columns
                    for col in ['display_name', 'name', 'jid', 'title']:
                        matches = self.db_reader.search_in_table(
                            table_name, col, name
                        )
                        results.extend(matches)
            
            return results
        except Exception as e:
            self.logger.error(f"Error getting contact by name: {e}")
            return []

    def get_groups(self) -> List[Dict]:
        """Get all group chats.
        
        Returns:
            List of group dictionaries
        """
        try:
            group_tables = ['groups', 'group', 'chat_list']
            
            for table_name in group_tables:
                tables = self.db_reader.get_tables()
                if table_name in tables:
                    # Filter for groups (usually identified by specific columns)
                    groups = self.db_reader.query_table(table_name)
                    return [g for g in groups if self._is_group(g)]
            
            return []
        except Exception as e:
            self.logger.error(f"Error getting groups: {e}")
            return []

    def get_group_members(self, group_id: str) -> List[Dict]:
        """Get members of a group.
        
        Args:
            group_id: Group ID or JID
            
        Returns:
            List of group member dictionaries
        """
        try:
            member_tables = ['group_members', 'participants', 'members']
            
            for table_name in member_tables:
                tables = self.db_reader.get_tables()
                if table_name in tables:
                    for col in ['group_id', 'gid', 'jid']:
                        results = self.db_reader.search_in_table(
                            table_name, col, group_id, exact_match=True
                        )
                        if results:
                            return results
            
            return []
        except Exception as e:
            self.logger.error(f"Error getting group members: {e}")
            return []

    def get_blocked_contacts(self) -> List[Dict]:
        """Get list of blocked contacts.
        
        Returns:
            List of blocked contact dictionaries
        """
        try:
            # Look for blocked contacts (usually marked with a flag)
            contact_tables = ['contacts', 'contact', 'wa_contacts']
            blocked = []
            
            for table_name in contact_tables:
                tables = self.db_reader.get_tables()
                if table_name in tables:
                    contacts = self.db_reader.query_table(table_name)
                    
                    for contact in contacts:
                        if contact.get('is_blocked', 0) == 1 or contact.get('blocked', 0) == 1:
                            blocked.append(contact)
            
            return blocked
        except Exception as e:
            self.logger.error(f"Error getting blocked contacts: {e}")
            return []

    def get_contact_statistics(self) -> Dict:
        """Get statistics about contacts.
        
        Returns:
            Dictionary with contact statistics
        """
        try:
            contacts = self.get_all_contacts()
            groups = self.get_groups()
            blocked = self.get_blocked_contacts()
            
            stats = {
                'total_contacts': len(contacts),
                'total_groups': len(groups),
                'blocked_contacts': len(blocked),
                'saved_contacts': 0,
                'unsaved_contacts': 0
            }
            
            for contact in contacts:
                if contact.get('is_name_saved', 0) == 1:
                    stats['saved_contacts'] += 1
                else:
                    stats['unsaved_contacts'] += 1
            
            return stats
        except Exception as e:
            self.logger.error(f"Error getting contact statistics: {e}")
            return {}

    def export_contacts(self, output_path: str, format: str = 'json') -> bool:
        """Export contacts to file.
        
        Args:
            output_path: Path to save exported contacts
            format: Export format (json, csv, vcard)
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            contact_tables = ['contacts', 'contact', 'wa_contacts']
            
            for table_name in contact_tables:
                tables = self.db_reader.get_tables()
                if table_name in tables:
                    if format == 'json':
                        return self.db_reader.export_table_to_json(table_name, output_path)
                    elif format == 'csv':
                        return self.db_reader.export_table_to_csv(table_name, output_path)
                    elif format == 'vcard':
                        return self._export_to_vcard(table_name, output_path)
            
            return False
        except Exception as e:
            self.logger.error(f"Error exporting contacts: {e}")
            return False

    def _is_group(self, contact: Dict) -> bool:
        """Check if contact is a group.
        
        Args:
            contact: Contact dictionary
            
        Returns:
            True if contact is a group, False otherwise
        """
        # Groups typically have @g.us or -g.us in their JID
        jid = contact.get('jid', '')
        return '@g.us' in str(jid) or '-g.us' in str(jid)

    def _export_to_vcard(self, table_name: str, output_path: str) -> bool:
        """Export contacts to vCard format.
        
        Args:
            table_name: Name of contact table
            output_path: Path to save vCard file
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            contacts = self.db_reader.query_table(table_name)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                for contact in contacts:
                    f.write('BEGIN:VCARD\n')
                    f.write('VERSION:3.0\n')
                    
                    name = contact.get('display_name') or contact.get('name') or 'Unknown'
                    f.write(f'FN:{name}\n')
                    
                    phone = contact.get('phone') or contact.get('number') or ''
                    if phone:
                        f.write(f'TEL:{phone}\n')
                    
                    jid = contact.get('jid') or ''
                    if jid:
                        f.write(f'X-WhatsApp-JID:{jid}\n')
                    
                    f.write('END:VCARD\n')
            
            self.logger.info(f"Exported {len(contacts)} contacts to {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error exporting to vCard: {e}")
            return False
