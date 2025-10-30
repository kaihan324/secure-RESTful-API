#!/usr/bin/env bash
set -e

# 1. ایجاد و فعال کردن محیط مجازی
python3 -m venv venv
source venv/bin/activate

# 2. به‌روز‌رسانی pip و نصب وابستگی‌ها
pip install --upgrade pip
pip install -r requirements.txt

# 3. نصب sqlite3 CLI (روی اوبونتو/دبیان)
if ! command -v sqlite3 &> /dev/null; then
  echo "Installing sqlite3..."
  sudo apt-get update
  sudo apt-get install -y sqlite3 libsqlite3-dev
fi

echo "✅ Setup complete. برای اجرا:"
echo "   source venv/bin/activate"
echo "   python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8001"

