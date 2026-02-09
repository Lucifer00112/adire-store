import sqlite3
import os

db_path = 'c:/adire-store/adire-backend/adire.db'

def migrate():
    if not os.path.exists(db_path):
        print(f"DB not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        # Check if column exists
        c.execute("PRAGMA table_info(products)")
        columns = [row[1] for row in c.fetchall()]
        
        if 'gallery' not in columns:
            print("Adding gallery column to products table...")
            c.execute("ALTER TABLE products ADD COLUMN gallery TEXT DEFAULT '[]'")
            conn.commit()
            print("Migration successful.")
        else:
            print("Gallery column already exists.")
            
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
