# Installation Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/psychotoxic007/whatsapp-backup-manager.git
cd whatsapp-backup-manager
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Google Drive Access (Optional)

To enable Google Drive backup access:

1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google Drive API
4. Create OAuth 2.0 credentials (Desktop application)
5. Download JSON credentials file
6. Save as `credentials.json` in the project root

### 5. Set Up Environment Variables

Copy `.env.example` to `.env` and update values:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```
GOOGLE_DRIVE_CREDENTIALS_PATH=./credentials.json
GOOGLE_DRIVE_ENABLED=true
BACKUP_STORAGE_PATH=./backups
MEDIA_STORAGE_PATH=./media
DATABASE_PATH=./data/whatsapp.db
LOG_LEVEL=INFO
```

## Running the Application

### Command Line Interface

```bash
# View help
python -m whatsapp_backup_manager --help

# List local backups
python -m whatsapp_backup_manager backup list-local
```

### Install as Command-Line Tool

```bash
pip install -e .

# Now you can use:
wbm --help
```

## Troubleshooting

### Permission Denied Error

Make sure the application has read/write access to backup directories.

### Google Drive Connection Issues

- Verify `credentials.json` exists and is valid
- Check internet connection
- Re-authenticate by deleting `token.pickle` file if it exists

### Database Lock Error

- Ensure only one instance is running
- Check database file permissions
- Restart the application
