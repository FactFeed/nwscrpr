"""
Tests for Article model
"""

import pytest
from datetime import datetime
from bangla_news_scraper.models import Article, ScrapingResult
from .conftest import SAMPLE_ARTICLE_DATA


class TestArticle:
    """Test Article model"""
    
    def test_article_creation(self):
        """Test creating an article with valid data"""
        article = Article(**SAMPLE_ARTICLE_DATA)
        
        assert article.title == SAMPLE_ARTICLE_DATA['title']
        assert article.content == SAMPLE_ARTICLE_DATA['content']
        assert article.url == SAMPLE_ARTICLE_DATA['url']
        assert article.author == SAMPLE_ARTICLE_DATA['author']
        assert article.date == SAMPLE_ARTICLE_DATA['date']
        assert article.image_url == SAMPLE_ARTICLE_DATA['image_url']
        assert article.site_name == SAMPLE_ARTICLE_DATA['site_name']
        assert article.scraped_at is not None
    
    def test_article_validation_valid(self):
        """Test validation with valid article data"""
        article = Article(**SAMPLE_ARTICLE_DATA)
        assert article.is_valid() is True
    
    def test_article_validation_invalid_title(self):
        """Test validation with invalid title"""
        data = SAMPLE_ARTICLE_DATA.copy()
        data['title'] = 'abc'  # Too short
        article = Article(**data)
        assert article.is_valid() is False
    
    def test_article_validation_invalid_content(self):
        """Test validation with invalid content"""
        data = SAMPLE_ARTICLE_DATA.copy()
        data['content'] = 'Short content'  # Too short
        article = Article(**data)
        assert article.is_valid() is False
    
    def test_article_validation_invalid_url(self):
        """Test validation with invalid URL"""
        data = SAMPLE_ARTICLE_DATA.copy()
        data['url'] = 'not-a-valid-url'
        article = Article(**data)
        assert article.is_valid() is False
    
    def test_article_to_dict(self):
        """Test converting article to dictionary"""
        article = Article(**SAMPLE_ARTICLE_DATA)
        article_dict = article.to_dict()
        
        assert isinstance(article_dict, dict)
        assert article_dict['title'] == SAMPLE_ARTICLE_DATA['title']
        assert article_dict['content'] == SAMPLE_ARTICLE_DATA['content']
        assert 'scraped_at' in article_dict
    
    def test_article_from_dict(self):
        """Test creating article from dictionary"""
        article = Article.from_dict(SAMPLE_ARTICLE_DATA)
        
        assert article.title == SAMPLE_ARTICLE_DATA['title']
        assert article.content == SAMPLE_ARTICLE_DATA['content']
        assert article.url == SAMPLE_ARTICLE_DATA['url']
    
    def test_article_previews(self):
        """Test title and content preview methods"""
        article = Article(**SAMPLE_ARTICLE_DATA)
        
        title_preview = article.get_title_preview(20)
        content_preview = article.get_content_preview(30)
        
        assert len(title_preview) <= 25  # Including "..."
        assert len(content_preview) <= 35  # Including "..."
        assert isinstance(title_preview, str)
        assert isinstance(content_preview, str)


class TestScrapingResult:
    """Test ScrapingResult model"""
    
    def test_scraping_result_creation(self):
        """Test creating a scraping result"""
        articles = [Article(**SAMPLE_ARTICLE_DATA)]
        result = ScrapingResult(
            articles=articles,
            site_name='test-site',
            total_requested=5,
            total_found=3,
            total_valid=1,
            scraped_at=datetime.now().isoformat()
        )
        
        assert len(result.articles) == 1
        assert result.site_name == 'test-site'
        assert result.total_requested == 5
        assert result.total_found == 3
        assert result.total_valid == 1
        assert result.scraped_at is not None
    
    def test_success_rate_calculation(self):
        """Test success rate calculation"""
        articles = [Article(**SAMPLE_ARTICLE_DATA)]
        result = ScrapingResult(
            articles=articles,
            site_name='test-site',
            total_requested=5,
            total_found=4,
            total_valid=2,
            scraped_at=datetime.now().isoformat()
        )
        
        success_rate = result.get_success_rate()
        assert success_rate == 50.0  # 2/4 * 100
    
    def test_success_rate_zero_found(self):
        """Test success rate with zero found articles"""
        result = ScrapingResult(
            articles=[],
            site_name='test-site',
            total_requested=5,
            total_found=0,
            total_valid=0,
            scraped_at=datetime.now().isoformat()
        )
        
        success_rate = result.get_success_rate()
        assert success_rate == 0.0
    
    def test_to_dict(self):
        """Test converting scraping result to dictionary"""
        articles = [Article(**SAMPLE_ARTICLE_DATA)]
        result = ScrapingResult(
            articles=articles,
            site_name='test-site',
            total_requested=5,
            total_found=3,
            total_valid=1,
            scraped_at=datetime.now().isoformat()
        )
        
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert 'articles' in result_dict
        assert 'success_rate' in result_dict
        assert len(result_dict['articles']) == 1
        assert result_dict['site_name'] == 'test-site'