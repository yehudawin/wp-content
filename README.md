# WordPress Content Automation System

מערכת אוטומטית ליצירת והעלאת תוכן ל-WordPress עם יצירת טקסט ותמונות באמצעות AI.

## תכונות עיקריות

- יצירת מאמרים אוטומטית באמצעות GPT-4
- יצירת תמונות באמצעות DALL-E 3
- העלאה אוטומטית ל-WordPress דרך REST API
- שליחת דוחות במייל עם קישורים לפוסטים שפורסמו
- ממשק מוגן עם Basic Authentication
- תמיכה בהפעלה עם Docker

## דרישות מקדימות

- Python 3.10+
- חשבון OpenAI עם API Key
- אתר WordPress עם REST API מופעל
- חשבון Gmail עם App Password (לשליחת דוחות)

## התקנה והפעלה

### אפשרות 1: הפעלה עם Python

1. **שכפל את הפרויקט:**
   ```bash
   git clone [repository-url]
   cd wp-content
   ```

2. **צור סביבה וירטואלית (מומלץ):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # או
   venv\Scripts\activate  # Windows
   ```

3. **התקן תלויות:**
   ```bash
   pip install -r requirements.txt
   ```

4. **הגדר משתני סביבה:**
   - העתק את `.env.example` ל-`.env`
   - ערוך את הקובץ והזן את הערכים המתאימים

5. **הפעל את האפליקציה:**
   ```bash
   # למצב פיתוח
   python main.py
   
   # למצב production
   gunicorn --bind 0.0.0.0:5001 --workers 1 --timeout 300 main:app
   ```

### אפשרות 2: הפעלה עם Docker

1. **בנה את ה-image:**
   ```bash
   docker build -t wp-automation .
   ```

2. **הפעל את הקונטיינר:**
   ```bash
   docker run -d \
     --name wp-automation \
     -p 5001:5001 \
     --env-file .env \
     -v $(pwd)/uploads:/app/uploads \
     -v $(pwd)/images:/app/images \
     -v $(pwd)/app.log:/app/app.log \
     wp-automation
   ```

### אפשרות 3: Docker Compose (מומלץ)

1. **צור קובץ `docker-compose.yml`:**
   ```yaml
   version: '3.8'
   services:
     app:
       build: .
       ports:
         - "5001:5001"
       env_file:
         - .env
       volumes:
         - ./uploads:/app/uploads
         - ./images:/app/images
         - ./app.log:/app/app.log
       restart: unless-stopped
   ```

2. **הפעל:**
   ```bash
   docker-compose up -d
   ```

## משתני סביבה

צור קובץ `.env` על בסיס `.env.example` עם הערכים הבאים:

### הגדרות Flask
- `FLASK_SECRET_KEY` - מפתח סודי לאבטחת הסשנים (חובה לשנות בפרודקשן!)
- `FLASK_ENV` - סביבת הרצה: `development` או `production`
- `FLASK_DEBUG` - מצב דיבאג: `true` או `false`

### OpenAI API
- `OPENAI_API_KEY` - המפתח שלך מ-OpenAI

### הגדרות אימייל (Gmail)
- `EMAIL_HOST_USER` - כתובת Gmail שלך
- `APP_PASSWORD` - סיסמת אפליקציה מ-Gmail (לא הסיסמה הרגילה!)
- `EMAIL_RECEIVER` - כתובת לקבלת הדוחות

### Basic Authentication
- `BASIC_AUTH_USERNAME` - שם משתמש לגישה לממשק
- `BASIC_AUTH_PASSWORD` - סיסמה לגישה לממשק

## שימוש במערכת

1. **גש לממשק:** `http://localhost:5001`
2. **הזן את שם המשתמש והסיסמה** שהגדרת ב-`.env`
3. **הורד את קובץ ה-CSV לדוגמה** מהממשק
4. **ערוך את הקובץ** עם הנתונים שלך:
   - `Title` - כותרת המאמר
   - `Domain` - כתובת אתר ה-WordPress (כולל https://)
   - `User` - שם משתמש ב-WordPress
   - `Pass` - סיסמת Application Password מ-WordPress
   - `CategoryID` - מזהה הקטגוריה ב-WordPress
   - `Anchor` - טקסט העוגן לקישור
   - `Link` - כתובת הקישור להטמעה במאמר
5. **העלה את הקובץ** דרך הממשק
6. **המתן לסיום העיבוד** - הדוח יישלח במייל

## בדיקת תקינות

בדוק את מצב המערכת ב: `http://localhost:5001/health`

## לוגים

הלוגים נשמרים בקובץ `app.log` ומוצגים גם בקונסול.

## אבטחה

- **החלף את `FLASK_SECRET_KEY`** בערך חזק וייחודי
- **השתמש בסיסמאות חזקות** ל-Basic Auth
- **אל תשתף את קובץ `.env`** או תעלה אותו ל-Git
- מומלץ להריץ מאחורי reverse proxy (nginx) עם HTTPS בפרודקשן

## פתרון בעיות

### בעיה: שגיאת חיבור ל-WordPress
- ודא שה-REST API מופעל באתר
- בדוק שהכתובת נכונה וכוללת https://
- ודא שה-Application Password נכון

### בעיה: שגיאה בשליחת מייל
- ודא שיצרת App Password ב-Gmail (לא סיסמה רגילה)
- בדוק שהאימות הדו-שלבי מופעל בחשבון Gmail

### בעיה: תמונות לא נמחקות
- בדוק הרשאות כתיבה בתיקיית `images/`
- ודא שהתהליך הסתיים בהצלחה

## הרצת בדיקות

המערכת כוללת חבילת בדיקות אוטומטיות באמצעות pytest.

### התקנת תלויות הבדיקה:
```bash
pip install -r requirements.txt
```

### הרצת כל הבדיקות:
```bash
pytest
```

### הרצת בדיקות ספציפיות:
```bash
# בדיקות נתיבים בלבד
pytest tests/test_routes.py

# בדיקות עיבוד CSV בלבד
pytest tests/test_csv_processing.py
```

### הרצה עם פירוט:
```bash
pytest -v
```

### הרצה עם כיסוי קוד:
```bash
pytest --cov=main --cov-report=html
```

הבדיקות כוללות:
- בדיקת נתיבי API והרשאות
- בדיקת עיבוד קבצי CSV
- בדיקת תמיכה בעברית
- בדיקות יחידה ללא תלות בשירותים חיצוניים

## רישיון

[הוסף רישיון לפי הצורך] 