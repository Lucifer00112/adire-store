import os
import psycopg2
from dotenv import load_dotenv

load_dotenv('adire-backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')

def verify():
    print(f"Connecting to: {DATABASE_URL.split('@')[1]}")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = cur.fetchall()
    print("Found tables:")
    for t in tables:
        print(f" - {t[0]}")
    conn.close()

if __name__ == "__main__":
    verify()
