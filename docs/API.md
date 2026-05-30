# API Documentation

## Backup Manager API

### BackupManager Class

```python
from whatsapp_backup_manager.backup_manager import BackupManager

manager = BackupManager(config)
```

#### Methods

**list_local_backups()**
- List all local WhatsApp backups
- Returns: List[Dict] - Backup information

**list_cloud_backups()**
- List WhatsApp backups from Google Drive
- Returns: List[Dict] - Cloud backup information

**import_backup(backup_path, backup_id=None)**
- Import a WhatsApp backup
- Args:
  - backup_path (str): Path to backup file
  - backup_id (str, optional): Custom backup ID
- Returns: bool - Import success status

**verify_backup(backup_id)**
- Verify backup integrity
- Args: backup_id (str)
- Returns: bool - Verification result

## Media Organizer API

### MediaOrganizer Class

```python
from whatsapp_backup_manager.media_organizer import MediaOrganizer

organizer = MediaOrganizer(config)
```

#### Methods

**organize_backup(backup_id)**
- Organize all media from a backup
- Args: backup_id (str)
- Returns: Dict - Organization statistics

**filter_media(backup_id, media_type=None, start_date=None, end_date=None)**
- Filter media by type and date
- Args:
  - backup_id (str)
  - media_type (str, optional): images, videos, audio, documents
  - start_date (datetime, optional)
  - end_date (datetime, optional)
- Returns: List[Dict] - Filtered media files

**get_media_statistics(backup_id)**
- Get media statistics
- Args: backup_id (str)
- Returns: Dict - Statistics data

## Analysis Tool API

### AnalysisTool Class

```python
from whatsapp_backup_manager.analysis_tool import AnalysisTool

analyzer = AnalysisTool(config)
```

#### Methods

**analyze_backup(backup_id)**
- Perform comprehensive analysis
- Args: backup_id (str)
- Returns: Dict - Analysis results

**generate_report(backup_id, output_format='json')**
- Generate analysis report
- Args:
  - backup_id (str)
  - output_format (str): json, pdf, html, csv
- Returns: bool - Generation success status
