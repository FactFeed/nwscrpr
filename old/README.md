# Bangla News Scraper

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Beautiful](https://img.shields.io/badge/CLI-Beautiful-pink.svg)](https://github.com/rayatchowdhury/BD-Newspaper-Scraper)

> A modern, beautiful CLI tool for scraping Bangladeshi news websites with style ✨

![Demo](https://img.shields.io/badge/🎬-Demo-brightgreen) *Experience the beautiful CLI interface in action*

## 🚀 Quick Start

```bash
# Clone & Install
git clone https://github.com/rayatchowdhury/BD-Newspaper-Scraper.git
cd BD-Newspaper-Scraper
pip install -r requirements.txt

# Start scraping with style!
python main.py --run --site=all --limit=5 --output=json
```

## ✨ Features

🎨 **Beautiful CLI** - Rich, colorful interface with progress indicators  
🌐 **Multi-Site** - Prothom Alo, Daily Ittefaq, and easily extensible  
⚡ **Fast & Smart** - Intelligent caching & rate limiting  
💾 **Rich Output** - JSON/CSV with complete article data  
🛡️ **Robust** - Error handling, validation, and retry mechanisms  
🔧 **Configurable** - Customizable delays, output formats, and caching

## 📋 Usage

### Basic Commands

```bash
# Scrape from all sites
python main.py --run --site=all --limit=10

# Single site with verbose output
python main.py --run --site=prothom-alo --limit=5 --verbose

# Get all available articles
python main.py --run --site=ittefaq --limit=0 --output=csv

# Short form
python main.py -r -s all -l 5 -o json
```

### Advanced Options

```bash
# Cache management
python main.py --cache-stats     # View cache info
python main.py --clear-cache     # Clear all cache

# Custom configuration
python main.py -r -s all -l 5 --delay 2.0 --output-dir ./news
```

## 📖 Python API

```python
from bangla_news_scraper import ProthomAloScraper, save_to_json

# Quick scraping
scraper = ProthomAloScraper(delay=1.0)
articles = scraper.scrape_articles(limit=10)
save_to_json(articles, 'prothom-alo', './output')

# Work with articles
for article in articles:
    print(f"📰 {article.title}")
    print(f"✍️  {article.author}")
    print(f"📅 {article.date}")
```

## 🎯 Supported Sites

| Site | Status | Articles/Day | Features |
|------|--------|--------------|----------|
| 🇧🇩 Prothom Alo | ✅ Active | ~50+ | Full content, images, metadata |
| 📰 Daily Ittefaq | ✅ Active | ~30+ | Complete article extraction |
| 🔄 More sites | 🚧 Coming | - | Easy to extend |

## 📁 Output Structure

```
output/
├── json/
│   ├── 2025-09-14_prothom-alo.json  # Structured JSON data
│   └── 2025-09-14_ittefaq.json      # Rich metadata included
└── csv/
    ├── 2025-09-14_prothom-alo.csv   # Spreadsheet format
    └── 2025-09-14_ittefaq.csv       # Easy analysis
```

## 🛠️ CLI Options

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--run` | `-r` | - | 🚀 Start scraping |
| `--site` | `-s` | `prothom-alo` | 🌐 Target site or `all` |
| `--limit` | `-l` | `5` | 📊 Articles per site |
| `--output` | `-o` | `json` | 💾 Format (`json`/`csv`) |
| `--verbose` | `-v` | - | 🔍 Detailed logging |
| `--delay` | - | `1.0` | ⏱️ Request delay (seconds) |

## 🧪 Development

```bash
# Setup development environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run tests
pytest

# Test CLI
python main.py --help
```

## 🤝 Contributing

1. 🍴 Fork the repo
2. 🌟 Create feature branch
3. ✅ Add tests
4. 📝 Update docs
5. 🚀 Submit PR

## ⚖️ Ethics & Legal

- ✅ Respects `robots.txt`
- ⏰ Default 1s delay between requests
- 🛡️ Responsible scraping practices
- 📚 Educational/research purposes

## 👨‍💻 Author

**Rayat Chowdhury** - [GitHub](https://github.com/rayatchowdhury)

---

<div align="center">

**⭐ Star this repo if you found it useful!**

[🐛 Report Bug](https://github.com/rayatchowdhury/BD-Newspaper-Scraper/issues) • [✨ Request Feature](https://github.com/rayatchowdhury/BD-Newspaper-Scraper/issues) • [📖 Documentation](https://github.com/rayatchowdhury/BD-Newspaper-Scraper)

</div>