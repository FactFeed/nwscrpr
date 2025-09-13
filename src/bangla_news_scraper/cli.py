"""
Improved Command Line Interface for Bangla News Scraper
"""

import click
import time
from datetime import datetime
from pathlib import Path

from .scrapers.prothom_alo import ProthomAloScraper
from .scrapers.ittefaq import IttefaqScraper
from .utils.output import save_to_json, save_to_csv, display_articles_summary, validate_articles
from .utils.cache import ArticleCache
from .utils import setup_logger, get_logger
from .models import ScrapingResult
from .config import Config
from .exceptions import ScraperException

# Setup default logger
logger = get_logger()


@click.command()
@click.option('--run', '-r', is_flag=True, help='Run the scraper')
@click.option('--site', '-s', default='prothom-alo',
              type=click.Choice(Config.get_site_names()),
              help='News site to scrape')
@click.option('--limit', '-l', default=5, type=int,
              help='Number of articles to scrape (0 = get all available articles)')
@click.option('--output', '-o', default='json',
              type=click.Choice(['json', 'csv']),
              help='Output format')
@click.option('--output-dir', '-d', default='output',
              help='Output directory for saved files')
@click.option('--delay', default=1.0, type=float,
              help='Delay between requests in seconds')
@click.option('--verbose', '-v', is_flag=True,
              help='Enable verbose logging')
@click.option('--no-cache', is_flag=True,
              help='Disable caching')
@click.option('--clear-cache', is_flag=True,
              help='Clear cache before running')
@click.option('--cache-stats', is_flag=True,
              help='Show cache statistics')
def main(run, site, limit, output, output_dir, delay, verbose, no_cache, clear_cache, cache_stats):
    """
    Bangla News Scraper - Enhanced Version
    
    A tool to scrape news articles from Bangladeshi news websites with improved
    architecture, caching, and error handling.
    
    Examples:
        bangla-news-scraper --run --site=prothom-alo --limit=5 --output=json
        bangla-news-scraper --run --site=ittefaq --limit=3 --output=csv --verbose
        bangla-news-scraper -r -s prothom-alo -l 10 -o csv -d ./output
        bangla-news-scraper --cache-stats
        bangla-news-scraper --clear-cache
    """
    
    # Setup logging
    log_level = 'DEBUG' if verbose else 'INFO'
    setup_logger(level=log_level)
    
    # Initialize cache
    cache = ArticleCache()
    
    # Handle cache operations
    if cache_stats:
        stats = cache.get_cache_stats()
        click.echo("\n📊 Cache Statistics:")
        click.echo(f"   Total files: {stats['total_files']}")
        click.echo(f"   Valid files: {stats['valid_files']}")
        click.echo(f"   Expired files: {stats['expired_files']}")
        click.echo(f"   Total size: {stats['total_size_mb']} MB")
        return
    
    if clear_cache:
        cleared = cache.clear()
        click.echo(f"🗑️  Cleared {cleared} cached articles")
        if not run:
            return
    
    if not run:
        click.echo("Use --run or -r flag to start scraping.")
        click.echo("Use --help for more information.")
        return
    
    # Disable cache if requested
    if no_cache:
        Config.CACHE_ENABLED = False
        click.echo("🚫 Caching disabled")
    
    click.echo(f"🚀 Starting {site} scraper (Enhanced Version)...")
    if limit == 0:
        click.echo(f"📊 Target: ALL available articles")
    else:
        click.echo(f"📊 Target: {limit} articles")
    click.echo(f"💾 Output: {output} format")
    click.echo(f"📁 Directory: {output_dir}")
    click.echo(f"⏱️  Delay: {delay}s between requests")
    
    try:
        # Initialize scraper based on site
        start_time = time.time()
        
        if site == 'prothom-alo':
            scraper = ProthomAloScraper(delay=delay)
        elif site == 'ittefaq':
            scraper = IttefaqScraper(delay=delay)
        else:
            raise click.ClickException(f"Unsupported site: {site}")
        
        # Scrape articles
        click.echo("\n🔍 Scraping articles...")
        articles = scraper.scrape_articles(limit=limit)
        
        if not articles:
            click.echo("❌ No articles found or scraped successfully.")
            return
        
        # Validate articles
        click.echo("✅ Validating articles...")
        valid_articles = validate_articles(articles)
        
        if not valid_articles:
            click.echo("❌ No valid articles after validation.")
            return
        
        # Create scraping result
        end_time = time.time()
        duration = end_time - start_time
        
        result = ScrapingResult(
            articles=valid_articles,
            site_name=site,
            total_requested=limit,
            total_found=len(articles),
            total_valid=len(valid_articles),
            scraped_at=datetime.now().isoformat(),
            duration_seconds=duration
        )
        
        # Display summary
        display_articles_summary(result)
        
        # Save articles
        click.echo(f"\n💾 Saving {len(valid_articles)} articles...")
        
        if output == 'json':
            filepath = save_to_json(result, site, output_dir)
        elif output == 'csv':
            filepath = save_to_csv(result, site, output_dir)
        
        click.echo(f"✅ Successfully saved to: {filepath}")
        click.echo(f"📈 Total articles: {len(valid_articles)}")
        click.echo(f"⚡ Success rate: {result.get_success_rate():.1f}%")
        click.echo(f"⏱️  Duration: {duration:.2f} seconds")
        
    except KeyboardInterrupt:
        click.echo("\n⚠️  Scraping interrupted by user.")
    except ScraperException as e:
        click.echo(f"\n❌ Scraper error: {e}")
        logger.error(f"Scraping failed: {e}")
        raise click.ClickException(str(e))
    except Exception as e:
        click.echo(f"\n❌ Unexpected error: {e}")
        logger.error(f"Unexpected error: {e}")
        raise click.ClickException(str(e))


@click.command()
def version():
    """Show version information"""
    from . import __version__, __author__
    click.echo(f"Bangla News Scraper v{__version__}")
    click.echo(f"Author: {__author__}")
    click.echo("A Python package for scraping Bangladeshi news websites")


@click.group()
def cli():
    """Bangla News Scraper CLI - Enhanced Version"""
    pass


# Add commands to group
cli.add_command(main, name='scrape')
cli.add_command(version)


if __name__ == '__main__':
    main()