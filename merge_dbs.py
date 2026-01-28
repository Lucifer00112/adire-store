import sqlite3
import os

root_db = r'c:\adire-store\adire.db'
backend_db = r'c:\adire-store\adire-backend\adire.db'

def merge_dbs():
    if not os.path.exists(root_db):
        print("Root DB not found.")
        return

    conn_r = sqlite3.connect(root_db)
    conn_b = sqlite3.connect(backend_db)
    conn_r.row_factory = sqlite3.Row
    conn_b.row_factory = sqlite3.Row
    
    cursor_r = conn_r.cursor()
    cursor_b = conn_b.cursor()

    tables = ['users', 'products', 'orders', 'reviews', 'admin_logs', 'settings']
    
    for table in tables:
        try:
            cursor_r.execute(f"SELECT * FROM {table}")
            rows = cursor_r.fetchall()
            for row in rows:
                cols = [c for c in row.keys() if c != 'id']
                placeholders = ', '.join(['?'] * len(cols))
                col_names = ', '.join(cols)
                
                if table == 'users':
                    cursor_b.execute("SELECT email FROM users WHERE email = ?", (row['email'],))
                    if cursor_b.fetchone(): continue
                elif table == 'settings':
                    cursor_b.execute("SELECT key FROM settings WHERE key = ?", (row['key'],))
                    if cursor_b.fetchone(): continue
                
                query = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"
                values = [row[c] for c in cols]
                cursor_b.execute(query, tuple(values))
            print(f"Merged {len(rows)} rows from {table}")
        except Exception as e:
            print(f"Error merging {table}: {e}")

    conn_b.commit()
    conn_r.close()
    conn_b.close()
    print("Merge complete.")

if __name__ == "__main__":
    merge_dbs()
