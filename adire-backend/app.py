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
import requests

print("Loading environment variables...")
load_dotenv()

app = Flask(__name__, static_folder='..', static_url_path='')
CORS(app)

print("Parsing configuration...")
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', '').strip()
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', '').strip()
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
try:
    email_port_env = os.getenv('EMAIL_PORT')
    EMAIL_PORT = int(email_port_env) if email_port_env and email_port_env.strip() else 587
except ValueError:
    print(f"Warning: Invalid EMAIL_PORT '{os.getenv('EMAIL_PORT')}', defaulting to 587")
    EMAIL_PORT = 587

DATABASE_URL = os.getenv('DATABASE_URL')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "adire.db")

def get_db_connection():
    try:
        if DATABASE_URL:
            if not PSYCOPG2_AVAILABLE:
                raise Exception("Postgres support (psycopg2) is not installed. Please run 'pip install psycopg2-binary'")
            # Add a timeout to the connection attempt for cloud environments
            conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor, connect_timeout=5)
            conn.autocommit = True
            return conn
        
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Database Connection Error: {e}")
        return None

def q(query):
    return query.replace('?', '%s') if DATABASE_URL else query

def log_admin_action(admin_email, action, details=None):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(q("INSERT INTO admin_logs (admin_email, action, details) VALUES (?, ?, ?)"),
              (admin_email, action, details))
    conn.commit()
    conn.close()

def rest_fallback_request(table, method='GET', query_params=None, data=None):
    """Helper to perform Supabase REST API requests as a fallback"""
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        return None
        
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    try:
        if method == 'GET':
            resp = requests.get(url, headers=headers, params=query_params, timeout=10)
        elif method == 'POST':
            resp = requests.post(url, headers=headers, json=data, timeout=10)
        elif method == 'PATCH':
            resp = requests.patch(url, headers=headers, json=data, params=query_params, timeout=10)
        elif method == 'DELETE':
            resp = requests.delete(url, headers=headers, params=query_params, timeout=10)
        else:
            return None
            
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"REST Fallback Error: {e}")
        return None

@app.errorhandler(500)
def handle_500(e):
    return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

def init_db():
    try:
        conn = get_db_connection()
        if not conn:
            print("Skipping DB initialization: Connection failed.")
            return
            
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
                    role TEXT DEFAULT 'user',
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
                    image_url TEXT,
                    gallery TEXT,
                    category TEXT,
                    stock INTEGER DEFAULT 10,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )''',
                '''CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_email TEXT NOT NULL,
                    user_id TEXT,
                    items TEXT NOT NULL,
                    total_amount INTEGER NOT NULL,
                    shipping_address TEXT,
                    phone TEXT,
                    payment_method TEXT,
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
                    role TEXT DEFAULT 'user',
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
                    image_url TEXT,
                    gallery TEXT,
                    category TEXT,
                    stock INTEGER DEFAULT 10,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''',
                '''CREATE TABLE IF NOT EXISTS orders (
                    id SERIAL PRIMARY KEY,
                    user_email TEXT NOT NULL,
                    user_id TEXT,
                    items JSONB NOT NULL,
                    total_amount INTEGER NOT NULL,
                    shipping_address TEXT,
                    phone TEXT,
                    payment_method TEXT,
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
    except Exception as e:
        print(f"Database initialization failed: {e}")

def migrate_db():
    conn = get_db_connection()
    if not conn: return
    c = conn.cursor()
    try:
        if not DATABASE_URL:
            # SQLite
            try: c.execute("ALTER TABLE users ADD COLUMN address TEXT")
            except: pass
            try: c.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
            except: pass
            try: c.execute("ALTER TABLE users ADD COLUMN verified INTEGER DEFAULT 0")
            except: pass
            try: c.execute("ALTER TABLE users ADD COLUMN verification_code TEXT")
            except: pass
            try: c.execute("ALTER TABLE users ADD COLUMN code_expiry DATETIME")
            except: pass
            try: c.execute("ALTER TABLE products ADD COLUMN image_url TEXT")
            except: pass
            # Orders table migrations
            try: c.execute("ALTER TABLE orders ADD COLUMN user_id TEXT")
            except: pass
            try: c.execute("ALTER TABLE orders ADD COLUMN total_amount INTEGER")
            except: pass
            try: c.execute("ALTER TABLE orders ADD COLUMN shipping_address TEXT")
            except: pass
            try: c.execute("ALTER TABLE orders ADD COLUMN payment_method TEXT")
            except: pass
        else:
            # Postgres
            try: c.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS address TEXT")
            except: pass
            try: c.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS role TEXT DEFAULT 'user'")
            except: pass
            try: c.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS verified INTEGER DEFAULT 0")
            except: pass
            try: c.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_code TEXT")
            except: pass
            try: c.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS code_expiry TIMESTAMP")
            except: pass
            try: c.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS image_url TEXT")
            except: pass
            # Orders table migrations
            try: c.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS user_id TEXT")
            except: pass
            try: c.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS total_amount INTEGER")
            except: pass
            try: c.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS shipping_address TEXT")
            except: pass
            try: c.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS payment_method TEXT")
            except: pass
            
            # Sync existing and new columns in Postgres if needed
            try:
                c.execute("UPDATE orders SET total_amount = total WHERE total_amount IS NULL AND total IS NOT NULL")
                c.execute("UPDATE orders SET shipping_address = address WHERE shipping_address IS NULL AND address IS NOT NULL")
            except: pass
        
        # Ensure ADMIN_EMAIL has admin role
        if ADMIN_EMAIL:
            print(f"Ensuring {ADMIN_EMAIL} has admin role...")
            c.execute(q("UPDATE users SET role = 'admin' WHERE email = ?"), (ADMIN_EMAIL.lower(),))
            
        conn.commit()
    except Exception as e:
        print(f"Migration error: {e}")
    conn.close()

# The database is initialized in the main block below

def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=10)
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

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    if DATABASE_URL: hashed = hashed.decode('utf-8')

    verification_code = ''.join(random.choices(string.digits, k=6))
    code_expiry = (datetime.now() + timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S')

    # Save to database
    try:
        conn = get_db_connection()
        if not conn:
            # Attempt REST fallback for registration
            print("Attempting REST fallback for registration...")
            # Check if email exists
            user_list = rest_fallback_request('users', query_params={'email': f"eq.{email}"})
            if user_list and len(user_list) > 0:
                return jsonify({"error": "Email already exists"}), 400
            
            # Insert via REST
            res = rest_fallback_request('users', method='POST', data={
                'email': email, 'password': hashed, 'name': name,
                'verification_code': verification_code, 'code_expiry': code_expiry, 'verified': 0
            })
            if res is None:
                return jsonify({"error": "Registration failed (REST Fallback)"}), 500
        else:
            c = conn.cursor()
            # Check if email exists
            c.execute(q("SELECT * FROM users WHERE email = ?"), (email,))
            if c.fetchone():
                conn.close()
                return jsonify({"error": "Email already exists"}), 400
                
            c.execute(q("INSERT INTO users (email, password, name, verification_code, code_expiry, verified) VALUES (?, ?, ?, ?, ?, ?)"),
                      (email, hashed, name, verification_code, code_expiry, 0))
            conn.commit()
            conn.close()
    except Exception as e:
        print(f"Registration Error: {e}")
        return jsonify({"error": "Registration failed", "details": str(e)}), 500
    finally:
        if 'conn' in locals() and conn: conn.close()

    subject = "Adire Boutique - Verify Your Email"
    body = f"Hello {name},\n\nWelcome to Adire Boutique!\n\nYour verification code is: {verification_code}\n\nEnter this code on the site to activate your account.\nThis code expires in 15 minutes.\n\nIf you didn't sign up, ignore this email.\n\nThank you!\nAdire Team"
    
    send_email(email, subject, body)
    return jsonify({"message": "Registration successful. Check your email for verification code."}), 201



@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()
    email = data.get('email')
    code = data.get('code')

    if not email or not code:
        return jsonify({"error": "Email and code required"}), 400

    user = None
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute(q("SELECT * FROM users WHERE email = ? AND verification_code = ? AND code_expiry > CURRENT_TIMESTAMP"), (email, code))
        user_row = c.fetchone()
        if user_row:
            user = dict(user_row)
            c.execute(q("UPDATE users SET verified = 1, verification_code = NULL, code_expiry = NULL WHERE email = ?"), (email,))
            conn.commit()
            conn.close()
    except Exception as e:
        print(f"Direct DB Error in verify: {e}")
        # REST Fallback
        print("Attempting REST fallback for verify...")
        rest_users = rest_fallback_request('users', query_params={'email': "eq.{}".format(email), 'verification_code': "eq.{}".format(code)})
        # Note: can't easily check expiry via REST simple query without complex PostgREST filters
        if rest_users and len(rest_users) > 0:
            user = rest_users[0]
            rest_fallback_request('users', method='PATCH', query_params={'email': "eq.{}".format(email)}, 
                                  data={"verified": 1, "verification_code": None, "code_expiry": None})

    if not user:
        return jsonify({"error": "Invalid or expired code"}), 400

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
    if not conn:
        # REST Fallback for resend_code
        user_list = rest_fallback_request('users', query_params={'email': "eq.{}".format(email)})
        if not user_list:
            return jsonify({"error": "User not found"}), 404
        user = user_list[0]
        
        if user.get('verified', 0) == 1:
            return jsonify({"error": "Email already verified"}), 400

        verification_code = ''.join(random.choices(string.digits, k=6))
        code_expiry = (datetime.now() + timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S')
        
        rest_fallback_request('users', method='PATCH', query_params={'email': "eq.{}".format(email)},
                              data={'verification_code': verification_code, 'code_expiry': code_expiry})
        
        subject = "Adire Boutique - New Verification Code"
        body = f"Hello {user.get('name', 'User')},\n\nYour new verification code is: {verification_code}\n\nEnter this code on the site to activate your account.\nThis code expires in 15 minutes.\n\nThank you!\nAdire Team"
        send_email(email, subject, body)
        return jsonify({"message": "New code sent to your email."}), 200

    try:
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
        body = f"Hello {user['name']},\n\nYour new verification code is: {verification_code}\n\nEnter this code on the site to activate your account.\nThis code expires in 15 minutes.\n\nThank you!\nAdire Team"
        send_email(email, subject, body)

        return jsonify({"message": "New code sent to your email."}), 200
    except Exception as e:
        if 'conn' in locals() and conn: conn.close()
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = None
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute(q("SELECT * FROM users WHERE email = ?"), (email,))
        user_row = c.fetchone()
        conn.close()
        if user_row:
            user = dict(user_row)
    except Exception as e:
        print(f"Direct DB Error in login: {e}")
        # Fallback to REST API
        print("Attempting REST fallback for login...")
        rest_users = rest_fallback_request('users', query_params={'email': "eq.{}".format(email)})
        if rest_users and len(rest_users) > 0:
            user = rest_users[0]

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    
    # Handle both bytes (SQLite) and str (Postgres)
    stored_password = user['password']
    if isinstance(stored_password, str): stored_password = stored_password.encode('utf-8')

    if not bcrypt.checkpw(password.encode('utf-8'), stored_password):
        return jsonify({"error": "Invalid credentials"}), 401

    if user.get('verified', 1) == 0:
        return jsonify({"error": "Email not verified"}), 403

    return jsonify({
        "message": "Login successful",
        "user": {
            "email": email,
            "name": user.get('name'),
            "phone": user.get('phone'),
            "address": user.get('address'),
            "role": user.get('role', 'user')
        }
    }), 200

@app.route('/user/profile', methods=['GET', 'PUT'])
def user_profile():
    email = request.args.get('email') 
    if not email:
        return jsonify({"error": "Email required"}), 400

    conn = get_db_connection()
    if not conn:
        if request.method == 'GET':
            # Defensive: Get all columns and handle missing fields in Python
            user_list = rest_fallback_request('users', method='GET', query_params={'email': "eq.{}".format(email)})
            if not user_list:
                return jsonify({"error": "User not found"}), 404
            
            user_data = user_list[0]
            # Ensure required fields exist in response
            resolved_data = {
                "name": user_data.get('name'),
                "email": user_data.get('email'),
                "phone": user_data.get('phone'),
                "address": user_data.get('address'),
                "role": user_data.get('role', 'user')
            }
            return jsonify(resolved_data), 200
        if request.method == 'PUT':
            data = request.get_json()
            updated = rest_fallback_request('users', method='PATCH', query_params={'email': "eq.{}".format(email)}, data=data)
            if updated is None:
                return jsonify({"error": "Update failed"}), 500
            return jsonify({"message": "Profile updated successfully"}), 200
        return jsonify({"error": "Database connection failed"}), 500

    c = conn.cursor()

    if request.method == 'GET':
        try:
            c.execute(q("SELECT name, email, phone, address, role FROM users WHERE email = ?"), (email,))
            user = c.fetchone()
            conn.close()
            if not user:
                return jsonify({"error": "User not found"}), 404
            return jsonify(dict(user)), 200
        except Exception as e:
            # Fallback for missing role column in local/direct DB
            print(f"SQL Role Fetch Error (likely missing column): {e}")
            c.execute(q("SELECT name, email, phone, address FROM users WHERE email = ?"), (email,))
            user = c.fetchone()
            conn.close()
            if not user:
                return jsonify({"error": "User not found"}), 404
            data = dict(user)
            data['role'] = 'user'
            return jsonify(data), 200

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
    if not conn:
        # Fetch user via REST first to verify old password
        user_list = rest_fallback_request('users', query_params={'email': "eq.{}".format(email)})
        if not user_list: return jsonify({"error": "User not found"}), 404
        user = user_list[0]
        stored_password = user['password']
        if isinstance(stored_password, str): stored_password = stored_password.encode('utf-8')
        if not bcrypt.checkpw(old_password.encode('utf-8'), stored_password):
            return jsonify({"error": "Incorrect password"}), 401
        
        # Update password via REST
        hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        if DATABASE_URL: hashed = hashed.decode('utf-8')
        updated = rest_fallback_request('users', method='PATCH', query_params={'email': "eq.{}".format(email)}, data={'password': hashed})
        if updated is None: return jsonify({"error": "Failed to update profile via REST"}), 500
        return jsonify({"message": "Password changed successfully"}), 200

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
        return jsonify({"error": "Incorrect password"}), 401

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
    image_url = data.get('image_url')
    gallery = data.get('gallery', '[]')
    category = data.get('category')
    stock = data.get('stock', 10)

    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != "Bearer " + ADMIN_PASSWORD:
        return jsonify({"error": "Admin access only"}), 403

    if not name or not price:
        return jsonify({"error": "Name and price required"}), 400

    conn = get_db_connection()
    if not conn:
        res = rest_fallback_request('products', method='POST', data={
            'name': name, 'description': description, 'price': price,
            'image_base64': image_base64, 'image_url': image_url, 'gallery': gallery,
            'category': category, 'stock': stock
        })
        if res is None: return jsonify({"error": "Failed to add product"}), 500
        return jsonify({"message": "Product added successfully"}), 201

    c = conn.cursor()
    c.execute(q("INSERT INTO products (name, description, price, image_base64, image_url, gallery, category, stock) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"),
              (name, description, price, image_base64, image_url, gallery, category, stock))
    conn.commit()
    conn.close()

    return jsonify({"message": "Product added successfully"}), 201

@app.route('/admin/products/<id>', methods=['PUT', 'DELETE'])
def admin_manage_product(id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != "Bearer " + ADMIN_PASSWORD:
        return jsonify({"error": "Admin access only"}), 403

    conn = get_db_connection()
    if not conn:
        # Fallback to REST
        if request.method == 'DELETE':
            res = rest_fallback_request('products', method='DELETE', query_params={'id': f"eq.{id}"})
            if res is None: return jsonify({"error": "Failed to delete product (REST)"}), 500
            return jsonify({"message": "Product deleted"}), 200
        elif request.method == 'PUT':
            data = request.get_json()
            # Map PUT to PATCH for Supabase
            res = rest_fallback_request('products', method='PATCH', data=data, query_params={'id': f"eq.{id}"})
            if res is None: return jsonify({"error": "Failed to update product (REST)"}), 500
            return jsonify({"message": "Product updated"}), 200
        return jsonify({"error": "Database unavailable"}), 500

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
        image_url = data.get('image_url')
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
        if image_url: updates.append("image_url = ?"); params.append(image_url)
        if gallery: updates.append("gallery = ?"); params.append(gallery)
        if category: updates.append("category = ?"); params.append(category)
        if stock is not None: updates.append("stock = ?"); params.append(stock)

        if not updates:
            conn.close()
            return jsonify({"message": "Nothing to update"}), 400

        query_str = "UPDATE products SET " + ", ".join(updates) + " WHERE id = ?"
        c.execute(q(query_str), params + [id])
        conn.commit()
        conn.close()
        return jsonify({"message": "Product updated"}), 200

@app.route('/admin/products/<id>/stylize', methods=['POST'])
def admin_stylize_product(id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != "Bearer " + ADMIN_PASSWORD:
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
    products = []

    conn = get_db_connection()
    if not conn:
        print("Attempting REST fallback for get_products (conn is None)...")
        rest_products = rest_fallback_request('products')
        if rest_products:
            products = rest_products
        return jsonify(products), 200

    try:
        c = conn.cursor()
        c.execute(q("SELECT * FROM products"))
        products = [dict(row) for row in c.fetchall()]
        conn.close()
    except Exception as e:
        print(f"Direct DB Error in get_products: {e}")
        print("Attempting REST fallback for get_products...")
        rest_products = rest_fallback_request('products')
        if rest_products:
            products = rest_products
            
    return jsonify(products), 200

@app.route('/track/<id>', methods=['GET'])
def track_order(id):
    order = None
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute(q("SELECT id, status, tracking_number, estimated_delivery, timeline FROM orders WHERE id = ?"), (id,))
        row = c.fetchone()
        if row: order = dict(row)
        conn.close()
    except Exception as e:
        print(f"Direct DB Error in track_order: {e}")
        rest_orders = rest_fallback_request('orders', query_params={'id': "eq.{}".format(id)})
        if rest_orders: order = rest_orders[0]

    if not order:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(order), 200

@app.route('/orders/<email>', methods=['GET'])
def get_user_orders(email):
    orders = []
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute(q("SELECT * FROM orders WHERE user_email = ? ORDER BY created_at DESC"), (email,))
        orders = [dict(row) for row in c.fetchall()]
        conn.close()
    except Exception as e:
        print(f"Direct DB Error in get_user_orders: {e}")
        rest_orders = rest_fallback_request('orders', query_params={'user_email': "eq.{}".format(email), 'order': 'created_at.desc'})
        if rest_orders: orders = rest_orders

    return jsonify(orders), 200

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    email = data.get('user_email')
    user_id = data.get('user_id')
    items = data.get('items') # Can be list or string
    total_amount = data.get('total') or data.get('total_amount')
    address = data.get('address') or data.get('shipping_address')
    phone = data.get('phone')
    payment_method = data.get('payment_method', 'Cash on Delivery')

    if not email or not items or not total_amount or not address or not phone:
        return jsonify({"error": "Missing required order details", "received": data}), 400

    # Harden items parsing
    if isinstance(items, str):
        try:
            items_json = items
            items_list = json.loads(items)
        except:
            return jsonify({"error": "Invalid items format"}), 400
    else:
        items_json = json.dumps(items)
        items_list = items

    # Create order
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute(q("INSERT INTO orders (user_email, user_id, items, total_amount, shipping_address, phone, payment_method, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"),
                  (email, user_id, items_json, total_amount, address, phone, payment_method, 'Pending'))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Direct DB Error in create_order: {e}")
        # REST Fallback
        print("Attempting REST fallback for create_order...")
        order_data = {
            "user_email": email,
            "user_id": user_id,
            "items": items_list, # Supabase handles JSONB
            "total_amount": total_amount,
            "shipping_address": address,
            "phone": phone,
            "payment_method": payment_method,
            "status": 'Pending'
        }
        rest_fallback_request('orders', method='POST', data=order_data)

    # Admin Notification
    try:
        items_parsed = json.loads(items)
        items_list = "\n".join([f"- {item.get('name')} (x{item.get('quantity')}) - N{item.get('price') * item.get('quantity'):,}" for item in items_parsed])
        
        subject = "NEW ORDER RECEIVED - N{:,}".format(total_amount)
        body = "Hello Admin,\n\nA new order has been placed on Eury Textiles!\n\nORDER DETAILS:\nCustomer: {}\nPhone: {}\nAddress: {}\nTotal: N{:,}\n\nITEMS:\n{}\n\nPlease login to the Admin Dashboard to manage this order.\n\nThank you!".format(email, phone, address, total_amount, items_list)
        send_email(ADMIN_EMAIL, subject, body)
    except Exception as e:
        print(f"Admin notification failed: {str(e)}")

    return jsonify({"message": "Order created successfully"}), 201

@app.route('/orders/<id>/receive', methods=['POST'])
def mark_order_received(id):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute(q("UPDATE orders SET status = 'Received' WHERE id = ?"), (id,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Direct DB Error in mark_order_received: {e}")
        rest_fallback_request('orders', method='PATCH', query_params={'id': "eq.{}".format(id)}, data={"status": "Received"})

    return jsonify({"message": "Order marked as received"}), 200

@app.route('/admin/orders', methods=['GET'])
def get_all_orders():
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != "Bearer " + ADMIN_PASSWORD:
        return jsonify({"error": "Admin access only"}), 403

    search = request.args.get('search', '').strip()
    status = request.args.get('status', '').strip()
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    offset = (page - 1) * limit

    orders = []
    total = 0
    
    try:
        conn = get_db_connection()
        if not conn: raise Exception("Conn failed")
        c = conn.cursor()
        
        query = "SELECT * FROM orders"
        params = []
        conditions = []
        
        if search:
            if not DATABASE_URL:
                conditions.append("(id LIKE ? OR user_email LIKE ?)")
            else:
                conditions.append("(CAST(id AS TEXT) LIKE %s OR user_email ILIKE %s)")
            search_param = "%" + search + "%"
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
        
        count_query = "SELECT COUNT(*) FROM orders"
        if conditions:
            count_query += " WHERE " + " AND ".join(conditions)
        c.execute(q(count_query) if not DATABASE_URL else count_query, params[:-2])
        total = c.fetchone()[0]
        conn.close()
    except Exception as e:
        print(f"Direct DB Error in get_all_orders: {e}")
        # Simplified REST fallback
        query_params = {'order': 'created_at.desc', 'limit': limit, 'offset': offset}
        if status: query_params['status'] = "eq." + status
        if search: 
             search_val = "ilike.*" + search + "*"
             query_params['or'] = "(user_email." + search_val + ")"
        
        rest_orders = rest_fallback_request('orders', query_params=query_params)
        if rest_orders:
            orders = rest_orders
            total = len(orders) # Approximated

    return jsonify({
        "orders": orders,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit if total > 0 else 1
    }), 200

@app.route('/admin/products/<int:id>', methods=['PUT'])
def admin_update_product(id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != "Bearer " + ADMIN_PASSWORD:
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
    query_str = "UPDATE products SET " + ", ".join(updates) + " WHERE id = ?"
    query = q(query_str)
    c.execute(query, params)
    conn.commit()
    conn.close()

    return jsonify({"message": "Product updated successfully"}), 200

@app.route('/admin/products/<int:id>', methods=['DELETE'])
def admin_delete_product(id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != "Bearer " + ADMIN_PASSWORD:
        return jsonify({"error": "Admin access only"}), 403

    conn = get_db_connection()
    c = conn.cursor()
    c.execute(q("DELETE FROM products WHERE id = ?"), (id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Product deleted successfully"}), 200

@app.route('/admin/orders/<id>', methods=['GET'])
def admin_get_order(id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != "Bearer " + ADMIN_PASSWORD:
        return jsonify({"error": "Admin access only"}), 403

    order = None
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute(q("SELECT * FROM orders WHERE id = ?"), (id,))
        row = c.fetchone()
        if row: order = dict(row)
        conn.close()
    except Exception as e:
        print(f"Direct DB Error in admin_get_order: {e}")
        rest_orders = rest_fallback_request('orders', query_params={'id': "eq.{}".format(id)})
        if rest_orders: order = rest_orders[0]

    if not order:
        return jsonify({"error": "Order not found"}), 404
        
    return jsonify(order), 200

@app.route('/admin/orders/<id>', methods=['PUT'])
def admin_update_order(id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != "Bearer " + ADMIN_PASSWORD:
        return jsonify({"error": "Admin access only"}), 403

    data = request.get_json()
    status = data.get('status')
    payment_status = data.get('payment_status')
    delivery_status = data.get('delivery_status')
    tracking_number = data.get('tracking_number')

    updates = []
    params = []
    if status: updates.append("status = ?"); params.append(status)
    if payment_status: updates.append("payment_status = ?"); params.append(payment_status)
    if delivery_status: updates.append("delivery_status = ?"); params.append(delivery_status)
    if tracking_number: updates.append("tracking_number = ?"); params.append(tracking_number)

    if not updates:
        return jsonify({"error": "No fields to update"}), 400

    try:
        conn = get_db_connection()
        c = conn.cursor()
        query_str = "UPDATE orders SET " + ", ".join(updates) + " WHERE id = ?"
        c.execute(q(query_str), params + [id])
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Direct DB Error in admin_update_order: {e}")
        # REST fallback (Supabase uses PATCH for partial updates)
        rest_fallback_request('orders', method='PATCH', query_params={'id': f"eq.{id}"}, data=data)

    return jsonify({"message": "Order updated successfully"}), 200

@app.route('/admin/customers', methods=['GET'])
def admin_get_customers():
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != "Bearer " + ADMIN_PASSWORD:
        return jsonify({"error": "Admin access only"}), 403

    search = request.args.get('search', '').strip()
    status = request.args.get('status', '').strip()

    users = []
    try:
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
            
            search_param = "%" + search + "%"
            params.extend([search_param, search_param, search_param])
        
        if status:
            conditions.append("status = ?")
            params.append(status)
            
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        query += " ORDER BY created_at DESC"
        
        # Use q() to handle ? translation if needed
        final_query = q(query)
        c.execute(final_query, params)
        users = [dict(row) for row in c.fetchall()]
        conn.close()
    except Exception as e:
        print("Direct DB Error in admin_get_customers: " + str(e))
        print("Attempting REST fallback for admin_get_customers...")
        # Simple fallback without complex search for now
        query_params = {}
        if status: query_params['status'] = "eq." + status
        # For search, we combine .or with ilike
        if search:
            query_params['or'] = "(name.ilike.*" + search + "*,email.ilike.*" + search + "*,phone.ilike.*" + search + "*)"
        
        rest_users = rest_fallback_request('users', query_params=query_params)
        if rest_users:
            users = rest_users

    return jsonify(users), 200

@app.route('/admin/customers/<id>', methods=['GET', 'PUT'])
def admin_manage_customer(id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != "Bearer " + ADMIN_PASSWORD:
        return jsonify({"error": "Admin access only"}), 403

    user = None
    orders = []
    stats = {"total_spent": 0, "order_count": 0}

    if request.method == 'GET':
        try:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute(q("SELECT * FROM users WHERE id = ?"), (id,))
            user_row = c.fetchone()
            if user_row:
                user = dict(user_row)
                # Fetch orders
                c.execute(q("SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC"), (id,))
                orders = [dict(row) for row in c.fetchall()]
                # Fetch stats
                c.execute(q("SELECT COUNT(*) as count, SUM(total_amount) as spent FROM orders WHERE user_id = ?"), (id,))
                row = c.fetchone()
                if row:
                    stats = {"order_count": row['count'] or 0, "total_spent": row['spent'] or 0}
            conn.close()
        except Exception as e:
            print(f"Direct DB Error in manage_customer (GET): {e}")
            print("Attempting REST fallback...")
            rest_users = rest_fallback_request('users', query_params={'id': "eq.{}".format(id)})
            if rest_users:
                user = rest_users[0]
                # REST orders fallback
                rest_orders = rest_fallback_request('orders', query_params={'user_id': "eq.{}".format(id), 'order': 'created_at.desc'})
                if rest_orders:
                    orders = rest_orders
                    stats['order_count'] = len(orders)
                    stats['total_spent'] = sum([o.get('total_amount', 0) for o in orders])

        if not user:
            return jsonify({"error": "User not found"}), 404
            
        user_dict = dict(user)
        user_dict['orders'] = orders
        user_dict['stats'] = stats
        return jsonify(user_dict), 200

    # PUT - Update details or status
    data = request.get_json()
    status = data.get('status')
    notes = data.get('admin_notes')
    
    updates = {}
    if status: updates['status'] = status
    if notes: updates['admin_notes'] = notes
    
    if updates:
        try:
            conn = get_db_connection()
            c = conn.cursor()
            up_items = []
            up_params = []
            for k, v in updates.items():
                up_items.append(f"{k} = ?")
                up_params.append(v)
            up_params.append(id)
            query_str = "UPDATE users SET " + ", ".join(up_items) + " WHERE id = ?"
            c.execute(q(query_str), up_params)
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Direct DB Error in manage_customer (PUT): {e}")
            print("Attempting REST fallback...")
            rest_fallback_request('users', method='PATCH', query_params={'id': "eq.{}".format(id)}, data=updates)
            
        log_admin_action(ADMIN_EMAIL, f"Updated customer {id}", f"Details: {updates}")
    
    return jsonify({"message": "Customer updated"}), 200

@app.route('/admin/reports', methods=['GET'])
def admin_get_reports():
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != "Bearer " + ADMIN_PASSWORD:
        return jsonify({"error": "Admin access only"}), 403

    revenue_trends = []
    daily_sales = []
    best_sellers = []
    total_customers = 0
    new_cust = 0
    returning = 0
    aov = 0
    delivery_rate = 0

    try:
        conn = get_db_connection()
        if not conn: raise Exception("Conn failed")
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
    except Exception as e:
        print(f"Direct DB Error in admin_get_reports: {e}")
        # REST fallback for reports is simplified
        orders = rest_fallback_request('orders', query_params={'status': 'neq.Cancelled'})
        users = rest_fallback_request('users')
        total_customers = len(users) if users else 0
        total_orders = len(orders) if orders else 0
        aov = sum([o.get('total', 0) for o in (orders or [])]) / total_orders if total_orders > 0 else 0

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
    if not auth_header or auth_header != "Bearer " + ADMIN_PASSWORD:
        return jsonify({"error": "Admin access only"}), 403

    conn = get_db_connection()
    if not conn:
        if request.method == 'GET':
            settings = {}
            rest_settings = rest_fallback_request('settings')
            if rest_settings:
                for row in rest_settings:
                    settings[row['key']] = row['value']
            return jsonify(settings), 200
        
        if request.method == 'POST':
            data = request.get_json()
            for key, value in data.items():
                existing = rest_fallback_request('settings', query_params={'key': "eq.{}".format(key)})
                if existing:
                    rest_fallback_request('settings', method='PATCH', query_params={'key': "eq.{}".format(key)}, data={'value': value})
                else:
                    rest_fallback_request('settings', method='POST', data={'key': key, 'value': value})
            return jsonify({"message": "Settings updated"}), 200

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
    if not auth_header or auth_header != "Bearer " + ADMIN_PASSWORD:
        return jsonify({"error": "Admin access only"}), 403

    conn = get_db_connection()
    if not conn:
        logs = rest_fallback_request('admin_logs', query_params={'order': 'created_at.desc'})
        if logs: return jsonify(logs), 200
        return jsonify([]), 200

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
    if not auth_header or auth_header != "Bearer " + ADMIN_PASSWORD:
        return jsonify({"error": "Admin access only"}), 403

    conn = get_db_connection()
    if not conn:
        reviews = []
        rest_reviews = rest_fallback_request('reviews', query_params={'order': 'created_at.desc'})
        if rest_reviews:
            reviews = rest_reviews
        return jsonify(reviews), 200

    # Join with products to get product name
    query = "SELECT r.*, p.name as product_name FROM reviews r LEFT JOIN products p ON r.product_id = p.id ORDER BY r.created_at DESC"
    conn.execute(query)
    # Correct way to fetch with join using row_factory
    c = conn.cursor()
    c.execute(query)
    reviews = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(reviews), 200

@app.route('/admin/reviews/<id>', methods=['PUT', 'DELETE'])
def manage_review(id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != "Bearer " + ADMIN_PASSWORD:
        return jsonify({"error": "Admin access only"}), 403

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    if request.method == 'DELETE':
        conn.execute("DELETE FROM reviews WHERE id = ?", (id,))
        msg = "Review deleted"
    else: # PUT - Approve status
        status = request.get_json().get('status', 'Approved')
        conn.execute("UPDATE reviews SET status = ? WHERE id = ?", (status, id))
    
    conn.commit()
    conn.close()
    return jsonify({"message": msg}), 200

# --- Reports Route (Basic) ---
@app.route('/admin/report-stats', methods=['GET'])
def get_report_stats():
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != "Bearer " + ADMIN_PASSWORD:
        return jsonify({"error": "Admin access only"}), 403

    stats = {}
    try:
        conn = get_db_connection()
        if not conn: raise Exception("Conn failed")
        c = conn.cursor()
        
        c.execute(q("SELECT SUM(total - refunded_amount) FROM orders WHERE status != 'Cancelled'"))
        total_revenue = c.fetchone()[0] or 0
        
        c.execute(q("SELECT COUNT(*) FROM orders"))
        total_orders = c.fetchone()[0]
        
        c.execute(q("SELECT COUNT(*) FROM products"))
        total_products = c.fetchone()[0]
        
        stats = {"revenue": total_revenue, "orders": total_orders, "products": total_products}
        conn.close()
    except Exception as e:
        print(f"Stats error: {e}")
        # REST fallback for stats
        orders = rest_fallback_request('orders', query_params={'status': 'neq.Cancelled'})
        products = rest_fallback_request('products')
        
        revenue = sum([(o.get('total', 0) - (o.get('refunded_amount') or 0)) for o in (orders or [])])
        stats = {
            "revenue": revenue,
            "orders": len(orders) if orders else 0,
            "products": len(products) if products else 0
        }

    return jsonify(stats), 200

@app.route('/api/init-db', methods=['POST'])
def manual_init_db():
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != "Bearer " + ADMIN_PASSWORD:
        return jsonify({"error": "Admin access only"}), 403
    
    try:
        init_db()
        migrate_db()
        return jsonify({"message": "Database initialized/migrated manually"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Global flag to ensure database initialization only runs once
_db_initialized = False

@app.before_request
def startup_initialization():
    global _db_initialized
    if not _db_initialized:
        try:
            print(">>> Running first-request database initialization...")
            init_db()
            migrate_db()
            print(">>> Database initialization/migration completed.")
            _db_initialized = True
        except Exception as e:
            print(f">>> CRITICAL: Startup initialization failed: {e}")
            # We don't block the request, but log the failure
            _db_initialized = True 

if __name__ == '__main__':
    # For local development
    print(">>> Starting Flask development server...")
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
