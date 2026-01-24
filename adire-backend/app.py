from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import sqlite3
import bcrypt
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
import base64

load_dotenv()

app = Flask(__name__)
CORS(app)

ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT'))

DB_NAME = "adire.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        name TEXT,
        verified INTEGER DEFAULT 0,
        verification_code TEXT,
        code_expiry DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price INTEGER NOT NULL,
        image_base64 TEXT,
        category TEXT,
        stock INTEGER DEFAULT 10,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT NOT NULL,
        items TEXT NOT NULL,
        total INTEGER NOT NULL,
        address TEXT,
        phone TEXT,
        status TEXT DEFAULT 'Pending',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS coupons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        discount INTEGER NOT NULL,
        expiry_date DATE,
        status TEXT DEFAULT 'Active',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        user_name TEXT,
        rating INTEGER,
        comment TEXT,
        status TEXT DEFAULT 'Pending',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

init_db()

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
    return jsonify({"message": "Adire backend live!"})

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
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    if c.fetchone():
        conn.close()
        return jsonify({"error": "Email already exists"}), 400

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    verification_code = ''.join(random.choices(string.digits, k=6))
    code_expiry = (datetime.now() + timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S')

    c.execute("INSERT INTO users (email, password, name, verification_code, code_expiry) VALUES (?, ?, ?, ?, ?)",
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
    c.execute("SELECT * FROM users WHERE email = ? AND verification_code = ? AND code_expiry > datetime('now')", (email, code))
    user = c.fetchone()

    if not user:
        conn.close()
        return jsonify({"error": "Invalid or expired code"}), 400

    c.execute("UPDATE users SET verified = 1, verification_code = NULL, code_expiry = NULL WHERE email = ?", (email,))
    conn.commit()
    conn.close()

    return jsonify({
        "message": "Email verified and logged in!",
        "user": {
            "email": email,
            "name": user['name']
        }
    }), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()

    if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return jsonify({"error": "Invalid credentials"}), 401

    if user['verified'] == 0:
        return jsonify({"error": "Email not verified"}), 403

    return jsonify({
        "message": "Login successful",
        "user": {
            "email": email,
            "name": user['name']
        }
    }), 200

@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
        return jsonify({"message": "Admin login OK"}), 200
    else:
        return jsonify({"error": "Invalid admin credentials"}), 401

@app.route('/admin/products', methods=['POST'])
def admin_add_product():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    price = data.get('price')
    image_base64 = data.get('image_base64')
    category = data.get('category')
    stock = data.get('stock', 10)

    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f"Bearer {ADMIN_PASSWORD}":
        return jsonify({"error": "Admin access only"}), 403

    if not name or not price:
        return jsonify({"error": "Name and price required"}), 400

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO products (name, description, price, image_base64, category, stock) VALUES (?, ?, ?, ?, ?, ?)",
              (name, description, price, image_base64, category, stock))
    conn.commit()
    conn.close()

    return jsonify({"message": "Product added successfully"}), 201

@app.route('/products', methods=['GET'])
def get_products():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    products = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(products), 200

@app.route('/track/<int:id>', methods=['GET'])
def track_order(id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, status, phone, created_at FROM orders WHERE id = ?", (id,))
    order = c.fetchone()
    conn.close()
    if order:
        return jsonify(dict(order)), 200
    return jsonify({"error": "Order not found"}), 404

@app.route('/orders/<email>', methods=['GET'])
def get_user_orders(email):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE user_email = ? ORDER BY created_at DESC", (email,))
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
    c.execute("INSERT INTO orders (user_email, items, total, address, phone) VALUES (?, ?, ?, ?, ?)",
              (user_email, items, total, address, phone))
    conn.commit()
    conn.close()

    return jsonify({"message": "Order placed successfully"}), 201

@app.route('/admin/orders', methods=['GET'])
def get_all_orders():
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f"Bearer {ADMIN_PASSWORD}":
        return jsonify({"error": "Admin access only"}), 403

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM orders ORDER BY created_at DESC")
    orders = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(orders), 200

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
    query = f"UPDATE products SET {', '.join(updates)} WHERE id = ?"
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
    c.execute("DELETE FROM products WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Product deleted successfully"}), 200

@app.route('/admin/orders/<int:id>', methods=['PUT'])
def admin_update_order(id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f"Bearer {ADMIN_PASSWORD}":
        return jsonify({"error": "Admin access only"}), 403

    data = request.get_json()
    status = data.get('status')

    if not status:
        return jsonify({"error": "Status required"}), 400

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE orders SET status = ? WHERE id = ?", (status, id))
    conn.commit()
    conn.close()

    return jsonify({"message": "Order status updated successfully"}), 200

# --- Coupon Routes ---
@app.route('/admin/coupons', methods=['GET', 'POST'])
def manage_coupons():
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f"Bearer {ADMIN_PASSWORD}":
        return jsonify({"error": "Admin access only"}), 403

    conn = get_db_connection()
    c = conn.cursor()

    if request.method == 'POST':
        data = request.get_json()
        code = data.get('code')
        discount = data.get('discount')
        expiry = data.get('expiry')
        
        try:
            c.execute("INSERT INTO coupons (code, discount, expiry_date) VALUES (?, ?, ?)", (code, discount, expiry))
            conn.commit()
            return jsonify({"message": "Coupon created!"}), 201
        except sqlite3.IntegrityError:
            return jsonify({"error": "Coupon code already exists"}), 400
        finally:
            conn.close()

    # GET
    c.execute("SELECT * FROM coupons ORDER BY created_at DESC")
    coupons = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(coupons), 200

@app.route('/admin/coupons/<int:id>', methods=['DELETE'])
def delete_coupon(id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f"Bearer {ADMIN_PASSWORD}":
        return jsonify({"error": "Admin access only"}), 403

    conn = get_db_connection()
    conn.execute("DELETE FROM coupons WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Coupon deleted"}), 200

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
    c.execute("SELECT SUM(total) FROM orders WHERE status != 'Cancelled'")
    total_revenue = c.fetchone()[0] or 0
    
    # Orders Count
    c.execute("SELECT COUNT(*) FROM orders")
    total_orders = c.fetchone()[0]
    
    # Products Count
    c.execute("SELECT COUNT(*) FROM products")
    total_products = c.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        "revenue": total_revenue,
        "orders": total_orders,
        "products": total_products
    }), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
