"""
Setup script for Bangla News Scraper
"""

from setuptools import setup, find_packages
import os

# Read the README file
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open(os.path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='bangla-news-scraper',
    version='1.1.0',
    description='A Python package for scraping Bangladeshi news websites',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Rayat Chowdhury',
    author_email='rayat@example.com',
    url='https://github.com/rayatchowdhury/BD-Newspaper-Scraper',
    
    # Package information
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.8',
    
    # Dependencies
    install_requires=requirements,
    
    # Entry points for CLI
    entry_points={
        'console_scripts': [
            'bangla-news-scraper=bangla_news_scraper.cli:main',
            'bns=bangla_news_scraper.cli:main',
        ],
    },
    
    # Classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup :: HTML',
    ],
    
    # Keywords
    keywords='news scraping bangladesh bangla web-scraping journalism',
    
    # Project URLs
    project_urls={
        'Bug Reports': 'https://github.com/rayatchowdhury/BD-Newspaper-Scraper/issues',
        'Source': 'https://github.com/rayatchowdhury/BD-Newspaper-Scraper',
        'Documentation': 'https://github.com/rayatchowdhury/BD-Newspaper-Scraper/blob/main/README.md',
    },
    
    # Include additional files
    include_package_data=True,
    zip_safe=False,
    
    # Development dependencies
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'black>=21.0',
            'flake8>=3.8',
            'mypy>=0.900',
        ],
        'test': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'responses>=0.20.0',
        ],
    },
)