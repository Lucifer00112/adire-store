import sqlite3
import os
import base64

def add_products():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, 'adire-backend', 'adire.db')
    
    images_dir = os.path.join(os.environ['USERPROFILE'], '.gemini', 'antigravity', 'brain', '02a6d858-2cea-4595-b485-1ae93684895e')
    image_files = [
        'uploaded_media_0_1769435146204.jpg',
        'uploaded_media_1_1769435146204.jpg',
        'uploaded_media_2_1769435146204.jpg',
        'uploaded_media_3_1769435146204.jpg',
        'uploaded_media_4_1769435146204.jpg'
    ]

    products = [
        {"name": "Blue & Black Geometric Adire", "category": "Premium Adire", "description": "Beautiful blue, black and white geometric patterns."},
        {"name": "Deep Maroon Patterned Adire", "category": "Premium Adire", "description": "Rich maroon color with intricate circular and cross patterns."},
        {"name": "Classic X-O Pattern Adire", "category": "Premium Adire", "description": "Black and white classic X and O design."},
        {"name": "Gold & Black Heritage Adire", "category": "Premium Adire", "description": "Stunning gold patterns on a dark background."},
        {"name": "Blue Floral Blossom Adire", "category": "Premium Adire", "description": "Elegant blue floral designs on a dark base."}
    ]

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    for i, product in enumerate(products):
        img_path = os.path.join(images_dir, image_files[i])
        if os.path.exists(img_path):
            with open(img_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                image_base64 = f"data:image/jpeg;base64,{encoded_string}"
        else:
            print(f"Image not found: {img_path}")
            image_base64 = ""

        c.execute("INSERT INTO products (name, description, price, image_base64, category, stock) VALUES (?, ?, ?, ?, ?, ?)",
                  (product['name'], product['description'], 0, image_base64, product['category'], 10))
        print(f"Added product: {product['name']}")

    conn.commit()
    conn.close()
    print("All products added successfully.")

if __name__ == "__main__":
    add_products()
