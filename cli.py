"""
Command Line Interface for Bangla News Scraper
"""

import click
import logging
from scraper import ProthomAloScraper, IttefaqScraper
from output_utils import save_to_json, save_to_csv, display_articles_summary, validate_articles

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@click.command()
@click.option('--run', '-r', is_flag=True, help='Run the scraper')
@click.option('--site', '-s', default='prothom-alo', 
              type=click.Choice(['prothom-alo', 'ittefaq']), 
              help='News site to scrape (prothom-alo or ittefaq)')
@click.option('--limit', '-l', default=5, type=int, 
              help='Number of articles to scrape (0 = get all available articles)')
@click.option('--output', '-o', default='json', 
              type=click.Choice(['json', 'csv']), 
              help='Output format')
@click.option('--output-dir', '-d', default='.', 
              help='Output directory for saved files')
@click.option('--delay', default=1.0, type=float, 
              help='Delay between requests in seconds')
@click.option('--verbose', '-v', is_flag=True, 
              help='Enable verbose logging')
def main(run, site, limit, output, output_dir, delay, verbose):
    """
    Bangla News Scraper
    
    A simple tool to scrape news articles from Bangladeshi news websites.
    
    Examples:
        news-scraper --run --site=prothom-alo --limit=5 --output=json
        news-scraper --run --site=ittefaq --limit=3 --output=csv
        news-scraper -r -s prothom-alo -l 10 -o csv -d ./output
    """
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if not run:
        click.echo("Use --run or -r flag to start scraping.")
        click.echo("Use --help for more information.")
        return
    
    click.echo(f"🚀 Starting {site} scraper...")
    if limit == 0:
        click.echo(f"📊 Target: ALL available articles")
    else:
        click.echo(f"📊 Target: {limit} articles")
    click.echo(f"💾 Output: {output} format")
    click.echo(f"📁 Directory: {output_dir}")
    
    try:
        # Initialize scraper based on site
        if site == 'prothom-alo':
            scraper = ProthomAloScraper(delay=delay)
        elif site == 'ittefaq':
            scraper = IttefaqScraper(delay=delay)
        else:
            click.echo(f"❌ Unsupported site: {site}")
            return
        
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
        
        # Display summary
        display_articles_summary(valid_articles)
        
        # Save articles
        click.echo(f"\n💾 Saving {len(valid_articles)} articles...")
        
        if output == 'json':
            filepath = save_to_json(valid_articles, site, output_dir)
        elif output == 'csv':
            filepath = save_to_csv(valid_articles, site, output_dir)
        
        click.echo(f"✅ Successfully saved to: {filepath}")
        click.echo(f"📈 Total articles: {len(valid_articles)}")
        
    except KeyboardInterrupt:
        click.echo("\n⚠️  Scraping interrupted by user.")
    except Exception as e:
        click.echo(f"\n❌ Error occurred: {e}")
        logger.error(f"Scraping failed: {e}")
        raise click.ClickException(str(e))


@click.command()
def version():
    """Show version information"""
    click.echo("Bangla News Scraper v1.0.0")
    click.echo("A simple web scraper for Bangladeshi news websites")


@click.group()
def cli():
    """Bangla News Scraper CLI"""
    pass


# Add commands to group
cli.add_command(main, name='scrape')
cli.add_command(version)


if __name__ == '__main__':
    main()