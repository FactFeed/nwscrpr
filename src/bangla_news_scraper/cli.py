"""
Enhanced Command Line Interface for Bangla News Scraper with Rich Styling
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
from .utils.cli_style import (
    print_startup_message, print_config_info, print_cache_stats,
    print_success, print_error, print_warning, print_info,
    print_site_header, print_site_result, print_overall_summary,
    print_file_saved, print_help_message, print_separator
)
from .models import ScrapingResult
from .config import Config
from .exceptions import ScraperException

# Setup default logger
logger = get_logger()


def get_scraper_instance(site_name: str, delay: float):
    """Get scraper instance for a given site"""
    if site_name == 'prothom-alo':
        return ProthomAloScraper(delay=delay)
    elif site_name == 'ittefaq':
        return IttefaqScraper(delay=delay)
    else:
        raise click.ClickException(f"Unsupported site: {site_name}")


def scrape_single_site(site_name: str, limit: int, delay: float, output: str, output_dir: str):
    """Scrape articles from a single site and return the result"""
    print_site_header(site_name)
    
    start_time = time.time()
    scraper = get_scraper_instance(site_name, delay)
    
    # Scrape articles
    articles = scraper.scrape_articles(limit=limit)
    
    if not articles:
        duration = time.time() - start_time
        print_site_result(site_name, 0, duration, success=False)
        print_error(f"No articles found from {site_name}")
        return None
    
    # Validate articles
    valid_articles = validate_articles(articles)
    
    if not valid_articles:
        duration = time.time() - start_time
        print_site_result(site_name, 0, duration, success=False)
        print_error(f"No valid articles from {site_name} after validation")
        return None
    
    # Create scraping result
    end_time = time.time()
    duration = end_time - start_time
    
    result = ScrapingResult(
        articles=valid_articles,
        site_name=site_name,
        total_requested=limit,
        total_found=len(articles),
        total_valid=len(valid_articles),
        scraped_at=datetime.now().isoformat(),
        duration_seconds=duration
    )
    
    print_site_result(site_name, len(valid_articles), duration, success=True)
    return result


@click.command()
@click.option('--run', '-r', is_flag=True, help='Run the scraper')
@click.option('--site', '-s', default='prothom-alo',
              type=click.Choice(Config.get_site_names() + ['all']),
              help='News site to scrape (use "all" to scrape from all sites)')
@click.option('--limit', '-l', default=5, type=int,
              help='Number of articles to scrape per site (0 = get all available articles)')
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
    🇧🇩 Bangla News Scraper - Enhanced Version
    
    A powerful tool to scrape news articles from Bangladeshi news websites with
    modern architecture, intelligent caching, and beautiful CLI interface.
    
    Examples:
        python main.py --run --site=prothom-alo --limit=5 --output=json
        python main.py --run --site=all --limit=3 --output=csv --verbose
        python main.py -r -s prothom-alo -l 10 -o csv -d ./output
        python main.py --cache-stats
        python main.py --clear-cache
    """
    
    # Setup logging
    log_level = 'DEBUG' if verbose else 'INFO'
    setup_logger(level=log_level)
    
    # Display startup banner
    print_startup_message()
    
    # Initialize cache
    cache = ArticleCache()
    
    # Handle cache operations
    if cache_stats:
        stats = cache.get_cache_stats()
        print_cache_stats(stats)
        return
    
    if clear_cache:
        cleared = cache.clear()
        print_success(f"Cleared {cleared} cached articles", "🗑️")
        if not run:
            return
    
    if not run:
        print_help_message()
        return
    
    # Disable cache if requested
    if no_cache:
        Config.CACHE_ENABLED = False
        print_warning("Caching disabled", "�")
    
    # Display configuration
    print_config_info(site, limit, output, output_dir, delay)
    print_separator()
    
    try:
        # Initialize scraper based on site
        start_time = time.time()
        all_results = []
        
        if site == 'all':
            # Scrape from all configured sites
            sites_to_scrape = Config.get_site_names()
            print_info(f"Scraping from {len(sites_to_scrape)} sites", "🔍")
            
            for site_name in sites_to_scrape:
                try:
                    result = scrape_single_site(site_name, limit, delay, output, output_dir)
                    if result:
                        all_results.append(result)
                except Exception as e:
                    print_error(f"Error scraping {site_name}: {e}")
                    logger.error(f"Error scraping {site_name}: {e}")
                    continue
                    
            if not all_results:
                print_error("No articles found from any site")
                return
                
        else:
            # Scrape from single site
            result = scrape_single_site(site, limit, delay, output, output_dir)
            if not result:
                return
            all_results = [result]
        
        # Calculate total statistics
        total_duration = time.time() - start_time
        total_articles = sum(len(result.articles) for result in all_results)
        total_requested = sum(result.total_requested for result in all_results)
        total_found = sum(result.total_found for result in all_results)
        success_rate = (total_articles/total_found*100) if total_found > 0 else 0
        
        print_separator()
        
        # Display summary for each site (only if multiple sites)
        if len(all_results) > 1:
            for result in all_results:
                display_articles_summary(result)
        else:
            display_articles_summary(all_results[0])
        
        # Display overall summary
        if len(all_results) > 1:
            print_overall_summary(len(all_results), total_articles, total_duration, success_rate)
        
        # Save articles
        print_separator()
        print_info("Saving articles", "💾")
        
        if site == 'all':
            # Save each site separately
            for result in all_results:
                if output == 'json':
                    filepath = save_to_json(result, result.site_name, output_dir)
                elif output == 'csv':
                    filepath = save_to_csv(result, result.site_name, output_dir)
                print_file_saved(result.site_name, filepath)
        else:
            # Save single site
            result = all_results[0]
            if output == 'json':
                filepath = save_to_json(result, site, output_dir)
            elif output == 'csv':
                filepath = save_to_csv(result, site, output_dir)
            print_file_saved(site, filepath)
        
        print_separator()
        print_success(f"Successfully saved {total_articles} articles in {total_duration:.2f}s", "🎉")
        
    except KeyboardInterrupt:
        print_warning("Scraping interrupted by user", "⚠️")
    except ScraperException as e:
        print_error(f"Scraper error: {e}")
        logger.error(f"Scraping failed: {e}")
        raise click.ClickException(str(e))
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        logger.error(f"Unexpected error: {e}")
        raise click.ClickException(str(e))


@click.command()
def version():
    """Show version information"""
    from . import __version__, __author__
    print_startup_message()
    print_info(f"Version: {__version__}", "📋")
    print_info(f"Author: {__author__}", "👨‍💻")
    print_info("A modern Python package for scraping Bangladeshi news websites", "📰")


@click.group()
def cli():
    """Bangla News Scraper CLI - Enhanced Version"""
    pass


# Add commands to group
cli.add_command(main, name='scrape')
cli.add_command(version)


if __name__ == '__main__':
    main()