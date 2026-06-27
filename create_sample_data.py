"""
RetailMart Pvt. Ltd. — Sample Data Generator
Run this file FIRST to create the 3 CSV files needed for the pipeline.
"""

import pandas as pd
import numpy as np

# ─────────────────────────────────────────────
# 1. products.csv
# ─────────────────────────────────────────────
products_data = {
    "product_id": [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
    "product_name": [
        "Basmati Rice 5kg", "Tata Salt 1kg", "Surf Excel 2kg",
        "Amul Butter 500g", "Maggi Noodles 12pk", "Dove Soap 3pk",
        "Coca Cola 2L", "Lay's Chips 200g", "Dettol Handwash 500ml", "Parle-G 800g"
    ],
    "category": [
        "Grocery", "Grocery", "Household", "Dairy",
        "Snacks", "Personal Care", "Beverages", "Snacks",
        "Personal Care", "Snacks"
    ],
    "price": [320.0, 28.0, 210.0, 240.0, 165.0, 95.0, 80.0, 40.0, 115.0, 60.0]
}

df_products = pd.DataFrame(products_data)
df_products.to_csv("products.csv", index=False)
print("✅ products.csv created")

# ─────────────────────────────────────────────
# 2. stores.csv
# ─────────────────────────────────────────────
stores_data = {
    "store_id": [1, 2, 3, 4, 5],
    "store_name": [
        "RetailMart Jodhpur Central", "RetailMart Jaipur Pink",
        "RetailMart Mumbai Andheri", "RetailMart Delhi Connaught",
        "RetailMart Bangalore Koramangala"
    ],
    "city": ["Jodhpur", "Jaipur", "Mumbai", "Delhi", "Bangalore"],
    "region": ["West", "West", "West", "North", "South"]
}

df_stores = pd.DataFrame(stores_data)
df_stores.to_csv("stores.csv", index=False)
print("✅ stores.csv created")

# ─────────────────────────────────────────────
# 3. sales_data.csv  (with intentional mess)
# ─────────────────────────────────────────────
sales_data = {
    "sale_id":    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 3, 7],   # 3 & 7 are duplicates
    "store_id":   [1, 2, 3, 4, 5,  1,  2,  3,  4,  5,  1,  2,  3,  4,  5, 3, 2],
    "product_id": [101,102,103,104,105,106,107,108,109,110,101,103,105,107,109,103,107],
    "quantity":   [2, 3, None, 5, 1, 4, 2, None, 3, 6, 2, 1, 4, None, 2, None, 2],  # some missing
    "sale_date":  [
        "2024-06-01","2024-06-01","2024-06-01","2024-06-01","2024-06-01",
        "2024-06-02","2024-06-02","2024-06-02","2024-06-02","2024-06-02",
        "2024-06-03","2024-06-03","2024-06-03","2024-06-03","2024-06-03",
        "2024-06-01","2024-06-02"  # duplicate rows
    ],
    "amount": [
        640.0, 84.0, None, 1200.0, 165.0,
        380.0, 330.0, None, 345.0, 480.0,
        640.0, 210.0, 660.0, None, 230.0,
        None, 330.0  # some missing
    ]
}

df_sales = pd.DataFrame(sales_data)
df_sales.to_csv("sales_data.csv", index=False)
print("✅ sales_data.csv created (with intentional duplicates and missing values)")
print("\nAll sample data files created! Now run pipeline.py")