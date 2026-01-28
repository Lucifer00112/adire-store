import sqlite3
import os

def migrate():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, 'adire-backend', 'adire.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Add columns to 'users'
    users_cols = [
        ('phone', 'TEXT'),
        ('status', "TEXT DEFAULT 'Active'"),
        ('admin_notes', 'TEXT'),
        ('last_login', 'DATETIME')
    ]
    
    for col_name, col_type in users_cols:
        try:
            c.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
            print(f"Added column {col_name} to users table.")
        except sqlite3.OperationalError:
            print(f"Column {col_name} already exists in users table.")

    # Add columns to 'orders'
    orders_cols = [
        ('payment_status', "TEXT DEFAULT 'Unpaid'"),
        ('delivery_status', "TEXT DEFAULT 'Pending'"),
        ('delivery_method', 'TEXT'),
        ('tracking_number', 'TEXT'),
        ('estimated_delivery', 'DATETIME'),
        ('timeline', 'TEXT'),
        ('refunded_amount', 'INTEGER DEFAULT 0')
    ]

    for col_name, col_type in orders_cols:
        try:
            c.execute(f"ALTER TABLE orders ADD COLUMN {col_name} {col_type}")
            print(f"Added column {col_name} to orders table.")
        except sqlite3.OperationalError:
            print(f"Column {col_name} already exists in orders table.")

    # Add admin_logs and settings tables if they don't exist (just in case)
    c.execute('''CREATE TABLE IF NOT EXISTS admin_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_email TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )''')

    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
