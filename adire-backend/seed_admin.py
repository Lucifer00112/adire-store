import os
import bcrypt
import psycopg2
from dotenv import load_dotenv

load_dotenv('adire-backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

def seed_admin():
    print(f"Seeding admin: {ADMIN_EMAIL}")
    hashed_pw = bcrypt.hashpw(ADMIN_PASSWORD.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Check if admin already exists
    cur.execute("SELECT email FROM users WHERE email = %s", (ADMIN_EMAIL,))
    if cur.fetchone():
        print("Admin already exists in database. Updating password...")
        cur.execute("UPDATE users SET password = %s, verified = 1 WHERE email = %s", (hashed_pw, ADMIN_EMAIL))
    else:
        print("Creating new admin entry...")
        cur.execute(
            "INSERT INTO users (email, password, name, verified) VALUES (%s, %s, %s, %s)",
            (ADMIN_EMAIL, hashed_pw, "Administrator", 1)
        )
    
    conn.commit()
    conn.close()
    print("✅ Admin seeded successfully!")

if __name__ == "__main__":
    seed_admin()
