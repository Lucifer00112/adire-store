import os
import requests
from dotenv import load_dotenv

load_dotenv('adire-backend/.env')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

def list_buckets():
    print(f"Listing buckets for: {SUPABASE_URL}")
    url = f"{SUPABASE_URL}/storage/v1/bucket"
    headers = {
        "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            buckets = response.json()
            print(f"Found {len(buckets)} buckets:")
            for b in buckets:
                print(f"- {b['id']} (Public: {b['public']})")
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_buckets()
