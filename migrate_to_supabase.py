import sqlite3
import os
import json
import base64
from supabase import create_client, Client

# --- CONFIGURATION ---
SUPABASE_URL = "https://fhnaialqfslxskroendg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZobmFpYWxxZnNseHNrcm9lbmRnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDgwODc4MSwiZXhwIjoyMDg2Mzg0NzgxfQ.9sCgEDPSeUxVNIDENYpHb6_5YpI2prUCokaM9Tr_FcA"
DB_PATH = "adire-backend/adire.db"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def migrate_products():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    products = c.fetchall()

    for p in products:
        print(f"Migrating product: {p['name']}...")
        
        image_url = None
        # Logic to handle base64 images
        if p['image_base64'] and p['image_base64'].startswith('data:image'):
            try:
                # Extract base64 content
                header, encoded = p['image_base64'].split(',', 1)
                file_ext = header.split(';')[0].split('/')[1]
                image_data = base64.b64decode(encoded)
                
                filename = f"{p['id']}.{file_ext}"
                path = f"products/{filename}"
                
                # Upload to Supabase Storage
                supabase.storage.from_("product-image").upload(path, image_data, {"content-type": f"image/{file_ext}"})
                image_url = supabase.storage.from_("product-image").get_public_url(path)
            except Exception as e:
                print(f"Failed to upload image for {p['name']}: {e}")

        # Insert into Supabase Postgres
        supabase.table("products").insert({
            "name": p["name"],
            "description": p["description"],
            "price": p["price"],
            "image_url": image_url,
            "category": p["category"],
            "stock": p["stock"]
        }).execute()

    conn.close()

if __name__ == "__main__":
    migrate_products()
    print("Migration completed successfully!")
