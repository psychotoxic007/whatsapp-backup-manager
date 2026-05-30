# WhatsApp Backup Manager

A comprehensive tool suite for managing, organizing, and analyzing WhatsApp backups from local and cloud storage.

## Features

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

## Requirements

- Python 3.8+
- Google Drive API credentials (for cloud backup access)
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
GOOGLE_DRIVE_CREDENTIALS_PATH=path/to/credentials.json
BACKUP_STORAGE_PATH=./backups
DATABASE_PATH=./data/whatsapp.db
```

2. Set up Google Drive API:
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable Google Drive API
   - Download OAuth 2.0 credentials (JSON)
   - Save as `credentials.json` in project root

## Usage

### Command Line Interface

```bash
python -m whatsapp_backup_manager --help
```

### Backup Manager
```bash
python -m whatsapp_backup_manager backup --list-local
python -m whatsapp_backup_manager backup --list-drive
python -m whatsapp_backup_manager backup --import path/to/backup.tar
```

### Media Organizer
```bash
python -m whatsapp_backup_manager media --organize backup_id
python -m whatsapp_backup_manager media --filter backup_id --type images --date 2024-01
```

### Analysis Tool
```bash
python -m whatsapp_backup_manager analyze --backup backup_id
python -m whatsapp_backup_manager analyze --report backup_id --output report.json
```

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
│   ├── backup_manager/
│   │   ├── __init__.py
│   │   ├── local_manager.py
│   │   ├── cloud_manager.py
│   │   └── backup_utils.py
│   ├── media_organizer/
│   │   ├── __init__.py
│   │   ├── organizer.py
│   │   ├── filters.py
│   │   └── media_utils.py
│   ├── analysis_tool/
│   │   ├── __init__.py
│   │   ├── analyzer.py
│   │   ├── statistics.py
│   │   └── report_generator.py
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
│   └── test_analysis_tool.py
└── docs/
    ├── INSTALLATION.md
    ├── API.md
    └── TROUBLESHOOTING.md
```

## License

MIT License - See LICENSE file for details

## Disclaimer

This tool is designed for personal use and data recovery on your own devices. Ensure you have proper authorization and comply with local laws when accessing and analyzing backup data.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
