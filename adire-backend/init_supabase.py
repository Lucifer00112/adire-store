import os
import sys
from dotenv import load_dotenv

# Add the current directory to sys.path to import app.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import init_db

if __name__ == "__main__":
    print("Initializing Supabase Tables...")
    try:
        init_db()
        print("Tables initialized successfully in Supabase Postgres!")
    except Exception as e:
        print(f"Initialization failed: {str(e)}")
