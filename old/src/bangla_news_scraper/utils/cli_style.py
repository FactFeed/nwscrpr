"""
Enhanced CLI visuals and styling utilities for Bangla News Scraper
"""

import time
from typing import Dict, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text
from rich.layout import Layout
from rich.align import Align
from rich import box
from rich.rule import Rule

# Initialize rich console
console = Console()

class CLITheme:
    """Color theme for the CLI"""
    PRIMARY = "cyan"
    SUCCESS = "green"
    ERROR = "red"
    WARNING = "yellow"
    INFO = "blue"
    ACCENT = "magenta"
    MUTED = "dim white"
    HIGHLIGHT = "bright_yellow"

def print_banner():
    """Display the application banner"""
    banner = Panel(
        Align.center(
            Text("BANGLA NEWS SCRAPER", style=f"bold {CLITheme.PRIMARY}")
        ),
        box=box.DOUBLE,
        border_style=CLITheme.PRIMARY,
        padding=(1, 2)
    )
    console.print(banner)

def print_separator():
    """Print a stylized separator"""
    console.print(Rule(style=CLITheme.MUTED))

def print_section_header(title: str, icon: str = "📋"):
    """Print a section header with icon and styling"""
    header = Text()
    header.append(f"{icon} ", style=CLITheme.ACCENT)
    header.append(title.upper(), style=f"bold {CLITheme.PRIMARY}")
    console.print(header)

def print_config_info(site: str, limit: int, output: str, output_dir: str, delay: float):
    """Display configuration information in a nice table"""
    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    table.add_column("Setting", style=CLITheme.INFO)
    table.add_column("Value", style="white")
    
    if site == 'all':
        from ..config import Config
        site_display = f"All Sites ({', '.join(Config.get_site_names())})"
    else:
        site_display = site.title()
    
    limit_display = "All Available" if limit == 0 else str(limit)
    
    table.add_row("🌐 Target", site_display)
    table.add_row("📊 Articles", f"{limit_display} per site")
    table.add_row("💾 Format", output.upper())
    table.add_row("📁 Directory", output_dir)
    table.add_row("⏱️  Delay", f"{delay}s")
    
    console.print(Panel(table, title="Configuration", border_style=CLITheme.INFO))

def print_cache_stats(stats: Dict):
    """Display cache statistics in a formatted table"""
    table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
    table.add_column("Metric", style=CLITheme.INFO)
    table.add_column("Value", style="white")
    
    table.add_row("📁 Total Files", str(stats['total_files']))
    table.add_row("✅ Valid Files", str(stats['valid_files']))
    table.add_row("⏰ Expired Files", str(stats['expired_files']))
    table.add_row("💾 Total Size", f"{stats['total_size_mb']} MB")
    
    console.print(Panel(table, title="📊 Cache Statistics", border_style=CLITheme.INFO))

def print_success(message: str, icon: str = "✅"):
    """Print a success message"""
    console.print(f"{icon} {message}", style=CLITheme.SUCCESS)

def print_error(message: str, icon: str = "❌"):
    """Print an error message"""
    console.print(f"{icon} {message}", style=CLITheme.ERROR)

def print_warning(message: str, icon: str = "⚠️"):
    """Print a warning message"""
    console.print(f"{icon} {message}", style=CLITheme.WARNING)

def print_info(message: str, icon: str = "ℹ️"):
    """Print an info message"""
    console.print(f"{icon} {message}", style=CLITheme.INFO)

def print_site_header(site_name: str):
    """Print a styled header for each site being scraped"""
    site_display = site_name.replace('-', ' ').title()
    header = Panel(
        Align.center(f"🔍 SCRAPING {site_display.upper()}"),
        box=box.ROUNDED,
        border_style=CLITheme.ACCENT,
        padding=(0, 2)
    )
    console.print(header)

def print_site_result(site_name: str, article_count: int, duration: float, success: bool = True):
    """Print the result for a scraped site"""
    if success:
        message = f"✅ {site_name}: [bold green]{article_count}[/bold green] articles in [dim]{duration:.2f}s[/dim]"
    else:
        message = f"❌ {site_name}: [bold red]Failed[/bold red] in [dim]{duration:.2f}s[/dim]"
    
    console.print(message)

def print_overall_summary(sites_count: int, total_articles: int, total_duration: float, success_rate: float):
    """Display overall scraping summary"""
    print_section_header("SCRAPING COMPLETE", "🎉")
    
    table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
    table.add_column("Metric", style=CLITheme.INFO)
    table.add_column("Value", style="white")
    
    table.add_row("🌐 Sites Scraped", str(sites_count))
    table.add_row("📰 Total Articles", str(total_articles))
    table.add_row("📈 Success Rate", f"{success_rate:.1f}%")
    table.add_row("⏱️  Total Time", f"{total_duration:.2f}s")
    
    console.print(Panel(table, title="📊 Overall Summary", border_style=CLITheme.SUCCESS))

def print_file_saved(site_name: str, filepath: str):
    """Print file save confirmation"""
    filename = filepath.split('\\')[-1] if '\\' in filepath else filepath.split('/')[-1]
    console.print(f"💾 [bold]{site_name}[/bold]: Saved to [link]{filename}[/link]", style=CLITheme.SUCCESS)

def create_progress_bar(description: str = "Processing"):
    """Create a styled progress bar"""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    )

def print_help_message():
    """Display help message"""
    help_panel = Panel(
        "[dim]Use [bold]--run[/bold] or [bold]-r[/bold] flag to start scraping.\n"
        "Use [bold]--help[/bold] for more information.[/dim]",
        title="💡 Help",
        border_style=CLITheme.INFO
    )
    console.print(help_panel)

def print_startup_message():
    """Display startup message with banner"""
    print_banner()
    console.print()