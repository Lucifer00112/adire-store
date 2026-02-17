import os
import requests
from dotenv import load_dotenv

load_dotenv('adire-backend/.env')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

def create_bucket(bucket_name):
    print(f"Creating bucket: {bucket_name}")
    url = f"{SUPABASE_URL}/storage/v1/bucket"
    headers = {
        "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "id": bucket_name,
        "name": bucket_name,
        "public": True
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print(f"Success: Bucket '{bucket_name}' created successfully!")
        elif response.status_code == 400 and "already exists" in response.text:
            print(f"Info: Bucket '{bucket_name}' already exists.")
        else:
            print(f"Error: Failed to create bucket: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_bucket("product-image")
