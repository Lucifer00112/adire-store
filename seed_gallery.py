import sqlite3
import json

db_path = 'c:/adire-store/adire-backend/adire.db'

def seed_gallery():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Get products with mannequin images
    c.execute("SELECT id, image_base64 FROM products WHERE id BETWEEN 7 AND 12")
    rows = c.fetchall()
    
    for row_id, img in rows:
        # Create a gallery with one style (the current mannequin image)
        gallery = json.dumps([img])
        c.execute("UPDATE products SET gallery = ? WHERE id = ?", (gallery, row_id))
    
    conn.commit()
    conn.close()
    print(f"Successfully seeded gallery for {len(rows)} products.")

if __name__ == "__main__":
    seed_gallery()
