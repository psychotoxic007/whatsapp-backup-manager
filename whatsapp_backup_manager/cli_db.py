"""Database CLI - Command line interface for database operations."""

import click
from rich.console import Console
from rich.table import Table
from rich.json import JSON
import json
from pathlib import Path

from whatsapp_backup_manager.db_extractor import (
    WhatsAppDatabaseReader,
    MessageExtractor,
    ContactExtractor,
    MediaExtractor
)
from whatsapp_backup_manager.db_extractor.db_viewer import DatabaseViewer

console = Console()


@click.group()
def db_commands():
    """Database extraction and viewing commands."""
    pass


@db_commands.command()
@click.argument('db_path', type=click.Path(exists=True))
def info(db_path):
    """Display database information."""
    try:
        reader = WhatsAppDatabaseReader(db_path)
        if not reader.connect():
            console.print("[red]Failed to connect to database[/red]")
            return
        
        info = reader.get_database_info()
        console.print("[bold blue]Database Information:[/bold blue]")
        console.print(JSON(json.dumps(info, indent=2, default=str)))
        
        reader.disconnect()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@db_commands.command()
@click.argument('db_path', type=click.Path(exists=True))
def tables(db_path):
    """List all tables in database."""
    try:
        reader = WhatsAppDatabaseReader(db_path)
        if not reader.connect():
            console.print("[red]Failed to connect to database[/red]")
            return
        
        table_list = reader.get_tables()
        
        table = Table(title="Database Tables")
        table.add_column("Table Name", style="cyan")
        table.add_column("Row Count", style="magenta")
        
        for table_name in table_list:
            count = reader.get_table_row_count(table_name)
            table.add_row(table_name, str(count))
        
        console.print(table)
        reader.disconnect()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@db_commands.command()
@click.argument('db_path', type=click.Path(exists=True))
@click.option('--table', required=True, help='Table name')
@click.option('--limit', default=10, help='Limit number of rows')
def view_table(db_path, table, limit):
    """View table contents."""
    try:
        reader = WhatsAppDatabaseReader(db_path)
        if not reader.connect():
            console.print("[red]Failed to connect to database[/red]")
            return
        
        rows = reader.query_table(table, limit)
        
        if not rows:
            console.print(f"[yellow]No data found in table: {table}[/yellow]")
            return
        
        # Create table
        columns = list(rows[0].keys())
        table_display = Table(title=f"Table: {table}")
        
        for col in columns:
            table_display.add_column(col, style="cyan")
        
        for row in rows:
            table_display.add_row(*[str(row[col])[:50] for col in columns])
        
        console.print(table_display)
        reader.disconnect()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@db_commands.command()
@click.argument('db_path', type=click.Path(exists=True))
def messages(db_path):
    """Get message statistics."""
    try:
        reader = WhatsAppDatabaseReader(db_path)
        if not reader.connect():
            console.print("[red]Failed to connect to database[/red]")
            return
        
        extractor = MessageExtractor(reader)
        stats = extractor.get_message_statistics()
        
        console.print("[bold blue]Message Statistics:[/bold blue]")
        console.print(JSON(json.dumps(stats, indent=2)))
        
        reader.disconnect()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@db_commands.command()
@click.argument('db_path', type=click.Path(exists=True))
def contacts(db_path):
    """Get contact statistics."""
    try:
        reader = WhatsAppDatabaseReader(db_path)
        if not reader.connect():
            console.print("[red]Failed to connect to database[/red]")
            return
        
        extractor = ContactExtractor(reader)
        stats = extractor.get_contact_statistics()
        
        console.print("[bold blue]Contact Statistics:[/bold blue]")
        console.print(JSON(json.dumps(stats, indent=2)))
        
        reader.disconnect()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@db_commands.command()
@click.argument('db_path', type=click.Path(exists=True))
def media(db_path):
    """Get media statistics."""
    try:
        reader = WhatsAppDatabaseReader(db_path)
        if not reader.connect():
            console.print("[red]Failed to connect to database[/red]")
            return
        
        extractor = MediaExtractor(reader)
        stats = extractor.get_media_statistics()
        
        console.print("[bold blue]Media Statistics:[/bold blue]")
        console.print(JSON(json.dumps(stats, indent=2, default=str)))
        
        reader.disconnect()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@db_commands.command()
@click.argument('db_path', type=click.Path(exists=True))
@click.option('--output', required=True, help='Output directory')
@click.option('--format', multiple=True, default=['json', 'csv'], help='Export formats')
def export(db_path, output, format):
    """Export database contents."""
    try:
        viewer = DatabaseViewer(db_path)
        results = viewer.export_all(output, list(format))
        
        console.print("[bold green]Export completed:[/bold green]")
        console.print(JSON(json.dumps(results, indent=2)))
        
        viewer.close()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@db_commands.command()
@click.argument('db_path', type=click.Path(exists=True))
@click.argument('keyword')
def search(db_path, keyword):
    """Search across database."""
    try:
        viewer = DatabaseViewer(db_path)
        results = viewer.search_all(keyword)
        
        console.print(f"[bold blue]Search Results for '{keyword}':[/bold blue]")
        
        if results['messages']:
            console.print(f"\n[cyan]Messages found: {len(results['messages'])}[/cyan]")
            for msg in results['messages'][:5]:
                console.print(f"  - {str(msg)[:100]}")
        
        if results['contacts']:
            console.print(f"\n[cyan]Contacts found: {len(results['contacts'])}[/cyan]")
            for contact in results['contacts'][:5]:
                console.print(f"  - {contact.get('display_name', 'Unknown')}")
        
        viewer.close()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
