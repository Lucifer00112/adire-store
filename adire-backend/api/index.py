from app import app

# Vercel looks for the variable named 'app' in the entry file
# Exporting it here matches the expected serverless structure
app = app
