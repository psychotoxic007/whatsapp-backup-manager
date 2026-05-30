# WhatsApp Backup Manager

A comprehensive tool suite for managing, organizing, analyzing, and extracting data from WhatsApp backups from local and cloud storage.

## ✨ Features

### 1. Backup Manager
- Browse and manage WhatsApp backups from Google Drive and local storage
- Support for both Android and iOS backup formats
- Backup verification and integrity checks
- Easy import/export functionality

### 2. Media Organizer
- Automatically organize media files from backups
- Filter by date, type (images, videos, audio, documents)
- Search and categorize media
- Export organized media collections
- Generate media statistics and reports

### 3. Analysis Tool
- Analyze chat metadata and patterns
- Generate statistics (message count, active hours, frequent contacts)
- Timeline visualization
- Export analysis reports
- Conversation insights and trends

### 4. Database Extractor & Viewer ⭐ NEW
- **View & Access**: Read and navigate WhatsApp SQLite database files
- **Extract Messages**: Get all messages, search by keyword, filter by contact/date
- **Extract Contacts**: Get all contacts, groups, blocked contacts, group members
- **Extract Media**: Get media metadata, filter by type, find media file paths
- **Search**: Global search across messages, contacts, and media
- **Export**: Export to JSON, CSV, vCard formats
- **Statistics**: Generate comprehensive reports on messages, contacts, media

## Requirements

- Python 3.8+
- Google Drive API credentials (for cloud backup access - optional)
- SQLite3 (included with Python)

## Installation

```bash
git clone https://github.com/psychotoxic007/whatsapp-backup-manager.git
cd whatsapp-backup-manager
pip install -r requirements.txt
```

## Configuration

1. Create a `.env` file in the project root:
```
GOOGLE_DRIVE_CREDENTIALS_PATH=./credentials.json
GOOGLE_DRIVE_ENABLED=true
BACKUP_STORAGE_PATH=./backups
MEDIA_STORAGE_PATH=./media
REPORT_STORAGE_PATH=./reports
DATABASE_PATH=./data/whatsapp.db
LOG_LEVEL=INFO
```

2. Set up Google Drive API (optional):
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable Google Drive API
   - Download OAuth 2.0 credentials (JSON)
   - Save as `credentials.json` in project root

## Usage

### Main CLI Help
```bash
python -m whatsapp_backup_manager --help
```

### Backup Manager
```bash
# List local backups
python -m whatsapp_backup_manager backup list-local

# List Google Drive backups
python -m whatsapp_backup_manager backup list-drive

# Import a backup
python -m whatsapp_backup_manager backup import /path/to/backup.tar
```

### Media Organizer
```bash
# Organize media from backup
python -m whatsapp_backup_manager media organize <backup_id>

# Filter media by type and date
python -m whatsapp_backup_manager media filter-media <backup_id> --type images --date 2024-01
```

### Analysis Tool
```bash
# Run analysis on backup
python -m whatsapp_backup_manager analyze run <backup_id>

# Generate analysis report
python -m whatsapp_backup_manager analyze generate-report <backup_id> --output report.json
```

### Database Extraction & Viewing ⭐ NEW

#### View Database Information
```bash
# Get complete database info (tables, row counts, schema)
python -m whatsapp_backup_manager db info /path/to/msgstore.db

# List all tables in database
python -m whatsapp_backup_manager db tables /path/to/msgstore.db

# View specific table contents
python -m whatsapp_backup_manager db view-table /path/to/msgstore.db --table messages --limit 20
```

#### Extract & Analyze Data
```bash
# Get message statistics
python -m whatsapp_backup_manager db messages /path/to/msgstore.db

# Get contact statistics
python -m whatsapp_backup_manager db contacts /path/to/msgstore.db

# Get media statistics
python -m whatsapp_backup_manager db media /path/to/msgstore.db

# Search across all data
python -m whatsapp_backup_manager db search /path/to/msgstore.db "keyword"
```

#### Export Data
```bash
# Export all data (messages, contacts, media) to JSON and CSV
python -m whatsapp_backup_manager db export /path/to/msgstore.db --output ./exports --format json --format csv
```

### Python API Usage

#### Database Viewer (Complete Overview)
```python
from whatsapp_backup_manager.db_extractor.db_viewer import DatabaseViewer

viewer = DatabaseViewer('/path/to/msgstore.db')

# Get complete overview
overview = viewer.get_overview()

# Search across all data
results = viewer.search_all('hello')

# Export all data
export_results = viewer.export_all('./output', formats=['json', 'csv'])

viewer.close()
```

#### Message Extraction
```python
from whatsapp_backup_manager.db_extractor import WhatsAppDatabaseReader, MessageExtractor

reader = WhatsAppDatabaseReader('/path/to/msgstore.db')
reader.connect()

msg_extractor = MessageExtractor(reader)

# Get all messages
messages = msg_extractor.get_all_messages(limit=100)

# Search messages
results = msg_extractor.search_messages('hello')

# Get message statistics
stats = msg_extractor.get_message_statistics()

# Export messages
msg_extractor.export_messages('./messages.json', format='json')

reader.disconnect()
```

#### Contact Extraction
```python
from whatsapp_backup_manager.db_extractor import WhatsAppDatabaseReader, ContactExtractor

reader = WhatsAppDatabaseReader('/path/to/msgstore.db')
reader.connect()

contact_extractor = ContactExtractor(reader)

# Get all contacts
contacts = contact_extractor.get_all_contacts()

# Get groups
groups = contact_extractor.get_groups()

# Get blocked contacts
blocked = contact_extractor.get_blocked_contacts()

# Export contacts
contact_extractor.export_contacts('./contacts.json', format='json')
contact_extractor.export_contacts('./contacts.vcf', format='vcard')

reader.disconnect()
```

#### Media Extraction
```python
from whatsapp_backup_manager.db_extractor import WhatsAppDatabaseReader, MediaExtractor

reader = WhatsAppDatabaseReader('/path/to/msgstore.db')
reader.connect()

media_extractor = MediaExtractor(reader)

# Get all media
media = media_extractor.get_all_media()

# Get media by type
images = media_extractor.get_media_by_type('image')
videos = media_extractor.get_media_by_type('video')

# Get media statistics
stats = media_extractor.get_media_statistics()

# Export media metadata
media_extractor.export_media_metadata('./media.json', format='json')

reader.disconnect()
```

#### Direct Database Reading
```python
from whatsapp_backup_manager.db_extractor import WhatsAppDatabaseReader

reader = WhatsAppDatabaseReader('/path/to/msgstore.db')
reader.connect()

# Get all tables
tables = reader.get_tables()

# Get table schema
schema = reader.get_table_schema('messages')

# Query table
messages = reader.query_table('messages', limit=50)

# Search in table
results = reader.search_in_table('messages', 'text', 'hello')

# Get table row count
count = reader.get_table_row_count('messages')

# Export table
reader.export_table_to_json('messages', './messages.json')
reader.export_table_to_csv('messages', './messages.csv')

# Get comprehensive database info
db_info = reader.get_database_info()

reader.disconnect()
```

## Supported Export Formats

| Data Type | JSON | CSV | vCard | HTML |
|-----------|------|-----|-------|------|
| Messages | ✅ | ✅ | - | - |
| Contacts | ✅ | ✅ | ✅ | - |
| Media | ✅ | ✅ | - | - |
| Groups | ✅ | ✅ | - | - |
| Complete Database | ✅ | ✅ | - | - |

## Project Structure

```
whatsapp-backup-manager/
├── README.md
├── requirements.txt
├── setup.py
├── .gitignore
├── .env.example
├── config/
│   ├── __init__.py
│   └── settings.py
├── whatsapp_backup_manager/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── cli_db.py                          # Database CLI
│   ├── backup_manager/
│   │   ├── __init__.py
│   │   ├── backup_manager.py
│   │   ├── local_manager.py
│   │   └── cloud_manager.py
│   ├── media_organizer/
│   │   ├── __init__.py
│   │   └── organizer.py
│   ├── analysis_tool/
│   │   ├── __init__.py
│   │   └── analyzer.py
│   ├── db_extractor/                      # ⭐ NEW: Database extraction
│   │   ├── __init__.py
│   │   ├── whatsapp_db_reader.py         # Read SQLite databases
│   │   ├── message_extractor.py          # Extract messages
│   │   ├── contact_extractor.py          # Extract contacts
│   │   ├── media_extractor.py            # Extract media
│   │   └── db_viewer.py                  # Unified interface
│   ├── database/
│   │   ├── __init__.py
│   │   ├── db_manager.py
│   │   └── models.py
│   └── utils/
│       ├── __init__.py
│       ├── logger.py
│       └── validators.py
├── tests/
│   ├── __init__.py
│   ├── test_backup_manager.py
│   ├── test_media_organizer.py
│   ├── test_analysis_tool.py
│   └── test_db_extractor.py
└── docs/
    ├── INSTALLATION.md
    ├── API.md
    ├── DATABASE_EXTRACTION.md              # ⭐ NEW: Database guide
    └── TROUBLESHOOTING.md
```

## Supported WhatsApp Databases

- `msgstore.db` - Main message database
- `messages.db` - Alternative message database
- `contacts.db` - Contacts database
- `chat_list.db` - Chat list database
- `wa.db` - General WhatsApp database

## Common Use Cases

### 1. Extract all messages as JSON
```bash
python -m whatsapp_backup_manager db export /path/to/msgstore.db --output ./exports --format json
```

### 2. Search for specific keyword
```bash
python -m whatsapp_backup_manager db search /path/to/msgstore.db "important keyword"
```

### 3. Get message statistics
```bash
python -m whatsapp_backup_manager db messages /path/to/msgstore.db
```

### 4. Export contacts as vCard
```python
from whatsapp_backup_manager.db_extractor import WhatsAppDatabaseReader, ContactExtractor

reader = WhatsAppDatabaseReader('/path/to/contacts.db')
reader.connect()
extractor = ContactExtractor(reader)
extractor.export_contacts('./contacts.vcf', format='vcard')
reader.disconnect()
```

## License

MIT License - See LICENSE file for details

## Disclaimer

This tool is designed for personal use and data recovery on your own devices. Ensure you have proper authorization and comply with local laws when accessing and analyzing backup data.

**Important**: WhatsApp data is encrypted. This tool works with **decrypted** database files (.db format). Always ensure you have the right to access and analyze the backup data.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, feature requests, or questions, please open an issue on GitHub.

### Documentation
- [Installation Guide](docs/INSTALLATION.md)
- [API Reference](docs/API.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
