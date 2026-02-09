import sqlite3
import base64
import os

db_path = 'c:/adire-store/adire-backend/adire.db'
images_dir = 'C:/Users/Mercy akinyemi/.gemini/antigravity/brain/02a6d858-2cea-4595-b485-1ae93684895e'

updates = {
    7: 'blue_black_geometric_adire_mannequin_1769884653297.png',
    8: 'maroon_patterned_adire_mannequin_1769884672062.png',
    9: 'classic_xo_pattern_adire_mannequin_1769884689030.png',
    10: 'gold_black_heritage_adire_mannequin_1769884714585.png',
    11: 'blue_floral_blossom_adire_mannequin_1769884735326.png',
    12: 'maroon_cyan_tribal_adire_mannequin_1769884761989.png'
}

def get_base64(file_path):
    with open(file_path, 'rb') as f:
        return 'data:image/png;base64,' + base64.b64encode(f.read()).decode('utf-8')

conn = sqlite3.connect(db_path)
c = conn.cursor()

for prod_id, filename in updates.items():
    full_path = os.path.join(images_dir, filename)
    if os.path.exists(full_path):
        b64 = get_base64(full_path)
        c.execute("UPDATE products SET image_base64 = ? WHERE id = ?", (b64, prod_id))
        print(f"Updated product {prod_id}")
    else:
        print(f"File not found: {full_path}")

conn.commit()
conn.close()
