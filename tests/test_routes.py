"""
בדיקות בסיסיות לנתיבים של האפליקציה
"""
import pytest
import sys
import os
from unittest.mock import patch, Mock

# הוספת נתיב הפרויקט ל-PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock את משתני הסביבה לפני ייבוא האפליקציה
os.environ['OPENAI_API_KEY'] = 'test-key'
os.environ['BASIC_AUTH_USERNAME'] = 'testuser'
os.environ['BASIC_AUTH_PASSWORD'] = 'testpass'

from main import app


@pytest.fixture
def client():
    """יוצר לקוח בדיקה של Flask"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_index_route_requires_auth(client):
    """בודק שהנתיב הראשי דורש אימות"""
    response = client.get('/')
    assert response.status_code == 401  # Unauthorized


def test_index_route_with_auth(client):
    """בודק שהנתיב הראשי עובד עם אימות"""
    # יצירת headers לאימות בסיסי
    from base64 import b64encode
    credentials = b64encode(b'testuser:testpass').decode('utf-8')
    headers = {'Authorization': f'Basic {credentials}'}
    
    response = client.get('/', headers=headers)
    assert response.status_code == 200
    assert b'WordPress Content Uploader' in response.data or b'wordpress' in response.data.lower()


def test_health_check_no_auth(client):
    """בודק שנתיב health check לא דורש אימות"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'
    assert 'uptime' in data
    assert 'timestamp' in data
    assert 'version' in data


def test_upload_csv_requires_auth(client):
    """בודק שהעלאת CSV דורשת אימות"""
    response = client.post('/upload_csv')
    assert response.status_code == 401


def test_download_sample_requires_auth(client):
    """בודק שהורדת קובץ לדוגמה דורשת אימות"""
    response = client.get('/download_sample_csv')
    assert response.status_code == 401 