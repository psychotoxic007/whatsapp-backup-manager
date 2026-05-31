# 📱 WhatsApp Backup Manager

> **Advanced WhatsApp backup management tool** — Download from Google Drive, decrypt databases, extract media, recover deleted chats, and analyze conversations with ease.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-production_ready-brightgreen.svg)

---

## ✨ Features

### 🌩️ **Cloud Integration**
- Download WhatsApp backups from Google Drive
- List all backup files with metadata
- Import local backup files

### 🔓 **Database Decryption**
- Support for CRYPT15 encrypted databases (latest WhatsApp)
- Automatic database validation
- Proper error handling for corrupted files

### 📸 **Media Management**
- Extract all media types (photos, videos, audio, documents)
- Organize media by chat
- Timestamped file naming
- Media statistics and filtering
- Export metadata (JSON/CSV)

### 🗑️ **Deleted Chat Recovery**
- View deleted chats and threads
- Recover deleted messages
- Export deleted content (JSON/CSV)
- Full message restoration with timestamps

### 📊 **Analytics & Insights**
- Message statistics and trends
- Top contacts ranking
- Chat overview
- Message type distribution

### 💾 **Multiple Export Formats**
- JSON export for all data types
- CSV export for spreadsheets
- vCard export for contacts
- Timestamped organization

---

## 📋 Prerequisites

### System Requirements
- **Python** 3.8 or higher
- **Windows, macOS, or Linux**
- **4GB RAM minimum** (for large backups)
- **Sufficient disk space** (depends on backup size)

### Google Drive Setup (Optional)
If you want to download backups from Google Drive:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable **Google Drive API**
4. Create **OAuth 2.0 credentials** (Desktop application)
5. Download credentials as `credentials.json`
6. Place in project root directory

---

## 🚀 Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/psychotoxic007/whatsapp-backup-manager.git
cd whatsapp-backup-manager
Step 2: Create Virtual Environment
bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
Step 3: Install Dependencies
bash
pip install --upgrade pip
pip install -r requirements.txt
Step 4: Install Decryption Tools
For CRYPT15 database decryption (required for modern WhatsApp backups):

bash
pip install wa-crypt-tools pycryptodome
Step 5: Verify Installation
bash
python -m whatsapp_backup_manager --help
Expected output:

Code
Usage: __main__.py [OPTIONS] COMMAND [ARGS]...

  WhatsApp Backup Manager — Advanced backup management with media & deleted chat recovery.

Commands:
  analyze  Analyze database and display statistics.
  backup   Backup management operations.
  deleted  Deleted chat and message recovery operations.
  media    Media extraction and export operations.
  view     View messages from specific contact.
✅ Installation complete!

📖 Complete Usage Guide
A. Getting Your WhatsApp Backup
Option 1: Download from Google Drive (Easiest)
Step 1: Setup Google Drive credentials

bash
# Place your credentials.json in the project root
# Download from: https://console.cloud.google.com/
Step 2: List available backups

bash
python -m whatsapp_backup_manager backup list-drive
Output:

Code
============================================================
  WhatsApp Backup Manager — Google Drive Backups
============================================================

✓  Found 2 backup file(s):

File Name                                Size            Modified
-------------------------------------------------------------------
msgstore-2024-05-31.1.db.crypt15       245.50 MB       2024-05-31
msgstore-2024-05-25.1.db.crypt15       240.30 MB       2024-05-25
  ├─ ID      : 1abc2def3ghi4jkl5mno6pqr
  ├─ Created : 2024-05-31T10:30:45.000Z
  ├─ MIME    : application/octet-stream
  └─ Link    : https://drive.google.com/file/d/1abc2def3ghi4jkl5mno6pqr/view
Step 3: Download the latest backup

bash
python -m whatsapp_backup_manager backup download 1abc2def3ghi4jkl5mno6pqr ./msgstore_encrypted.db.crypt15
Option 2: Use Local Backup File
Extract WhatsApp backup from your phone:

Android: Use WhatsApp > Settings > Chats > Chat backup > Download
iPhone: Use iCloud or local backup
Then import:

bash
python -m whatsapp_backup_manager backup import /path/to/msgstore.db.crypt15
B. Decrypt Your Database ⚠️ IMPORTANT STEP
WhatsApp uses CRYPT15 encryption. You MUST decrypt before using other features.

Prerequisites for Decryption
Android device with WhatsApp installed OR
Backup key file: key.db.json from your Android device (location: /data/data/com.whatsapp/files/key)
Step 1: Extract Encryption Key from Android
Option A: Using WhatsApp Key Extractor

bash
# Install WhatsApp Key Extractor tool
pip install whatsapp-key-extractor

# Extract key from device (requires adb)
whatsapp-key-extractor
Option B: Manual Extraction (Rooted Android)

Connect Android device to PC via USB
Enable USB Debugging
Extract key using ADB:
bash
adb pull /data/data/com.whatsapp/files/key key
Step 2: Decrypt the Database
bash
# Basic decryption
wa-crypt-tools decrypt \
  -i msgstore.db.crypt15 \
  -o msgstore.db \
  -k key.db.json

# With verbose output
wa-crypt-tools decrypt \
  -i msgstore.db.crypt15 \
  -o msgstore.db \
  -k key.db.json \
  -v
Success message:

Code
[*] Decryption started...
[OK] Database decrypted successfully: msgstore.db
[OK] Size: 245.50 MB
❌ Troubleshooting Decryption:

Error	Solution
Key file not found	Ensure key.db.json is in current directory
Invalid key format	Extract new key from Android device
Permission denied	Run with admin/sudo privileges
Corrupted database	Try with different backup file
C. Analyze Your Database
Once you have a decrypted msgstore.db file:

Get Overview Statistics
bash
python -m whatsapp_backup_manager analyze msgstore.db
Output:

Code
================================================================================
  WhatsApp Chat Insights Engine
================================================================================

📊 General Statistics:
  • Total Chats     : 42
  • Total Messages  : 18,453
  • Text Messages   : 15,200
  • Media Messages  : 3,253

🏆 Top 5 Active Conversations:
  1. John Doe                         (2,145 messages)
  2. Family Group                     (1,890 messages)
  3. Work Team                        (1,567 messages)
  4. Sarah Smith                      (1,234 messages)
  5. Business Partner                 (987 messages)

================================================================================
View All Chats (No Limit)
bash
python -m whatsapp_backup_manager analyze msgstore.db --all-chats
View Messages from Specific Contact
bash
python -m whatsapp_backup_manager view msgstore.db "John Doe" --limit 50
Output:

Code
--- Messages from: John Doe ---

You: Hey, how are you?
John Doe: I'm good, thanks for asking!
You: Great! Let's meet tomorrow
John Doe: Sure, what time?
D. Extract All Media Files
Step 1: List All Media
bash
# List all media files
python -m whatsapp_backup_manager media list msgstore.db

# List specific type
python -m whatsapp_backup_manager media list msgstore.db --type image
python -m whatsapp_backup_manager media list msgstore.db --type video
Output:

Code
================================================================================
  WhatsApp Media Manager — Media Files Inventory
================================================================================

✓  Total Media: 3,453 files (8.67 GB)

By Type:
  • Image             : 2,145 files
  • Video             : 567 files
  • Audio             : 345 files
  • Document          : 234 files
  • Other             : 162 files

┏━━━┳━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━��━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┓
┃ # ┃ Type  ┃ Chat       ┃ Filename          ┃ Size   ┃ Date     ┃
┡━━━╇━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━┩
│ 1 │ IMAGE │ John Doe   │ IMG_2024_05_15... │ 2.45MB │ 2024-05-15
│ 2 │ VIDEO │ Family Grp │ VID_2024_05_14... │ 45.6MB │ 2024-05-14
│ 3 │ AUDIO │ Work Team  │ AUD_2024_05_13... │ 567KB  │ 2024-05-13
└───┴───────┴────────────┴───────────────────┴────────┴──────────┘

... and 3,450 more files
Step 2: Export All Media to Directory
Export all media:

bash
python -m whatsapp_backup_manager media export msgstore.db ./media_export
Export by type:

bash
# Photos only
python -m whatsapp_backup_manager media export msgstore.db ./photos --type image

# Videos only
python -m whatsapp_backup_manager media export msgstore.db ./videos --type video

# Documents only
python -m whatsapp_backup_manager media export msgstore.db ./documents --type document
Output structure:

Code
media_export/
├── John Doe/
│   ├── 20240515_143022_IMG_001.jpg
│   ├── 20240514_102145_IMG_002.jpg
│   └── 20240513_085932_VID_001.mp4
├── Family Group/
│   ├── 20240512_165430_AUD_001.m4a
│   └── 20240511_202015_DOC_001.pdf
└── Work Team/
    ├── 20240510_091200_IMG_003.jpg
    └── 20240509_143830_VID_002.mp4
Step 3: Export Media Metadata
For spreadsheet analysis:

bash
# JSON format
python -m whatsapp_backup_manager media metadata msgstore.db media_list.json --format json

# CSV format (for Excel)
python -m whatsapp_backup_manager media metadata msgstore.db media_list.csv --format csv
CSV columns:

Code
id,chat_row_id,from_me,timestamp,media_name,media_url,media_size,file_path,media_type,media_type_name,caption,chat_name,jid
E. Recover Deleted Chats & Messages
Step 1: List Deleted Chats
bash
python -m whatsapp_backup_manager deleted list-chats msgstore.db
Output:

Code
================================================================================
  Deleted Chats Recovery
================================================================================

✓  Found 5 deleted chats:

┏━━━┳────────────────────────┳─────────────────┳──────────┳────────────┓
┃ # ┃ Chat Name              ┃ JID             ┃ Messages ┃ Created    ┃
┡━━━╇────────────────────────╇─────────────────╇──────────╇────────────┩
│ 1 │ Old Project Group      │ 120232...@g.us │ 234      │ 2024-01-15
│ 2 │ Jane Smith             │ 919876...@s.us │ 89       │ 2024-02-20
│ 3 │ Development Team       │ 120555...@g.us │ 456      │ 2024-03-10
│ 4 │ Vendor Contact         │ 919123...@s.us │ 34       │ 2024-04-05
│ 5 │ Event Planning         │ 120999...@g.us │ 178      │ 2024-04-28
└───┴────────────────────────┴─────────────────┴──────────┴────────────┘
Step 2: View Deleted Messages
View all deleted messages:

bash
python -m whatsapp_backup_manager deleted view-messages msgstore.db
View deleted messages from specific chat:

bash
python -m whatsapp_backup_manager deleted view-messages msgstore.db --chat-id 1 --limit 100
Output:

Code
================================================================================
  Deleted Messages Recovery
================================================================================

✓  Found 234 deleted messages:

┏━━━┳───────────────────┳──────┳────────────────────────────────┳────────────┓
┃ # ┃ Chat              ┃ From ┃ Message                        ┃ Date       ┃
┡━━━╇───────────────────╇──────╇────────────────────────────────╇────────────┩
│ 1 │ Old Project Group │ You  │ Meeting at 3 PM tomorrow       │ 2024-05-30
│ 2 │ Old Project Group │ Jane │ I'll be there!                 │ 2024-05-30
│ 3 │ Old Project Group │ You  │ Agenda attached                │ 2024-05-29
│ 4 │ Jane Smith        │ Jane │ Thanks for the update!         │ 2024-05-28
└───┴───────────────────┴──────┴────────────────────────────────┴────────────┘

... and 230 more messages
Step 3: Export Deleted Content
Export deleted chats only:

bash
python -m whatsapp_backup_manager deleted export msgstore.db deleted_chats.json --type chats --format json
Export deleted messages only:

bash
python -m whatsapp_backup_manager deleted export msgstore.db deleted_messages.csv --type messages --format csv
Export everything (both chats and messages):

bash
python -m whatsapp_backup_manager deleted export msgstore.db deleted_recovery --type all --format json
This creates:

deleted_recovery_chats.json
deleted_recovery_messages.json
🔧 Advanced Usage & Troubleshooting
Troubleshooting Common Issues
Issue 1: "credentials.json not found"
Error:

Code
[ERROR] File not found: credentials.json not found at credentials.json
Solution:

bash
# Download credentials from Google Cloud Console
# 1. Go to https://console.cloud.google.com/
# 2. Create OAuth 2.0 credentials (Desktop)
# 3. Download as credentials.json
# 4. Place in project root:
cp ~/Downloads/credentials.json ./credentials.json
Issue 2: "Database not found"
Error:

Code
FileNotFoundError: Database not found: msgstore.db
Solution:

bash
# Ensure you're using the DECRYPTED database
# Correct:
python -m whatsapp_backup_manager analyze msgstore.db

# Wrong (encrypted file):
python -m whatsapp_backup_manager analyze msgstore.db.crypt15  # ❌ Won't work
Issue 3: "Decryption failed - Invalid key"
Error:

Code
Error: Invalid or corrupted key file
Solution:

bash
# Extract fresh key from Android device:
adb shell
su
cp /data/data/com.whatsapp/files/key /sdcard/key

# Then pull:
adb pull /sdcard/key ./key.db.json

# Verify file is not empty:
ls -lh key.db.json  # Should be ~64 bytes
Issue 4: "No media found" but you expect media
Causes & Solutions:

Media files deleted from phone:

WhatsApp stores media references in database
Even if files are deleted, metadata remains
Use include-deleted flag
Wrong database format:

bash
# Verify it's a valid SQLite3 database:
sqlite3 msgstore.db ".tables"
Backup doesn't include media:

Android: Ensure "Include media" in backup settings
Google Drive backup might not include media files
Performance Tips
For large databases (>500MB):

bash
# Use limit to avoid memory issues
python -m whatsapp_backup_manager deleted view-messages msgstore.db --limit 1000

# Export in smaller batches
python -m whatsapp_backup_manager media list msgstore.db --type image > image_metadata.json
Check database size:

bash
# Linux/macOS
ls -lh msgstore.db

# Windows
dir msgstore.db
Command Reference
Backup Commands
bash
backup list-drive              # List Google Drive backups
backup download <ID> <PATH>    # Download from Google Drive
backup import <PATH>           # Import local backup
Media Commands
bash
media list <DB> [-t TYPE]                          # List media
media export <DB> <OUT> [-t TYPE] [-b BACKUP_DIR]  # Export media files
media metadata <DB> <FILE> [-f FORMAT]             # Export metadata
Deleted Chat Commands
bash
deleted list-chats <DB>                 # List deleted chats
deleted view-messages <DB> [-c ID] [-l] # View deleted messages
deleted export <DB> <FILE> [-t] [-f]    # Export deleted content
Analysis Commands
bash
analyze <DB> [--all-chats]       # Database statistics
view <DB> <NAME> [--limit N]     # View specific chat messages
📊 Output Formats
JSON Export
JSON
{
  "id": "1",
  "name": "John Doe",
  "jid": "919876543210@s.us",
  "creation_time": 1234567890,
  "message_count": 234,
  "date_created": "2024-01-15T10:30:45"
}
CSV Export
CSV
id,name,jid,creation_time,message_count
1,John Doe,919876543210@s.us,1234567890,234
Exported Media Structure
Code
export_dir/
├── Chat_Name_1/
│   ├── 20240515_143022_filename.jpg
│   ├── 20240514_102145_video.mp4
├── Chat_Name_2/
│   ├── 20240513_085932_document.pdf
└── Chat_Name_3/
    ├── 20240512_165430_audio.m4a
🔒 Security & Privacy
Important Security Notes
⚠️ Backup Files Contain Sensitive Data

WhatsApp backups contain all messages (including deleted ones)
Media files are unencrypted after extraction
Keep backups in secure locations
✅ Security Best Practices

bash
# 1. Keep encryption key secure
chmod 600 key.db.json

# 2. Use strong passwords for backup storage
# 3. Delete temporary files after analysis
rm msgstore.db.crypt15

# 4. Use encrypted storage
# 5. Don't share credential files
Data Privacy
Local processing: All analysis happens locally (no cloud)
No data collection: Tool doesn't send data anywhere
Credential protection: Store credentials.json securely
Temp files: Delete after use
🐛 Reporting Bugs
Found an issue? Please report it:

bash
# Create detailed bug report with:
# 1. Python version: python --version
# 2. OS: Windows/macOS/Linux
# 3. Error message (full traceback)
# 4. Steps to reproduce

# Submit: https://github.com/psychotoxic007/whatsapp-backup-manager/issues
📝 Requirements.txt
Code
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0
google-api-python-client==2.100.0
click==8.1.7
colorama==0.4.6
rich==13.7.0
wa-crypt-tools==1.1.0
pycryptodome==3.19.1
Install with:

bash
pip install -r requirements.txt
📚 Example Workflows
Workflow 1: Complete Backup Analysis
bash
# 1. Download latest backup
python -m whatsapp_backup_manager backup list-drive
python -m whatsapp_backup_manager backup download <ID> backup.crypt15

# 2. Decrypt database
wa-crypt-tools decrypt -i backup.crypt15 -o msgstore.db -k key.db.json

# 3. Analyze
python -m whatsapp_backup_manager analyze msgstore.db

# 4. Check top contacts
python -m whatsapp_backup_manager analyze msgstore.db --all-chats

# 5. Read specific conversation
python -m whatsapp_backup_manager view msgstore.db "Contact Name" --limit 50
Workflow 2: Media Backup & Archive
bash
# 1. Prepare database (same as above)
wa-crypt-tools decrypt -i backup.crypt15 -o msgstore.db -k key.db.json

# 2. Export all media
python -m whatsapp_backup_manager media export msgstore.db ./media_archive

# 3. Create metadata backup
python -m whatsapp_backup_manager media metadata msgstore.db media_metadata.json

# 4. Archive with compression (optional)
tar -czf media_archive_2024.tar.gz media_archive/
Workflow 3: Recover Deleted Content
bash
# 1. Decrypt database
wa-crypt-tools decrypt -i backup.crypt15 -o msgstore.db -k key.db.json

# 2. Check what's deleted
python -m whatsapp_backup_manager deleted list-chats msgstore.db

# 3. View deleted messages
python -m whatsapp_backup_manager deleted view-messages msgstore.db

# 4. Export for archival/legal purposes
python -m whatsapp_backup_manager deleted export msgstore.db recovery.json --type all
📞 Support
GitHub Issues: https://github.com/psychotoxic007/whatsapp-backup-manager/issues
Documentation: See this README
Troubleshooting: Check the "Troubleshooting" section above
📄 License
MIT License - See LICENSE file for details

🙏 Acknowledgments
wa-crypt-tools for database decryption
google-api-python-client for Google Drive integration
Click for CLI framework
🎯 Roadmap
 Support for CRYPT12 databases
 Web UI interface
 Scheduled automated backups
 Contact name recovery
 Message search functionality
 Export to PDF reports
Made with ❤️ by psychotoxic007
