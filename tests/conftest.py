"""
קובץ הגדרות משותפות לבדיקות pytest
"""
import os
import sys
import pytest
from unittest.mock import patch

# הוספת נתיב הפרויקט ל-PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# הגדרת משתני סביבה בסיסיים לבדיקות
os.environ.setdefault('OPENAI_API_KEY', 'test-key')
os.environ.setdefault('BASIC_AUTH_USERNAME', 'testuser')
os.environ.setdefault('BASIC_AUTH_PASSWORD', 'testpass')
os.environ.setdefault('FLASK_SECRET_KEY', 'test-secret-key')
os.environ.setdefault('EMAIL_HOST_USER', 'test@gmail.com')
os.environ.setdefault('APP_PASSWORD', 'test-app-password')
os.environ.setdefault('EMAIL_RECEIVER', 'receiver@gmail.com')


@pytest.fixture(scope='session')
def app():
    """יוצר אינסטנס של האפליקציה לבדיקות"""
    from main import app as flask_app
    flask_app.config['TESTING'] = True
    return flask_app


@pytest.fixture
def mock_openai():
    """Mock לקריאות OpenAI"""
    with patch('main.client') as mock_client:
        # Mock GPT responses
        mock_client.chat.completions.create.return_value.choices = [
            type('obj', (object,), {'message': type('obj', (object,), {'content': 'Mocked GPT response'})})()
        ]
        
        # Mock DALL-E responses
        mock_client.images.generate.return_value.data = [
            type('obj', (object,), {'url': 'http://mocked-image-url.com/image.png'})()
        ]
        
        yield mock_client 