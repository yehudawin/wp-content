"""
בדיקות לעיבוד קבצי CSV
"""
import pytest
import pandas as pd
import os
import sys
from unittest.mock import patch, Mock, MagicMock
import tempfile

# הוספת נתיב הפרויקט ל-PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock את משתני הסביבה
os.environ['OPENAI_API_KEY'] = 'test-key'

from main import allowed_file, process_csv_data


def test_allowed_file():
    """בודק פונקציית בדיקת סיומת קבצים"""
    assert allowed_file('test.csv') == True
    assert allowed_file('test.CSV') == True
    assert allowed_file('test.txt') == False
    assert allowed_file('test.xlsx') == False
    assert allowed_file('test') == False


def test_sample_csv_structure():
    """בודק שקובץ ה-CSV לדוגמה קיים ומכיל את כל העמודות הנדרשות"""
    sample_path = os.path.join('static', 'sample.csv')
    assert os.path.exists(sample_path), "קובץ sample.csv לא נמצא"
    
    # טוען את הקובץ ובודק את העמודות
    df = pd.read_csv(sample_path)
    required_columns = ['Title', 'Domain', 'User', 'Pass', 'CategoryID', 'Anchor', 'Link']
    
    for col in required_columns:
        assert col in df.columns, f"עמודה חסרה: {col}"


def test_sample_csv_readable():
    """בודק שניתן לקרוא את קובץ ה-CSV לדוגמה ללא שגיאות"""
    sample_path = os.path.join('static', 'sample.csv')
    try:
        df = pd.read_csv(sample_path, encoding='utf-8-sig')
        # בודק שהקובץ נטען בהצלחה
        assert isinstance(df, pd.DataFrame)
    except Exception as e:
        pytest.fail(f"לא ניתן לקרוא את קובץ ה-CSV: {str(e)}")


@patch('main.write_text_with_gpt')
@patch('main.humanize_text_with_gpt')
@patch('main.generate_image_prompt_with_gpt')
@patch('main.generate_image_with_dalle')
@patch('main.upload_to_wordpress')
@patch('main.upload_image_to_wordpress')
@patch('main.send_report_email')
def test_process_csv_data_mock(mock_send_email, mock_upload_img, mock_upload_wp, 
                              mock_dalle, mock_img_prompt, mock_humanize, mock_write):
    """בודק עיבוד CSV עם mocks - ללא קריאות אמיתיות ל-API"""
    # הגדרת ה-mocks
    mock_write.return_value = "Generated text"
    mock_humanize.return_value = "Humanized text"
    mock_img_prompt.return_value = "Image prompt"
    mock_dalle.return_value = "http://fake-image-url.com/image.png"
    mock_upload_img.return_value = 123  # Fake image ID
    mock_upload_wp.return_value = "http://example.com/post-url"
    
    # יוצר קובץ CSV זמני לבדיקה
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8-sig') as f:
        f.write("Title,Domain,User,Pass,CategoryID,Anchor,Link\n")
        f.write("Test Post,http://example.com,testuser,testpass,1,Test Anchor,http://test.com\n")
        temp_path = f.name
    
    try:
        # מריץ את הפונקציה
        result = process_csv_data(temp_path)
        
        # בודק שהפונקציה הצליחה
        assert "Successfully read CSV" in result
        assert "Processing title: Test Post" in result
        
        # בודק שה-mocks נקראו
        mock_write.assert_called_once()
        mock_humanize.assert_called_once()
        mock_img_prompt.assert_called_once()
        
    finally:
        # מנקה את הקובץ הזמני
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_csv_with_hebrew():
    """בודק שניתן לקרוא CSV עם תוכן בעברית"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8-sig') as f:
        f.write("Title,Domain,User,Pass,CategoryID,Anchor,Link\n")
        f.write("כותרת בעברית,http://example.com,user,pass,1,עוגן בעברית,http://test.com\n")
        temp_path = f.name
    
    try:
        df = pd.read_csv(temp_path, encoding='utf-8-sig')
        assert df.iloc[0]['Title'] == 'כותרת בעברית'
        assert df.iloc[0]['Anchor'] == 'עוגן בעברית'
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path) 