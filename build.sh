#!/bin/bash
set -e

# התקנת תלויות
pip3 install -r requirements.txt pyinstaller

# ניקוי תוצרים ישנים
rm -rf build/ dist/

# בנייה
pyinstaller wp_content_app.spec

echo "הבנייה הושלמה. התוצר נמצא ב-dist/wp_content_app" 