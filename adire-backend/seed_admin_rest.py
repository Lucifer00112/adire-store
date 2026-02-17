import os
import bcrypt
import requests
from dotenv import load_dotenv

load_dotenv('adire-backend/.env')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

def seed_admin_rest():
    print(f"Seeding admin via REST: {ADMIN_EMAIL}")
    hashed_pw = bcrypt.hashpw(ADMIN_PASSWORD.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    headers = {
        "apikey": SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    # Check if admin already exists
    url_get = f"{SUPABASE_URL}/rest/v1/users?email=eq.{ADMIN_EMAIL}"
    try:
        response = requests.get(url_get, headers=headers)
        response.raise_for_status()
        existing_users = response.json()
        
        if existing_users:
            print("Admin already exists in database. Updating password...")
            user_id = existing_users[0]['id']
            url_patch = f"{SUPABASE_URL}/rest/v1/users?id=eq.{user_id}"
            data = {"password": hashed_pw, "verified": 1}
            res = requests.patch(url_patch, headers=headers, json=data)
            res.raise_for_status()
        else:
            print("Creating new admin entry...")
            url_post = f"{SUPABASE_URL}/rest/v1/users"
            data = {
                "email": ADMIN_EMAIL, 
                "password": hashed_pw, 
                "name": "Administrator", 
                "verified": 1,
                "status": "Active"
            }
            res = requests.post(url_post, headers=headers, json=data)
            res.raise_for_status()
        
        print("Success: Admin seeded successfully via REST!")
    except Exception as e:
        print(f"Error: Seeding via REST failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")

if __name__ == "__main__":
    seed_admin_rest()
