# Bangla News Scraper# Bangla News Scraper

🎨 **Beautiful CLI** - Rich, colorful interface with progr| Site | S##| 📰## 📁 Output StructureDaily Ittefaq | ✅ Active | ~3- 📚 Educational/research purposes+ | Complete article extraction |

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)| � More sites | 🚧 Coming | - | Easy to extend |📁 Output Structureatus | Articles/Day | Feat- ✅ Resp## 👨‍💻 Author

[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[![Beautiful](https://img.shields.io/badge/CLI-Beautiful-pink.svg)](https://github.com/rayatchowdhury/BD-Newspaper-Scraper)**Rayat Chowdhury** - [GitHub](https://github.com/rayatchowdhury)s `robots.txt`

- ⏰ Default 1s delay between requests

> A modern, beautiful CLI tool for scraping Bangladeshi news websites with style ✨- 🛡️ Responsible scraping practices

- 📚 Educational/research purposes |

![Demo](https://img.shields.io/badge/🎬-Demo-brightgreen) *Experience the beautiful CLI interface in action*|------|--------|--------------|----------|

| 🇧🇩 Prothom Alo | ✅ Active | ~50+ | Full content, images, metadata |

## 🚀 Quick Start| 📰 Daily Ittefaq | ✅ Active | ~30+ | Complete article extraction |

| 🔄 More sites | 🚧 Coming | - | Easy to extend |ndicators  

```bash🌐 **Multi-Site** - Prothom Alo, Daily Ittefaq, and easily extensible  

# Clone & Install⚡ **Fast & Smart** - Intelligent caching & rate limiting  

git clone https://github.com/rayatchowdhury/BD-Newspaper-Scraper.git💾 **Rich Output** - JSON/CSV with complete article data  

cd BD-Newspaper-Scraper🛡️ **Robust** - Error handling, validation, and retry mechanisms  

pip install -r requirements.txt🔧 **Configurable** - Customizable delays, output formats, and cachingthon](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)

[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

# Start scraping with style![![Beautiful](https://img.shields.io/badge/CLI-Beautiful-pink.svg)](https://github.com/rayatchowdhury/BD-Newspaper-Scraper)

python main.py --run --site=all --limit=5 --output=json

```> A modern, beautiful CLI tool for scraping Bangladeshi news websites with style ✨



## ✨ Features![Demo](https://img.shields.io/badge/🎬-Demo-brightgreen) *Experience the beautiful CLI interface in action*



🎨 **Beautiful CLI** - Rich, colorful interface with progress indicators  ## 🚀 Quick Start

🌐 **Multi-Site** - Prothom Alo, Daily Ittefaq, and easily extensible  

⚡ **Fast & Smart** - Intelligent caching & rate limiting  ```bash

💾 **Rich Output** - JSON/CSV with complete article data  # Clone & Install

🛡️ **Robust** - Error handling, validation, and retry mechanisms  git clone https://github.com/rayatchowdhury/BD-Newspaper-Scraper.git

🔧 **Configurable** - Customizable delays, output formats, and cachingcd BD-Newspaper-Scraper

pip install -r requirements.txt

## 📋 Usage

# Start scraping with style!

### Basic Commandspython main.py --run --site=all --limit=5 --output=json

```bash```

# Scrape from all sites

python main.py --run --site=all --limit=10## ✨ Features



# Single site with verbose output  🎨 **Beautiful CLI** - Rich, colorful interface with progress indicators  

python main.py --run --site=prothom-alo --limit=5 --verbose🌐 **Multi-Site** - Prothom Alo, Daily Ittefaq, and easily extensible  

⚡ **Fast & Smart** - Intelligent caching & rate limiting  

# Get all available articles� **Rich Output** - JSON/CSV with complete article data  

python main.py --run --site=ittefaq --limit=0 --output=csv🛡️ **Robust** - Error handling, validation, and retry mechanisms  

🔧 **Configurable** - Customizable delays, output formats, and caching

# Short form

python main.py -r -s all -l 5 -o json## � Usage

```

### Basic Commands

### Advanced Options```bash

```bash# Scrape from all sites

# Cache managementpython main.py --run --site=all --limit=10

python main.py --cache-stats     # View cache info

python main.py --clear-cache     # Clear all cache# Single site with verbose output  

python main.py --run --site=prothom-alo --limit=5 --verbose

# Custom configuration

python main.py -r -s all -l 5 --delay 2.0 --output-dir ./news# Get all available articles

```python main.py --run --site=ittefaq --limit=0 --output=csv



## 📖 Python API# Short form

python main.py -r -s all -l 5 -o json

```python```

from bangla_news_scraper import ProthomAloScraper, save_to_json

### Advanced Options

# Quick scraping```bash

scraper = ProthomAloScraper(delay=1.0)# Cache management

articles = scraper.scrape_articles(limit=10)python main.py --cache-stats     # View cache info

save_to_json(articles, 'prothom-alo', './output')python main.py --clear-cache     # Clear all cache



# Work with articles# Custom configuration

for article in articles:python main.py -r -s all -l 5 --delay 2.0 --output-dir ./news

    print(f"📰 {article.title}")```

    print(f"✍️  {article.author}")

    print(f"📅 {article.date}")## � Usage

```

```python

## 🎯 Supported Sitesfrom bangla_news_scraper import ProthomAloScraper, save_to_json



| Site | Status | Articles/Day | Features |# Quick scraping

|------|--------|--------------|----------|scraper = ProthomAloScraper(delay=1.0)

| 🇧🇩 Prothom Alo | ✅ Active | ~50+ | Full content, images, metadata |articles = scraper.scrape_articles(limit=10)

| 📰 Daily Ittefaq | ✅ Active | ~30+ | Complete article extraction |save_to_json(articles, 'prothom-alo', './output')

| 🔄 More sites | 🚧 Coming | - | Easy to extend |

# Work with articles

## 📁 Output Structurefor article in articles:

    print(f"📰 {article.title}")

```    print(f"✍️  {article.author}")

output/    print(f"📅 {article.date}")

├── json/```

│   ├── 2025-09-14_prothom-alo.json  # Structured JSON data

│   └── 2025-09-14_ittefaq.json      # Rich metadata included## 🎯 Supported Sites

└── csv/

    ├── 2025-09-14_prothom-alo.csv   # Spreadsheet format| Site | Status | Articles/Day | Features |

    └── 2025-09-14_ittefaq.csv       # Easy analysis|------|--------|--------------|----------|

```| 🇧🇩 Prothom Alo | ✅ Active | ~50+ | Full content, images, metadata |

| � Daily Ittefaq | ✅ Active | ~30+ | Complete article extraction |

## 🛠️ CLI Options| 🔄 More sites | � Coming | - | Easy to extend |



| Flag | Short | Default | Description |## � Output Structure

|------|-------|---------|-------------|

| `--run` | `-r` | - | 🚀 Start scraping |```

| `--site` | `-s` | `prothom-alo` | 🌐 Target site or `all` |output/

| `--limit` | `-l` | `5` | 📊 Articles per site |├── json/

| `--output` | `-o` | `json` | 💾 Format (`json`/`csv`) |│   ├── 2025-09-14_prothom-alo.json  # Structured JSON data

| `--verbose` | `-v` | - | 🔍 Detailed logging |│   └── 2025-09-14_ittefaq.json      # Rich metadata included

| `--delay` | - | `1.0` | ⏱️ Request delay (seconds) |└── csv/

    ├── 2025-09-14_prothom-alo.csv   # Spreadsheet format

## 🧪 Development    └── 2025-09-14_ittefaq.csv       # Easy analysis

```

```bash

# Setup development environment## 🛠️ CLI Options

python -m venv venv

source venv/bin/activate  # Windows: venv\Scripts\activate| Flag | Short | Default | Description |

pip install -r requirements.txt|------|-------|---------|-------------|

| `--run` | `-r` | - | 🚀 Start scraping |

# Run tests| `--site` | `-s` | `prothom-alo` | 🌐 Target site or `all` |

pytest| `--limit` | `-l` | `5` | 📊 Articles per site |

| `--output` | `-o` | `json` | 💾 Format (`json`/`csv`) |

# Test CLI| `--verbose` | `-v` | - | 🔍 Detailed logging |

python main.py --help| `--delay` | - | `1.0` | ⏱️ Request delay (seconds) |

```

## 🧪 Development

## 🤝 Contributing

```bash

1. 🍴 Fork the repo# Setup development environment

2. 🌟 Create feature branchpython -m venv venv

3. ✅ Add testssource venv/bin/activate  # Windows: venv\Scripts\activate

4. 📝 Update docspip install -r requirements.txt

5. 🚀 Submit PR

# Run tests

## ⚖️ Ethics & Legalpytest



- ✅ Respects `robots.txt`# Test CLI

- ⏰ Default 1s delay between requestspython main.py --help

- 🛡️ Responsible scraping practices```

- 📚 Educational/research purposes

## 🤝 Contributing

## 👨‍💻 Author

1. 🍴 Fork the repo

**Rayat Chowdhury** - [GitHub](https://github.com/rayatchowdhury)2. 🌟 Create feature branch

3. ✅ Add tests

---4. 📝 Update docs

5. 🚀 Submit PR

<div align="center">

## ⚖️ Ethics & Legal

**⭐ Star this repo if you found it useful!**

- ✅ Respects `robots.txt`

[🐛 Report Bug](https://github.com/rayatchowdhury/BD-Newspaper-Scraper/issues) • [✨ Request Feature](https://github.com/rayatchowdhury/BD-Newspaper-Scraper/issues) • [📖 Documentation](https://github.com/rayatchowdhury/BD-Newspaper-Scraper)- ⏰ Default 1s delay between requests

- 🛡️ Responsible scraping practices

</div>- � Educational/research purposes

## �‍💻 Author

**Rayat Chowdhury** - [GitHub](https://github.com/rayatchowdhury)

---

<div align="center">

**⭐ Star this repo if you found it useful!**

[🐛 Report Bug](https://github.com/rayatchowdhury/BD-Newspaper-Scraper/issues) • [✨ Request Feature](https://github.com/rayatchowdhury/BD-Newspaper-Scraper/issues) • [📖 Documentation](https://github.com/rayatchowdhury/BD-Newspaper-Scraper)

</div>

</div>