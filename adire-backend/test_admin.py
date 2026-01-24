
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:5000"
ADMIN_EMAIL = "adireboutique.noreply@gmail.com"
# We know the password from .env reading previously: Crude124@
ADMIN_PASSWORD = "Crude124@"

def test_admin_flow():
    print(f"Testing against {BASE_URL}")

    # 1. Admin Login (Test logic)
    print("\n1. Testing Admin Login...")
    payload = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    try:
        r = requests.post(f"{BASE_URL}/admin/login", json=payload)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.json()}")
    except Exception as e:
        print(f"Login failed: {e}")
        return

    auth_header = {"Authorization": f"Bearer {ADMIN_PASSWORD}"}

    # 2. Add Product
    print("\n2. Testing Add Product...")
    prod_payload = {
        "name": "Test Adire",
        "description": "Test Desc",
        "price": 5000,
        "category": "Test",
        "stock": 10,
        "image_base64": ""
    }
    r = requests.post(f"{BASE_URL}/admin/products", json=prod_payload, headers=auth_header)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.json()}")

    # 3. Get Products
    print("\n3. Testing Get Products...")
    r = requests.get(f"{BASE_URL}/products")
    print(f"Status: {r.status_code}")
    products = r.json()
    print(f"Count: {len(products)}")

    # 4. Create Coupon
    print("\n4. Testing Create Coupon...")
    coupon_payload = {
        "code": "TESTCOUPON",
        "discount": 10,
        "expiry": "2025-12-31"
    }
    r = requests.post(f"{BASE_URL}/admin/coupons", json=coupon_payload, headers=auth_header)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.json()}")

    # 5. Get Coupons
    print("\n5. Testing Get Coupons...")
    r = requests.get(f"{BASE_URL}/admin/coupons", headers=auth_header)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.json()}")
    
    # 6. Reports
    print("\n6. Testing Reports...")
    r = requests.get(f"{BASE_URL}/admin/reports/stats", headers=auth_header)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.json()}")

if __name__ == "__main__":
    test_admin_flow()
