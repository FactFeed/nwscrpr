# Bangla News Scraper

A simple command-line tool to scrape news articles from Bangladeshi news websites.

## Features

- 🚀 Simple CLI interface
- 📰 Scrapes multiple Bangladeshi news sites (Prothom Alo, Ittefaq)
- 📄 Extracts full articles (title, content, author, date, URL, main image)
- 🖼️ Extracts main article images (featured/hero images)
- 🔤 Proper UTF-8 encoding for Bengali text
- 💾 Export to JSON or CSV formats
- 🛡️ Error handling and retry mechanisms
- ⏱️ Rate limiting to avoid blocking
- 📊 Clean, structured output

## Installation

1. Clone or download this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
# Scrape 5 articles from Prothom Alo and save as JSON
python news_scraper.py --run --site=prothom-alo --limit=5 --output=json

# Scrape 3 articles from Ittefaq and save as CSV
python news_scraper.py --run --site=ittefaq --limit=3 --output=csv

# Get ALL available articles from today (limit=0)
python news_scraper.py --run --site=prothom-alo --limit=0 --output=json

# Short form
python news_scraper.py -r -s prothom-alo -l 5 -o json
python news_scraper.py -r -s ittefaq -l 5 -o json
```

### Advanced Usage

```bash
# Get ALL available articles from today 
python news_scraper.py -r -s prothom-alo -l 0 -o json
python news_scraper.py -r -s ittefaq -l 0 -o json

# Scrape 10 articles and save as CSV
python news_scraper.py -r -s prothom-alo -l 10 -o csv

# Save to specific directory with custom delay
python news_scraper.py -r -s prothom-alo -l 5 -o json -d ./output --delay 2.0

# Enable verbose logging
python news_scraper.py -r -s prothom-alo -l 5 -o json --verbose
```

### Command Options

- `--run` / `-r`: Run the scraper (required)
- `--site` / `-s`: News site to scrape (`prothom-alo` or `ittefaq`)
- `--limit` / `-l`: Number of articles to scrape (default: 5, use 0 for all available articles)
- `--output` / `-o`: Output format - `json` or `csv` (default: json)
- `--output-dir` / `-d`: Output directory (default: current directory)
- `--delay`: Delay between requests in seconds (default: 1.0)
- `--verbose` / `-v`: Enable verbose logging

## Output

### JSON Format
Articles are saved as `YYYY-MM-DD_sitename.json` with the following structure:

```json
[
  {
    "title": "Article Title in Bengali",
    "content": "Full article content...",
    "author": "Author name",
    "date": "2024-01-15",
    "url": "https://www.prothomalo.com/...",
    "image_url": "https://www.prothomalo.com/path/to/main-image.jpg",
    "scraped_at": "2024-01-15T10:30:00"
  }
]
```

### CSV Format
Articles are saved as `YYYY-MM-DD_prothom-alo.csv` with columns:
- title
- content  
- author
- date
- url
- image_url
- scraped_at

## Project Structure

```
Scrapper/
├── news_scraper.py      # Main entry point
├── scraper.py           # Core scraper functionality
├── cli.py              # Command-line interface
├── output_utils.py     # Output utilities (JSON/CSV)
├── requirements.txt    # Dependencies
└── README.md          # This file
```

## Dependencies

- `requests`: HTTP requests
- `beautifulsoup4`: HTML parsing
- `click`: CLI framework
- `lxml`: XML/HTML parser (optional but recommended)

## Error Handling

The scraper includes:
- Retry mechanisms for failed requests
- Rate limiting to respect website policies
- Validation of scraped data
- Graceful handling of missing content
- UTF-8 encoding for Bengali text

## Extending the Scraper

To add support for new news sites:

1. Create a new scraper class in `scraper.py` following the `ProthomAloScraper` pattern
2. Add the new site option to the CLI in `cli.py`
3. Update the site selection logic in the main function

## Limitations

- Currently supports only Prothom Alo
- Depends on website structure (may break if site layout changes)
- Basic error handling (doesn't handle all edge cases)
- No support for article pagination

## Legal Notice

Please respect the website's robots.txt and terms of service. This tool is for educational and research purposes. Always check the website's scraping policies before use.

## License

This project is open source. Feel free to modify and distribute according to your needs.

## Author

Rayat Chowdhury  
Version: 1.0.0