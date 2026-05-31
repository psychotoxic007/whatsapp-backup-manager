"""Command Line Interface for WhatsApp Backup Manager."""

import click
import logging
import sys
from pathlib import Path
from colorama import Fore, Style, init
from rich.console import Console
from rich.table import Table

from whatsapp_backup_manager.backup_manager.analytics_manager import AnalyticsManager
from whatsapp_backup_manager.backup_manager.cloud_manager import CloudManager

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('whatsapp_backup_manager.log')
    ]
)
logger = logging.getLogger(__name__)
console = Console()


@click.group()
def cli():
    """WhatsApp Backup Manager — Manage your WhatsApp backups with analysis & cloud sync."""
    pass


@click.group()
def backup():
    """Backup management operations."""
    pass


@backup.command('list-drive')
def list_drive_backups():
    """List all WhatsApp backup files from Google Drive."""
    try:
        click.echo(f"\n{Fore.CYAN}{'='*60}")
        click.echo(f"{Fore.CYAN}  WhatsApp Backup Manager — Google Drive Backups")
        click.echo(f"{Fore.CYAN}{'='*60}\n")
        
        click.echo(f"{Fore.YELLOW}▶ Initializing Google Drive connection...")
        cloud_manager = CloudManager()
        
        click.echo(f"{Fore.YELLOW}▶ Searching for backup files...\n")
        backups = cloud_manager.list_backups(max_results=50)

        if not backups:
            click.echo(f"{Fore.YELLOW}⚠  No backup files found on Google Drive.\n")
            return

        click.echo(f"{Fore.GREEN}✓  Found {len(backups)} backup file(s):\n")
        click.echo(f"{Fore.CYAN}{'File Name':<40} {'Size':<15} {'Modified':<12}")
        click.echo(f"{Fore.CYAN}{'-'*67}")

        for backup_file in backups:
            raw_size = backup_file.get('size', 0)
            size_int = int(raw_size) if str(raw_size).isdigit() else 0
            name = (backup_file['name'] or '')[:38]
            size = _format_size(size_int)
            modified = (backup_file.get('modified_time') or 'Unknown')[:10]

            click.echo(f"{Fore.WHITE}{name:<40} {size:<15} {modified:<12}")
            click.echo(f"  {Fore.BLUE}├─ ID      : {backup_file['id']}")
            click.echo(f"  {Fore.BLUE}├─ Created : {backup_file.get('created_time', 'N/A')}")
            click.echo(f"  {Fore.BLUE}├─ MIME    : {backup_file.get('mime_type', 'N/A')}")
            click.echo(f"  {Fore.BLUE}└─ Link    : {backup_file.get('web_view_link', 'N/A')}\n")

        click.echo(f"{Fore.GREEN}{'='*60}")
        click.echo(f"{Fore.GREEN}✓  Done — retrieved from Google Drive")
        click.echo(f"{Fore.GREEN}{'='*60}\n")
    except Exception as e:
        click.echo(f"\n{Fore.RED}✗  Unexpected error: {e}")
        logger.exception("Exception in list_drive_backups")
        sys.exit(1)


@backup.command('download')
@click.argument('file_id')
@click.argument('output_path', type=click.Path())
def download_backup(file_id, output_path):
    """Download a backup file from Google Drive.
    
    FILE_ID: Google Drive file ID
    OUTPUT_PATH: Local path to save file
    """
    try:
        click.echo(f"\n{Fore.YELLOW}▶ Downloading backup...\n")
        cloud_manager = CloudManager()
        
        file_info = cloud_manager.get_backup_info(file_id)
        if not file_info:
            click.echo(f"{Fore.RED}✗ File not found")
            sys.exit(1)
        
        click.echo(f"{Fore.GREEN}File: {file_info['name']}")
        click.echo(f"{Fore.GREEN}Size: {_format_size(int(file_info['size']) if file_info['size'] else 0)}\n")
        
        success = cloud_manager.download_backup(file_id, output_path)
        if success:
            click.echo(f"{Fore.GREEN}✓  Download complete: {output_path}")
        else:
            click.echo(f"{Fore.RED}✗ Download failed")
            sys.exit(1)
    except Exception as e:
        click.echo(f"{Fore.RED}✗  Error: {e}")
        logger.exception("Exception in download_backup")
        sys.exit(1)


@backup.command('import')
@click.argument('backup_path', type=click.Path(exists=True))
def import_backup(backup_path):
    """Import a local WhatsApp backup file.
    
    BACKUP_PATH: Path to backup file
    """
    try:
        import shutil
        target_dir = Path("./backups")
        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(Path(backup_path), target_dir / Path(backup_path).name)
        click.echo(f"\n{Fore.GREEN}✓ Successfully imported backup file!{Fore.RESET}\n")
    except Exception as e:
        click.echo(f"{Fore.RED}Error: {e}")
        sys.exit(1)


@cli.command('analyze')
@click.argument('db_path', type=click.Path(exists=True))
@click.option('--all-chats', '-a', is_flag=True, help='Display entire conversation list.')
def analyze_database(db_path, all_chats):
    """Analyze WhatsApp database and display chat statistics.
    
    DB_PATH: Path to decrypted WhatsApp database file
    """
    try:
        click.echo(f"\n{Fore.CYAN}{'='*60}")
        click.echo(f"{Fore.CYAN}  WhatsApp Backup Manager — Chat Insights Engine")
        click.echo(f"{Fore.CYAN}{'='*60}\n")
        
        engine = AnalyticsManager(db_path)
        stats = engine.get_basic_stats()
        
        click.echo(f"📊 {Fore.GREEN}General Statistics:{Fore.RESET}")
        click.echo(f"  • Total Chats Indexed : {stats['total_chats']}")
        click.echo(f"  • Total Messages      : {stats['total_messages']}")
        click.echo(f"  • Text Messages       : {stats['text_messages']}")
        click.echo(f"  • Media Attachments   : {stats['media_messages']}\n")
        
        limit_val = -1 if all_chats else 5
        top = engine.get_top_contacts(limit=limit_val)
        
        title = "Complete Ranked Chat List (Includes Deleted Log Threads):" if all_chats else "Top Active Conversations:"
        click.echo(f"🏆 {Fore.GREEN}{title}{Fore.RESET}")
        
        for i, contact in enumerate(top, 1):
            click.echo(f"  {Fore.WHITE}{i}. {contact[0]:<35} ({contact[1]} records)")
            
        click.echo(f"\n{Fore.CYAN}{'='*60}\n")
    except Exception as e:
        click.echo(f"{Fore.RED}Error: {e}")
        logger.exception("Exception in analyze_database")
        sys.exit(1)


@cli.command('view')
@click.argument('db_path', type=click.Path(exists=True))
@click.argument('name')
@click.option('--limit', '-l', default=20, help='Number of recent messages to show.')
def view_messages(db_path, name, limit):
    """View recent messages from a specific contact.
    
    DB_PATH: Path to decrypted WhatsApp database
    NAME: Contact name or phone number
    """
    try:
        engine = AnalyticsManager(db_path)
        messages = engine.get_chat_messages(name, limit=limit)
        
        click.echo(f"\n{Fore.CYAN}--- Reading Messages for: {name} ---{Fore.RESET}\n")
        count = 0
        for from_me, text, timestamp in messages:
            sender = f"{Fore.GREEN}You" if from_me == 1 else f"{Fore.YELLOW}{name}"
            click.echo(f"{sender}: {Fore.WHITE}{text}")
            count += 1
            
        if count == 0:
            click.echo(f"{Fore.RED}No messages found matching '{name}'.")
        click.echo(f"\n{Fore.CYAN}-----------------------------------{Fore.RESET}\n")
    except Exception as e:
        click.echo(f"{Fore.RED}Error: {e}")
        logger.exception("Exception in view_messages")
        sys.exit(1)


def _format_size(b: int) -> str:
    """Format bytes to human-readable size."""
    for unit in ('B', 'KB', 'MB', 'GB', 'TB'):
        if b < 1024:
            return f"{b:.2f} {unit}"
        b /= 1024
    return f"{b:.2f} PB"


cli.add_command(backup)
main = cli

if __name__ == '__main__':
    main()
