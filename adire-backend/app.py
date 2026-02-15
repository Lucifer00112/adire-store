from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import sqlite3
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
import bcrypt
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
import base64
import json

load_dotenv()

app = Flask(__name__, static_folder='..', static_url_path='')
CORS(app)

ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', '').strip()
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', '').strip()
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT') or 587)

DATABASE_URL = os.getenv('DATABASE_URL')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "adire.db")

def get_db_connection():
    if DATABASE_URL:
        if not PSYCOPG2_AVAILABLE:
            raise Exception("Postgres support (psycopg2) is not installed. Please run 'pip install psycopg2-binary'")
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        conn.autocommit = True
        return conn
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def q(query):
    return query.replace('?', '%s') if DATABASE_URL else query

def log_admin_action(admin_email, action, details=None):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(q("INSERT INTO admin_logs (admin_email, action, details) VALUES (?, ?, ?)"),
              (admin_email, action, details))
    conn.commit()
    conn.close()

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    if not DATABASE_URL:
        # SQLite
        tables = [
            '''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT,
                phone TEXT,
                status TEXT DEFAULT 'Active',
                admin_notes TEXT,
                verified INTEGER DEFAULT 0,
                verification_code TEXT,
                code_expiry DATETIME,
                last_login DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price INTEGER NOT NULL,
                image_base64 TEXT,
                gallery TEXT,
                category TEXT,
                stock INTEGER DEFAULT 10,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL,
                items TEXT NOT NULL,
                total INTEGER NOT NULL,
                address TEXT,
                phone TEXT,
                status TEXT DEFAULT 'Pending',
                payment_status TEXT DEFAULT 'Unpaid',
                delivery_status TEXT DEFAULT 'Pending',
                delivery_method TEXT,
                tracking_number TEXT,
                estimated_delivery DATETIME,
                timeline TEXT,
                refunded_amount INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                user_name TEXT,
                rating INTEGER,
                comment TEXT,
                status TEXT DEFAULT 'Pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS admin_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_email TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )'''
        ]
    else:
        # Postgres
        tables = [
            '''CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT,
                phone TEXT,
                status TEXT DEFAULT 'Active',
                admin_notes TEXT,
                verified INTEGER DEFAULT 0,
                verification_code TEXT,
                code_expiry TIMESTAMP,
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                price INTEGER NOT NULL,
                image_base64 TEXT,
                category TEXT,
                stock INTEGER DEFAULT 10,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                user_email TEXT NOT NULL,
                items TEXT NOT NULL,
                total INTEGER NOT NULL,
                address TEXT,
                phone TEXT,
                status TEXT DEFAULT 'Pending',
                payment_status TEXT DEFAULT 'Unpaid',
                delivery_status TEXT DEFAULT 'Pending',
                delivery_method TEXT,
                tracking_number TEXT,
                estimated_delivery TIMESTAMP,
                timeline TEXT,
                refunded_amount INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS reviews (
                id SERIAL PRIMARY KEY,
                product_id INTEGER,
                user_name TEXT,
                rating INTEGER,
                comment TEXT,
                status TEXT DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS admin_logs (
                id SERIAL PRIMARY KEY,
                admin_email TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )'''
        ]

    for table in tables:
        c.execute(table)
    
    # Database initialized
    conn.commit()
    conn.close()

init_db()

# Database Migration: Add address column to users if missing
def migrate_db():
    conn = get_db_connection()
    c = conn.cursor()
    try:
        if not DATABASE_URL:
            # SQLite
            c.execute("ALTER TABLE users ADD COLUMN address TEXT")
        else:
            # Postgres
            c.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS address TEXT")
        conn.commit()
        print("Migration: Added address column to users")
    except Exception as e:
        # Column might already exist
        pass
    conn.close()

migrate_db()

def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
        server.quit()
        print(f"Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"Email failed: {str(e)}")
        return False

@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/healthz')
def healthz():
    return "OK"

# Catch-all route to serve static files or index.html for unknown routes (SPA routing)
@app.errorhandler(404)
def not_found(e):
    # If the user requested an image or something we don't have, return 404
    if request.path.startswith('/api'):
        return jsonify({"error": "Not found"}), 404
    return app.send_static_file('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    conn = get_db_connection()
    c = conn.cursor()
    c.execute(q("SELECT * FROM users WHERE email = ?"), (email,))
    if c.fetchone():
        conn.close()
        return jsonify({"error": "Email already exists"}), 400

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    if DATABASE_URL: hashed = hashed.decode('utf-8')

    verification_code = ''.join(random.choices(string.digits, k=6))
    code_expiry = (datetime.now() + timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S')

    c.execute(q("INSERT INTO users (email, password, name, verification_code, code_expiry) VALUES (?, ?, ?, ?, ?)"),
              (email, hashed, name, verification_code, code_expiry))
    conn.commit()
    conn.close()

    subject = "Adire Boutique - Verify Your Email"
    body = f"""
    Hello {name},

    Welcome to Adire Boutique!

    Your verification code is: {verification_code}

    Enter this code on the site to activate your account.
    This code expires in 15 minutes.

    If you didn't sign up, ignore this email.

    Thank you!
    Adire Team
    """
    email_sent = send_email(email, subject, body)

    if email_sent:
        return jsonify({"message": "Registration successful. Check your email for verification code."}), 201
    else:
        return jsonify({"message": "Registered, but email failed to send. Code: " + verification_code}), 201

@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()
    email = data.get('email')
    code = data.get('code')

    if not email or not code:
        return jsonify({"error": "Email and code required"}), 400

    conn = get_db_connection()
    c = conn.cursor()
    # Postgres uses interval for date math usually, but we can pass string for simple check
    c.execute(q("SELECT * FROM users WHERE email = ? AND verification_code = ? AND code_expiry > CURRENT_TIMESTAMP"), (email, code))
    user = c.fetchone()

    if not user:
        conn.close()
        return jsonify({"error": "Invalid or expired code"}), 400

    c.execute(q("UPDATE users SET verified = 1, verification_code = NULL, code_expiry = NULL WHERE email = ?"), (email,))
    conn.commit()
    conn.close()

    return jsonify({
        "message": "Email verified and logged in!",
        "user": {
            "email": email,
            "name": user['name']
        }
    }), 200

@app.route('/resend-code', methods=['POST'])
def resend_code():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({"error": "Email required"}), 400

    conn = get_db_connection()
    c = conn.cursor()
    c.execute(q("SELECT * FROM users WHERE email = ?"), (email,))
    user = c.fetchone()

    if not user:
        conn.close()
        return jsonify({"error": "User not found"}), 404

    if user['verified'] == 1:
        conn.close()
        return jsonify({"error": "Email already verified"}), 400

    verification_code = ''.join(random.choices(string.digits, k=6))
    code_expiry = (datetime.now() + timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S')

    c.execute(q("UPDATE users SET verification_code = ?, code_expiry = ? WHERE email = ?"),
              (verification_code, code_expiry, email))
    conn.commit()
    conn.close()

    subject = "Adire Boutique - New Verification Code"
    body = f"""
    Hello {user['name']},

    Your new verification code is: {verification_code}

    Enter this code on the site to activate your account.
    This code expires in 15 minutes.

    Thank you!
    Adire Team
    """
    send_email(email, subject, body)

    return jsonify({"message": "New code sent to your email."}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    conn = get_db_connection()
    c = conn.cursor()
    c.execute(q("SELECT * FROM users WHERE email = ?"), (email,))
    user = c.fetchone()
    conn.close()

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    
    # Handle both bytes (SQLite) and str (Postgres)
    stored_password = user['password']
    if isinstance(stored_password, str): stored_password = stored_password.encode('utf-8')

    if not bcrypt.checkpw(password.encode('utf-8'), stored_password):
        return jsonify({"error": "Invalid credentials"}), 401

    if user['verified'] == 0:
        return jsonify({"error": "Email not verified"}), 403

    return jsonify({
        "message": "Login successful",
        "user": {
            "email": email,
            "name": user['name'],
            "phone": user['phone'],
            "address": user['address']
        }
    }), 200

@app.route('/user/profile', methods=['GET', 'PUT'])
def user_profile():
    email = request.args.get('email') # Simplified for now, usually would be from JWT
    if not email:
        return jsonify({"error": "Email required"}), 400

    conn = get_db_connection()
    c = conn.cursor()

    if request.method == 'GET':
        c.execute(q("SELECT name, email, phone, address FROM users WHERE email = ?"), (email,))
        user = c.fetchone()
        conn.close()
        if not user:
            return jsonify({"error": "User not found"}), 404
        return jsonify(dict(user)), 200

    if request.method == 'PUT':
        data = request.get_json()
        name = data.get('name')
        phone = data.get('phone')
        address = data.get('address')

        c.execute(q("UPDATE users SET name = ?, phone = ?, address = ? WHERE email = ?"), (name, phone, address, email))
        conn.commit()
        conn.close()
        return jsonify({"message": "Profile updated successfully"}), 200

@app.route('/user/change-password', methods=['POST'])
def change_password():
    data = request.get_json()
    email = data.get('email')
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not email or not old_password or not new_password:
        return jsonify({"error": "Missing fields"}), 400

    conn = get_db_connection()
    c = conn.cursor()
    c.execute(q("SELECT password FROM users WHERE email = ?"), (email,))
    user = c.fetchone()

    if not user:
        conn.close()
        return jsonify({"error": "User not found"}), 404

    stored_password = user['password']
    if isinstance(stored_password, str): stored_password = stored_password.encode('utf-8')

    if not bcrypt.checkpw(old_password.encode('utf-8'), stored_password):
        conn.close()
        return jsonify({"error": "Incorrect biological password"}), 401

    hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    if DATABASE_URL: hashed = hashed.decode('utf-8')

    c.execute(q("UPDATE users SET password = ? WHERE email = ?"), (hashed, email))
    conn.commit()
    conn.close()
    return jsonify({"message": "Password changed successfully"}), 200


@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()

    # Robust check with space stripping
    if ADMIN_EMAIL and email == ADMIN_EMAIL.lower() and password == ADMIN_PASSWORD:
        print(f"Admin login successful: {email}")
        return jsonify({"message": "Admin login OK"}), 200
    else:
        print(f"Admin login failed for: {email}")
        return jsonify({"error": "Invalid admin credentials. Check your .env file."}), 401

@app.route('/admin/products', methods=['POST'])
def admin_add_product():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    price = data.get('price')
    image_base64 = data.get('image_base64')
    gallery = data.get('gallery', '[]') # New gallery field
    category = data.get('category')
    stock = data.get('stock', 10)

    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f"Bearer {ADMIN_PASSWORD}":
        return jsonify({"error": "Admin access only"}), 403

    if not name or not price:
        return jsonify({"error": "Name and price required"}), 400

    conn = get_db_connection()
    c = conn.cursor()
    c.execute(q("INSERT INTO products (name, description, price, image_base64, gallery, category, stock) VALUES (?, ?, ?, ?, ?, ?, ?)"),
              (name, description, price, image_base64, gallery, category, stock))
    conn.commit()
    conn.close()

    return jsonify({"message": "Product added successfully"}), 201

@app.route('/admin/products/<int:id>', methods=['PUT', 'DELETE'])
def admin_manage_product(id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f"Bearer {ADMIN_PASSWORD}":
        return jsonify({"error": "Admin access only"}), 403

    conn = get_db_connection()
    c = conn.cursor()

    if request.method == 'DELETE':
        c.execute(q("DELETE FROM products WHERE id = ?"), (id,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Product deleted"}), 200

    if request.method == 'PUT':
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        price = data.get('price')
        image_base64 = data.get('image_base64')
        gallery = data.get('gallery') # New gallery field
        category = data.get('category')
        stock = data.get('stock')

        # Build update query dynamically
        updates = []
        params = []
        if name: updates.append("name = ?"); params.append(name)
        if description: updates.append("description = ?"); params.append(description)
        if price is not None: updates.append("price = ?"); params.append(price)
        if image_base64: updates.append("image_base64 = ?"); params.append(image_base64)
        if gallery: updates.append("gallery = ?"); params.append(gallery)
        if category: updates.append("category = ?"); params.append(category)
        if stock is not None: updates.append("stock = ?"); params.append(stock)

        if not updates:
            conn.close()
            return jsonify({"message": "Nothing to update"}), 400

        params.append(id)
        query = f"UPDATE products SET {', '.join(updates)} WHERE id = ?"
        c.execute(q(query), tuple(params))
        conn.commit()
        conn.close()
        return jsonify({"message": "Product updated"}), 200

@app.route('/admin/products/<int:id>/stylize', methods=['POST'])
def admin_stylize_product(id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f"Bearer {ADMIN_PASSWORD}":
        return jsonify({"error": "Admin access only"}), 403

    conn = get_db_connection()
    c = conn.cursor()
    c.execute(q("SELECT * FROM products WHERE id = ?"), (id,))
    product = c.fetchone()
    
    if not product:
        conn.close()
        return jsonify({"error": "Product not found"}), 404

    # This logs the request for the AI assistant/agent to handle
    print(f"STYLIZING LOG: AI Style Generation requested for product ID: {id}")
    
    conn.close()
    return jsonify({
        "message": "Styling sequence initiated. Our AI mannequins are preparing the different views.",
        "status": "pending_generation"
    }), 200

@app.route('/products', methods=['GET'])
def get_products():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(q("SELECT * FROM products"))
    products = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(products), 200

@app.route('/track/<int:id>', methods=['GET'])
def track_order(id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(q("SELECT id, status, phone, created_at FROM orders WHERE id = ?"), (id,))
    order = c.fetchone()
    conn.close()
    if order:
        return jsonify(dict(order)), 200
    return jsonify({"error": "Order not found"}), 404

@app.route('/orders/<email>', methods=['GET'])
def get_user_orders(email):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(q("SELECT * FROM orders WHERE user_email = ? ORDER BY created_at DESC"), (email,))
    orders = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(orders), 200

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    user_email = data.get('user_email')
    items = data.get('items') # JSON string of items
    total = data.get('total')
    address = data.get('address')
    phone = data.get('phone')

    if not user_email or not items or not total:
        return jsonify({"error": "Order details required"}), 400

    conn = get_db_connection()
    c = conn.cursor()
    c.execute(q("INSERT INTO orders (user_email, items, total, address, phone) VALUES (?, ?, ?, ?, ?)"),
              (user_email, items, total, address, phone))
    conn.commit()
    conn.close()

    # Admin Notification
    try:
        items = json.loads(items)
        items_list = "\n".join([f"- {item.get('name')} (x{item.get('quantity')}) - N{item.get('price') * item.get('quantity'):,}" for item in items])
        
        subject = f"NEW ORDER RECEIVED - N{total:,}"
        body = f"""
        Hello Admin,

        A new order has been placed on Eury Textiles!

        ORDER DETAILS:
        Customer: {user_email}
        Phone: {phone}
        Address: {address}
        Total: N{total:,}

        ITEMS:
        {items_list}

        Please login to the Admin Dashboard to manage this order.

        Thank you!
        """
        send_email(ADMIN_EMAIL, subject, body)
    except Exception as e:
        print(f"Admin notification failed: {str(e)}")

    return jsonify({"message": "Order placed successfully"}), 201

@app.route('/orders/<int:id>/received', methods=['PUT'])
def mark_order_received(id):
    conn = get_db_connection()
    c = conn.cursor()
    
    # Verify order exists
    c.execute(q("SELECT * FROM orders WHERE id = ?"), (id,))
    order = c.fetchone()
    if not order:
        conn.close()
        return jsonify({"error": "Order not found"}), 404

    # Update status to Delivered
    c.execute(q("UPDATE orders SET status = 'Delivered' WHERE id = ?"), (id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Order marked as received!"}), 200

@app.route('/admin/orders', methods=['GET'])
def get_all_orders():
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f"Bearer {ADMIN_PASSWORD}":
        return jsonify({"error": "Admin access only"}), 403

    search = request.args.get('search', '').strip()
    status = request.args.get('status', '').strip()
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    offset = (page - 1) * limit

    conn = get_db_connection()
    c = conn.cursor()
    
    query = "SELECT * FROM orders"
    params = []
    conditions = []
    
    if search:
        if not DATABASE_URL:
            conditions.append("(id LIKE ? OR user_email LIKE ?)")
        else:
            conditions.append("(CAST(id AS TEXT) LIKE %s OR user_email ILIKE %s)")
        search_param = f"%{search}%"
        params.extend([search_param, search_param])
    
    if status:
        conditions.append("status = ?")
        params.append(status)
        
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
        
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    c.execute(q(query) if not DATABASE_URL else query, params)
    orders = [dict(row) for row in c.fetchall()]
    
    # Get total count for pagination
    count_query = "SELECT COUNT(*) FROM orders"
    if conditions:
        count_query += " WHERE " + " AND ".join(conditions)
    c.execute(q(count_query) if not DATABASE_URL else count_query, params[:-2])
    total = c.fetchone()[0]
    
    conn.close()
    return jsonify({
        "orders": orders,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }), 200

@app.route('/admin/products/<int:id>', methods=['PUT'])
def admin_update_product(id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f"Bearer {ADMIN_PASSWORD}":
        return jsonify({"error": "Admin access only"}), 403

    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    price = data.get('price')
    category = data.get('category')
    stock = data.get('stock')
    image_base64 = data.get('image_base64')

    conn = get_db_connection()
    c = conn.cursor()
    
    # Build update query dynamically based on provided fields
    updates = []
    params = []
    if name: updates.append("name = ?"); params.append(name)
    if description: updates.append("description = ?"); params.append(description)
    if price: updates.append("price = ?"); params.append(price)
    if category: updates.append("category = ?"); params.append(category)
    if stock is not None: updates.append("stock = ?"); params.append(stock)
    if image_base64: updates.append("image_base64 = ?"); params.append(image_base64)
    
    if not updates:
        return jsonify({"error": "No fields to update"}), 400
    
    params.append(id)
    query = f"UPDATE products SET {', '.join(updates)} WHERE id = {get_placeholder() if 'get_placeholder' in globals() else '?'}"
    # Wait, I have q helper now.
    query = q(f"UPDATE products SET {', '.join(updates)} WHERE id = ?")
    c.execute(query, params)
    conn.commit()
    conn.close()

    return jsonify({"message": "Product updated successfully"}), 200

@app.route('/admin/products/<int:id>', methods=['DELETE'])
def admin_delete_product(id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f"Bearer {ADMIN_PASSWORD}":
        return jsonify({"error": "Admin access only"}), 403

    conn = get_db_connection()
    c = conn.cursor()
    c.execute(q("DELETE FROM products WHERE id = ?"), (id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Product deleted successfully"}), 200

@app.route('/admin/orders/<int:id>', methods=['GET'])
def admin_get_order(id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f"Bearer {ADMIN_PASSWORD}":
        return jsonify({"error": "Admin access only"}), 403

    conn = get_db_connection()
    c = conn.cursor()
    c.execute(q("SELECT * FROM orders WHERE id = ?"), (id,))
    order = c.fetchone()
    conn.close()
    
    if not order:
        return jsonify({"error": "Order not found"}), 404
        
    order_dict = dict(order)
    return jsonify(order_dict), 200

@app.route('/admin/orders/<int:id>', methods=['PUT'])
def admin_update_order(id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f"Bearer {ADMIN_PASSWORD}":
        return jsonify({"error": "Admin access only"}), 403

    data = request.get_json()
    status = data.get('status')
    payment_status = data.get('payment_status')
    delivery_status = data.get('delivery_status')
    tracking_number = data.get('tracking_number')
    estimated_delivery = data.get('estimated_delivery')
    refund_amount = data.get('refund_amount')

    conn = get_db_connection()
    c = conn.cursor()
    
    # Get current order state for timeline
    c.execute(q("SELECT timeline, status, payment_status, delivery_status, refunded_amount FROM orders WHERE id = ?"), (id,))
    current = c.fetchone()
    if not current:
        conn.close()
        return jsonify({"error": "Order not found"}), 404
    
    timeline = []
    if current['timeline']:
        import json
        try:
            timeline = json.loads(current['timeline'])
        except:
            timeline = []
            
    updates = []
    params = []
    
    if status and status != current['status']:
        updates.append("status = ?")
        params.append(status)
        timeline.append({"date": datetime.now().strftime('%Y-%m-%d %H:%M'), "action": f"Status changed to {status}"})
        
    if payment_status and payment_status != current['payment_status']:
        updates.append("payment_status = ?")
        params.append(payment_status)
        timeline.append({"date": datetime.now().strftime('%Y-%m-%d %H:%M'), "action": f"Payment marked as {payment_status}"})
        
    if delivery_status and delivery_status != current['delivery_status']:
        updates.append("delivery_status = ?")
        params.append(delivery_status)
        timeline.append({"date": datetime.now().strftime('%Y-%m-%d %H:%M'), "action": f"Delivery updated to {delivery_status}"})
        
    if tracking_number is not None:
        updates.append("tracking_number = ?")
        params.append(tracking_number)
        timeline.append({"date": datetime.now().strftime('%Y-%m-%d %H:%M'), "action": f"Tracking number updated: {tracking_number}"})
        
    if estimated_delivery:
        updates.append("estimated_delivery = ?")
        params.append(estimated_delivery)

    if refund_amount is not None:
        new_refund_total = (current['refunded_amount'] or 0) + int(refund_amount)
        updates.append("refunded_amount = ?")
        params.append(new_refund_total)
        timeline.append({"date": datetime.now().strftime('%Y-%m-%d %H:%M'), "action": f"Issued refund of ₦{refund_amount}. Total refunded: ₦{new_refund_total}"})
        if status != 'Refunded': # Auto-update status if fully/partially refunded and not already set
             updates.append("status = ?")
             params.append('Refunded')
        
    if timeline:
        import json
        updates.append("timeline = ?")
        params.append(json.dumps(timeline))
        
    if not updates:
        conn.close()
        return jsonify({"message": "No changes"}), 200
        
    params.append(id)
    c.execute(q(f"UPDATE orders SET {', '.join(updates)} WHERE id = ?"), params)
    conn.commit()
    
    log_admin_action(ADMIN_EMAIL, f"Updated order {id}", f"Fields: {', '.join(updates)}")
    
    conn.close()
    return jsonify({"message": "Order updated"}), 200

@app.route('/admin/customers', methods=['GET'])
def admin_get_customers():
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f"Bearer {ADMIN_PASSWORD}":
        return jsonify({"error": "Admin access only"}), 403

    search = request.args.get('search', '').strip()
    status = request.args.get('status', '').strip()

    conn = get_db_connection()
    c = conn.cursor()
    
    query = "SELECT id, email, name, phone, status, created_at FROM users"
    params = []
    conditions = []
    
    if search:
        if not DATABASE_URL:
            conditions.append("(name LIKE ? OR email LIKE ? OR phone LIKE ?)")
        else:
            conditions.append("(name ILIKE %s OR email ILIKE %s OR phone ILIKE %s)")
        search_param = f"%{search}%"
        params.extend([search_param, search_param, search_param])
    
    if status:
        conditions.append("status = ?")
        params.append(status)
        
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
        
    query += " ORDER BY created_at DESC"
    
    c.execute(q(query) if not DATABASE_URL else query, params)
    users = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(users), 200

@app.route('/admin/customers/<int:id>', methods=['GET', 'PUT'])
def admin_manage_customer(id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f"Bearer {ADMIN_PASSWORD}":
        return jsonify({"error": "Admin access only"}), 403

    conn = get_db_connection()
    c = conn.cursor()

    if request.method == 'GET':
        c.execute(q("SELECT * FROM users WHERE id = ?"), (id,))
        user = c.fetchone()
        if not user: return jsonify({"error": "User not found"}), 404
        # Get order count and total spent
        c.execute(q("SELECT COUNT(*), SUM(total) FROM orders WHERE user_email = ?"), (user['email'],))
        stats = c.fetchone()
        
        c.execute(q("SELECT id, total, status, created_at FROM orders WHERE user_email = ? ORDER BY created_at DESC"), (user['email'],))
        orders = [dict(row) for row in c.fetchall()]
        
        user_dict = dict(user)
        user_dict['order_count'] = stats[0] or 0
        user_dict['total_spent'] = stats[1] or 0
        user_dict['orders'] = orders
        conn.close()
        return jsonify(user_dict), 200

    # PUT - Update details or status
    data = request.get_json()
    status = data.get('status')
    notes = data.get('admin_notes')
    
    updates = []
    params = []
    if status: updates.append("status = ?"); params.append(status)
    if notes: updates.append("admin_notes = ?"); params.append(notes)
    
    if updates:
        params.append(id)
        c.execute(q(f"UPDATE users SET {', '.join(updates)} WHERE id = ?"), params)
        conn.commit()
        log_admin_action(ADMIN_EMAIL, f"Updated customer {id}", f"Status: {status}, Notes updated")
    
    conn.close()
    return jsonify({"message": "Customer updated"}), 200

@app.route('/admin/reports', methods=['GET'])
def admin_get_reports():
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f"Bearer {ADMIN_PASSWORD}":
        return jsonify({"error": "Admin access only"}), 403

    conn = get_db_connection()
    c = conn.cursor()
    
    # 1. Revenue Trends (Monthly)
    if not DATABASE_URL:
        c.execute("SELECT strftime('%Y-%m', created_at) as period, SUM(total - refunded_amount) as revenue, COUNT(*) as orders FROM orders WHERE status != 'Cancelled' GROUP BY period ORDER BY period DESC LIMIT 12")
    else:
        c.execute("SELECT to_char(created_at, 'YYYY-MM') as period, SUM(total - refunded_amount) as revenue, COUNT(*) as orders FROM orders WHERE status != 'Cancelled' GROUP BY period ORDER BY period DESC LIMIT 12")
    revenue_trends = [dict(row) for row in c.fetchall()]
    
    # 2. Daily Sales (Last 30 days)
    if not DATABASE_URL:
        c.execute("SELECT strftime('%Y-%m-%d', created_at) as period, SUM(total - refunded_amount) as revenue FROM orders WHERE status != 'Cancelled' AND created_at > date('now', '-30 days') GROUP BY period ORDER BY period ASC")
    else:
        c.execute("SELECT to_char(created_at, 'YYYY-MM-DD') as period, SUM(total - refunded_amount) as revenue FROM orders WHERE status != 'Cancelled' AND created_at > CURRENT_DATE - INTERVAL '30 days' GROUP BY period ORDER BY period ASC")
    daily_sales = [dict(row) for row in c.fetchall()]

    # 3. Best sellers
    c.execute(q("SELECT items FROM orders WHERE status != 'Cancelled'"))
    import json
    product_stats = {}
    for row in c.fetchall():
        try:
            items = json.loads(row['items'])
            for item in items:
                name = item.get('name')
                product_stats[name] = product_stats.get(name, 0) + item.get('quantity', 1)
        except: continue
    best_sellers = sorted(product_stats.items(), key=lambda x: x[1], reverse=True)[:10]

    # 4. Customer Analytics
    c.execute(q("SELECT COUNT(*) FROM users"))
    total_customers = c.fetchone()[0]
    
    # New vs Returning (Simulated by order count)
    c.execute(q("SELECT user_email, COUNT(*) as cnt FROM orders GROUP BY user_email"))
    customer_orders = c.fetchall()
    returning = len([x for x in customer_orders if x['cnt'] > 1])
    new_cust = len([x for x in customer_orders if x['cnt'] == 1])

    # 5. Average Order Value
    c.execute(q("SELECT AVG(total) FROM orders WHERE status != 'Cancelled'"))
    aov = c.fetchone()[0] or 0

    # 6. Delivery Success Rate
    c.execute(q("SELECT COUNT(*) FROM orders WHERE delivery_status = 'Delivered'"))
    delivered = c.fetchone()[0]
    c.execute(q("SELECT COUNT(*) FROM orders"))
    total_orders = c.fetchone()[0]
    delivery_rate = (delivered / total_orders * 100) if total_orders > 0 else 0

    conn.close()
    return jsonify({
        "revenue_trends": revenue_trends,
        "daily_sales": daily_sales,
        "best_sellers": best_sellers,
        "customer_stats": {
            "total": total_customers,
            "new": new_cust,
            "returning": returning,
            "aov": aov
        },
        "delivery_performance": {
            "success_rate": delivery_rate
        }
    }), 200

@app.route('/admin/reports/export', methods=['GET'])
def admin_export_reports():
    # Simple token check from query param for easy link access
    token = request.args.get('token')
    if not token or token != ADMIN_PASSWORD:
        return jsonify({"error": "Admin access only"}), 403

    conn = get_db_connection()
    c = conn.cursor()
    c.execute(q("SELECT id, user_email, total, status, payment_status, created_at FROM orders ORDER BY created_at DESC"))
    orders = c.fetchall()
    conn.close()

    import io
    import csv
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Order ID', 'Customer', 'Total', 'Status', 'Payment', 'Date'])
    for o in orders:
        writer.writerow([o['id'], o['user_email'], o['total'], o['status'], o['payment_status'], o['created_at']])
    
    output.seek(0)
    return output.getvalue(), 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': 'attachment; filename=orders_report.csv'
    }

@app.route('/admin/settings', methods=['GET', 'POST'])
def admin_manage_settings():
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f"Bearer {ADMIN_PASSWORD}":
        return jsonify({"error": "Admin access only"}), 403

    conn = get_db_connection()
    c = conn.cursor()

    if request.method == 'POST':
        data = request.get_json()
        for key, value in data.items():
            if not DATABASE_URL:
                c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
            else:
                c.execute("INSERT INTO settings (key, value) VALUES (%s, %s) ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value", (key, value))
        conn.commit()
        log_admin_action(ADMIN_EMAIL, "Updated settings", str(list(data.keys())))
        conn.close()
        return jsonify({"message": "Settings updated"}), 200

    c.execute("SELECT * FROM settings")
    settings = {row['key']: row['value'] for row in c.fetchall()}
    conn.close()
    return jsonify(settings), 200

@app.route('/admin/logs', methods=['GET'])
def admin_get_logs():
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f"Bearer {ADMIN_PASSWORD}":
        return jsonify({"error": "Admin access only"}), 403

    conn = get_db_connection()
    c = conn.cursor()
    c.execute(q("SELECT * FROM admin_logs ORDER BY created_at DESC LIMIT 100"))
    logs = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(logs), 200

# --- Review Routes ---
@app.route('/reviews', methods=['POST'])
def add_review():
    data = request.get_json()
    product_id = data.get('product_id')
    user_name = data.get('user_name')
    rating = data.get('rating')
    comment = data.get('comment')

    conn = get_db_connection()
    conn.execute("INSERT INTO reviews (product_id, user_name, rating, comment) VALUES (?, ?, ?, ?)",
                 (product_id, user_name, rating, comment))
    conn.commit()
    conn.close()
    return jsonify({"message": "Review submitted for approval"}), 201

@app.route('/admin/reviews', methods=['GET'])
def get_all_reviews():
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f"Bearer {ADMIN_PASSWORD}":
        return jsonify({"error": "Admin access only"}), 403

    conn = get_db_connection()
    # Join with products to get product name
    query = """
        SELECT r.*, p.name as product_name 
        FROM reviews r 
        LEFT JOIN products p ON r.product_id = p.id 
        ORDER BY r.created_at DESC
    """
    conn.execute(query)
    # Correct way to fetch with join using row_factory
    c = conn.cursor()
    c.execute(query)
    reviews = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(reviews), 200

@app.route('/admin/reviews/<int:id>', methods=['PUT', 'DELETE'])
def manage_review(id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f"Bearer {ADMIN_PASSWORD}":
        return jsonify({"error": "Admin access only"}), 403

    conn = get_db_connection()
    
    if request.method == 'DELETE':
        conn.execute("DELETE FROM reviews WHERE id = ?", (id,))
        msg = "Review deleted"
    else: # PUT - Approve status
        status = request.get_json().get('status', 'Approved')
        conn.execute("UPDATE reviews SET status = ? WHERE id = ?", (status, id))
        msg = f"Review {status}"
    
    conn.commit()
    conn.close()
    return jsonify({"message": msg}), 200

# --- Reports Route (Basic) ---
@app.route('/admin/reports/stats', methods=['GET'])
def get_report_stats():
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f"Bearer {ADMIN_PASSWORD}":
        return jsonify({"error": "Admin access only"}), 403
        
    conn = get_db_connection()
    c = conn.cursor()
    
    # Total Revenue
    c.execute(q("SELECT SUM(total) FROM orders WHERE status != 'Cancelled'"))
    total_revenue = c.fetchone()
    total_revenue = total_revenue[0] if total_revenue else 0
    if total_revenue is None: total_revenue = 0
    
    # Orders Count
    c.execute(q("SELECT COUNT(*) FROM orders"))
    # Fetch result carefully for Postgres/SQLite
    row = c.fetchone()
    total_orders = row[0] if row else 0
    
    # Products Count
    c.execute(q("SELECT COUNT(*) FROM products"))
    row = c.fetchone()
    total_products = row[0] if row else 0
    
    conn.close()
    
    return jsonify({
        "revenue": total_revenue,
        "orders": total_orders,
        "products": total_products
    }), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
