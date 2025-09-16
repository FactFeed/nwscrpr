"""
Test configuration and fixtures
"""

import pytest
import tempfile
import shutil
from pathlib import Path

# Test data
SAMPLE_ARTICLE_DATA = {
    'title': 'Sample Article Title',
    'content': 'This is a sample article content with enough text to pass validation.',
    'url': 'https://www.example.com/article/sample',
    'author': 'Test Author',
    'date': '2024-01-15',
    'image_url': 'https://www.example.com/image.jpg',
    'site_name': 'Test Site'
}

SAMPLE_HTML = """
<html>
<head>
    <title>Sample Article - Test Site</title>
    <meta property="og:image" content="https://example.com/image.jpg">
</head>
<body>
    <h1>Sample Article Title</h1>
    <div class="author">Test Author</div>
    <div class="date">2024-01-15</div>
    <div class="content">
        <p>This is the first paragraph of the article.</p>
        <p>This is the second paragraph with more content.</p>
    </div>
</body>
</html>
"""


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)