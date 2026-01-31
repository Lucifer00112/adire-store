import sys
import os

# Add the parent directory to sys.path so Vercel can find 'app.py'
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app import app

# Vercel looks for the variable named 'app' in the entry file
app = app
