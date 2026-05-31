"""Updated CLI with media export and deleted chat viewing features."""

import click
import logging
import sys
from pathlib import Path
from colorama import Fore, Style, init
from rich.console import Console
from rich.table import Table

from whatsapp_backup_manager.backup_manager.analytics_manager import AnalyticsManager
from whatsapp_backup_manager.backup_manager.cloud_manager import CloudManager
from whatsapp_backup_manager.backup_manager.media_manager import MediaManager
from whatsapp_backup_manager.backup_manager.deleted_chat_manager import DeletedChatManager

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
    """WhatsApp Backup Manager — Advanced backup management with media & deleted chat recovery."""
    pass


@click.group()
def backup():
    """Backup management operations."""
    pass


@click.group()
def media():
    """Media extraction and export operations."""
    pass


@click.group()
def deleted():
    """Deleted chat and message recovery operations."""
    pass


# ===== BACKUP COMMANDS =====

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
        click.echo(f"\n{Fore.RED}✗  Error: {e}")
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


# ===== MEDIA COMMANDS =====

@media.command('list')
@click.argument('db_path', type=click.Path(exists=True))
@click.option('--type', '-t', default=None, help='Filter by media type (image, video, audio, document)')
@click.option('--include-deleted', is_flag=True, default=True, help='Include deleted media')
def list_media(db_path, type, include_deleted):
    """List all media files in database.
    
    DB_PATH: Path to decrypted WhatsApp database
    """
    try:
        click.echo(f"\n{Fore.CYAN}{'='*80}")
        click.echo(f"{Fore.CYAN}  WhatsApp Media Manager — Media Files Inventory")
        click.echo(f"{Fore.CYAN}{'='*80}\n")
        
        manager = MediaManager(db_path)
        
        if type:
            media = manager.get_media_by_type(type, include_deleted)
            click.echo(f"{Fore.GREEN}✓  Found {len(media)} {type.upper()} files\n")
        else:
            media = manager.get_all_media(include_deleted)
            stats = manager.get_media_statistics(include_deleted)
            click.echo(f"{Fore.GREEN}✓  Total Media: {stats['total_media']} files ({_format_size(stats['total_size'])})\n")
            click.echo(f"{Fore.YELLOW}By Type:")
            for media_type, count in stats['by_type'].items():
                if count > 0:
                    click.echo(f"  • {media_type.title():<15} : {count} files")
            click.echo()
        
        # Display as table
        table = Table(title="Media Files", show_header=True, header_style="bold cyan")
        table.add_column("#", style="magenta")
        table.add_column("Type", style="green")
        table.add_column("Chat", style="yellow")
        table.add_column("Filename", style="white")
        table.add_column("Size", style="blue")
        table.add_column("Date", style="cyan")
        
        from datetime import datetime
        for i, item in enumerate(media[:50], 1):  # Show first 50
            timestamp = datetime.fromtimestamp(item['timestamp'] / 1000) if item['timestamp'] else None
            date_str = timestamp.strftime('%Y-%m-%d') if timestamp else 'Unknown'
            size_str = _format_size(item['media_size']) if item['media_size'] else 'Unknown'
            filename = item['media_name'] or 'No name'
            
            table.add_row(
                str(i),
                item['media_type_name'].upper(),
                item['chat_name'][:20],
                filename[:30],
                size_str,
                date_str
            )
        
        console.print(table)
        
        if len(media) > 50:
            click.echo(f"\n{Fore.YELLOW}... and {len(media) - 50} more files")
        
        click.echo()
    except Exception as e:
        click.echo(f"{Fore.RED}Error: {e}")
        logger.exception("Exception in list_media")
        sys.exit(1)


@media.command('export')
@click.argument('db_path', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path())
@click.option('--type', '-t', default=None, help='Filter by media type')
@click.option('--include-deleted', is_flag=True, default=True, help='Include deleted media')
@click.option('--backup-dir', '-b', default=None, help='WhatsApp backup directory')
def export_media_files(db_path, output_dir, type, include_deleted, backup_dir):
    """Export all media files to directory.
    
    DB_PATH: Path to decrypted database
    OUTPUT_DIR: Output directory for media files
    """
    try:
        click.echo(f"\n{Fore.CYAN}{'='*80}")
        click.echo(f"{Fore.CYAN}  Exporting Media Files...")
        click.echo(f"{Fore.CYAN}{'='*80}\n")
        
        manager = MediaManager(db_path, backup_dir)
        
        click.echo(f"{Fore.YELLOW}▶ Scanning database...")
        results = manager.export_media_files(output_dir, type, include_deleted, backup_dir)
        
        click.echo(f"\n{Fore.GREEN}✓  Export Complete:")
        click.echo(f"  • Total files   : {results['total_files']}")
        click.echo(f"  • Exported      : {results['exported']}")
        click.echo(f"  • Failed        : {results['failed']}")
        click.echo(f"  • Skipped       : {results['skipped']}")
        click.echo(f"  • Output dir    : {output_dir}\n")
        
        if results['exported'] > 0:
            click.echo(f"{Fore.GREEN}✓  Media exported successfully to: {output_dir}")
    except Exception as e:
        click.echo(f"{Fore.RED}✗  Error: {e}")
        logger.exception("Exception in export_media")
        sys.exit(1)


@media.command('metadata')
@click.argument('db_path', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path())
@click.option('--format', '-f', default='json', type=click.Choice(['json', 'csv']))
def export_media_metadata(db_path, output_file, format):
    """Export media metadata to file.
    
    DB_PATH: Path to decrypted database
    OUTPUT_FILE: Output file path
    """
    try:
        manager = MediaManager(db_path)
        success = manager.export_media_metadata(output_file, format)
        
        if success:
            click.echo(f"{Fore.GREEN}✓  Metadata exported to: {output_file}")
        else:
            click.echo(f"{Fore.RED}✗  Failed to export metadata")
            sys.exit(1)
    except Exception as e:
        click.echo(f"{Fore.RED}✗  Error: {e}")
        logger.exception("Exception in export_media_metadata")
        sys.exit(1)


# ===== DELETED CHAT COMMANDS =====

@deleted.command('list-chats')
@click.argument('db_path', type=click.Path(exists=True))
def list_deleted_chats(db_path):
    """List all deleted chat threads.
    
    DB_PATH: Path to decrypted database
    """
    try:
        click.echo(f"\n{Fore.CYAN}{'='*80}")
        click.echo(f"{Fore.CYAN}  Deleted Chats Recovery")
        click.echo(f"{Fore.CYAN}{'='*80}\n")
        
        manager = DeletedChatManager(db_path)
        chats = manager.get_deleted_chats()
        
        if not chats:
            click.echo(f"{Fore.YELLOW}No deleted chats found.\n")
            return
        
        click.echo(f"{Fore.GREEN}✓  Found {len(chats)} deleted chats:\n")
        
        table = Table(title="Deleted Chats", show_header=True, header_style="bold red")
        table.add_column("#", style="magenta")
        table.add_column("Chat Name", style="yellow")
        table.add_column("JID", style="cyan")
        table.add_column("Messages", style="green")
        table.add_column("Created", style="blue")
        
        from datetime import datetime
        for i, chat in enumerate(chats, 1):
            created = datetime.fromtimestamp(chat['creation_time'] / 1000) if chat['creation_time'] else None
            created_str = created.strftime('%Y-%m-%d') if created else 'Unknown'
            
            table.add_row(
                str(i),
                chat['name'][:30],
                chat['jid'][:25] if chat['jid'] else 'N/A',
                str(chat['message_count']),
                created_str
            )
        
        console.print(table)
        click.echo()
    except Exception as e:
        click.echo(f"{Fore.RED}✗  Error: {e}")
        logger.exception("Exception in list_deleted_chats")
        sys.exit(1)


@deleted.command('view-messages')
@click.argument('db_path', type=click.Path(exists=True))
@click.option('--chat-id', '-c', default=None, type=int, help='Specific chat ID')
@click.option('--limit', '-l', default=50, type=int, help='Max messages')
def view_deleted_messages(db_path, chat_id, limit):
    """View deleted messages.
    
    DB_PATH: Path to decrypted database
    """
    try:
        click.echo(f"\n{Fore.CYAN}{'='*80}")
        click.echo(f"{Fore.CYAN}  Deleted Messages Recovery")
        click.echo(f"{Fore.CYAN}{'='*80}\n")
        
        manager = DeletedChatManager(db_path)
        messages = manager.get_deleted_messages(chat_id, limit)
        
        if not messages:
            click.echo(f"{Fore.YELLOW}No deleted messages found.\n")
            return
        
        click.echo(f"{Fore.GREEN}✓  Found {len(messages)} deleted messages:\n")
        
        table = Table(title="Deleted Messages", show_header=True, header_style="bold red")
        table.add_column("#", style="magenta")
        table.add_column("Chat", style="yellow")
        table.add_column("From", style="cyan")
        table.add_column("Message", style="white")
        table.add_column("Date", style="blue")
        
        for i, msg in enumerate(messages[:30], 1):  # Show first 30
            sender = "You" if msg['from_me'] else "Other"
            text = (msg['text'] or msg['media_name'] or "[Media]")[:50]
            date_str = msg['date'].split('T')[0] if msg['date'] else 'Unknown'
            
            table.add_row(
                str(i),
                msg['chat_name'][:20],
                sender,
                text,
                date_str
            )
        
        console.print(table)
        
        if len(messages) > 30:
            click.echo(f"\n{Fore.YELLOW}... and {len(messages) - 30} more messages")
        
        click.echo()
    except Exception as e:
        click.echo(f"{Fore.RED}✗  Error: {e}")
        logger.exception("Exception in view_deleted_messages")
        sys.exit(1)


@deleted.command('export')
@click.argument('db_path', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path())
@click.option('--type', '-t', default='chats', type=click.Choice(['chats', 'messages', 'all']))
@click.option('--format', '-f', default='json', type=click.Choice(['json', 'csv']))
@click.option('--chat-id', '-c', default=None, type=int, help='Specific chat ID')
def export_deleted(db_path, output_file, type, format, chat_id):
    """Export deleted chats and messages.
    
    DB_PATH: Path to decrypted database
    OUTPUT_FILE: Output file path
    """
    try:
        click.echo(f"\n{Fore.YELLOW}▶ Exporting deleted {type}...\n")
        manager = DeletedChatManager(db_path)
        
        success = False
        if type == 'chats':
            success = manager.export_deleted_chats(output_file, format)
        elif type == 'messages':
            success = manager.export_deleted_messages(output_file, chat_id, format)
        elif type == 'all':
            # Export both
            base = Path(output_file).stem
            dir_path = Path(output_file).parent
            success = manager.export_deleted_chats(str(dir_path / f"{base}_chats.{format}"), format)
            success = manager.export_deleted_messages(str(dir_path / f"{base}_messages.{format}"), None, format) and success
        
        if success:
            click.echo(f"{Fore.GREEN}✓  Exported to: {output_file}")
        else:
            click.echo(f"{Fore.RED}✗  Export failed")
            sys.exit(1)
    except Exception as e:
        click.echo(f"{Fore.RED}✗  Error: {e}")
        logger.exception("Exception in export_deleted")
        sys.exit(1)


# ===== ANALYSIS COMMANDS =====

@cli.command('analyze')
@click.argument('db_path', type=click.Path(exists=True))
@click.option('--all-chats', '-a', is_flag=True, help='Display all chats')
def analyze_database(db_path, all_chats):
    """Analyze database and display statistics.
    
    DB_PATH: Path to decrypted database
    """
    try:
        click.echo(f"\n{Fore.CYAN}{'='*80}")
        click.echo(f"{Fore.CYAN}  WhatsApp Chat Insights Engine")
        click.echo(f"{Fore.CYAN}{'='*80}\n")
        
        engine = AnalyticsManager(db_path)
        stats = engine.get_basic_stats()
        
        click.echo(f"📊 {Fore.GREEN}General Statistics:{Fore.RESET}")
        click.echo(f"  • Total Chats     : {stats['total_chats']}")
        click.echo(f"  • Total Messages  : {stats['total_messages']}")
        click.echo(f"  • Text Messages   : {stats['text_messages']}")
        click.echo(f"  • Media Messages  : {stats['media_messages']}\n")
        
        limit_val = -1 if all_chats else 5
        top = engine.get_top_contacts(limit=limit_val)
        
        title = "All Chats (Ranked):" if all_chats else "Top 5 Active Conversations:"
        click.echo(f"🏆 {Fore.GREEN}{title}{Fore.RESET}")
        
        for i, contact in enumerate(top, 1):
            click.echo(f"  {Fore.WHITE}{i}. {contact[0]:<35} ({contact[1]} messages)")
        
        click.echo(f"\n{Fore.CYAN}{'='*80}\n")
    except Exception as e:
        click.echo(f"{Fore.RED}Error: {e}")
        logger.exception("Exception in analyze_database")
        sys.exit(1)


@cli.command('view')
@click.argument('db_path', type=click.Path(exists=True))
@click.argument('name')
@click.option('--limit', '-l', default=20, type=int, help='Max messages')
def view_messages(db_path, name, limit):
    """View messages from specific contact.
    
    DB_PATH: Path to decrypted database
    NAME: Contact name or phone
    """
    try:
        engine = AnalyticsManager(db_path)
        messages = engine.get_chat_messages(name, limit=limit)
        
        click.echo(f"\n{Fore.CYAN}--- Messages from: {name} ---{Fore.RESET}\n")
        count = 0
        for from_me, text, timestamp in messages:
            sender = f"{Fore.GREEN}You" if from_me == 1 else f"{Fore.YELLOW}{name}"
            click.echo(f"{sender}: {Fore.WHITE}{text}")
            count += 1
        
        if count == 0:
            click.echo(f"{Fore.RED}No messages found for '{name}'.")
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


# Register command groups
cli.add_command(backup)
cli.add_command(media)
cli.add_command(deleted)
main = cli

if __name__ == '__main__':
    main()
