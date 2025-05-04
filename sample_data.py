import sqlite3

conn = sqlite3.connect("inventory.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS inventory (
    name TEXT NOT NULL UNIQUE COLLATE NOCASE,
    quantity INTEGER NOT NULL,
    unit TEXT NOT NULL
)
''')

expanded_data = [
    # Fruits & Vegetables
    ("apples", 50, "kg"),
    ("bananas", 30, "dozen"),
    ("tomatoes", 25, "kg"),
    ("potatoes", 100, "kg"),
    ("onions", 80, "kg"),
    ("carrots", 40, "kg"),
    ("lemons", 15, "kg"),
    
    # Grains & Pulses
    ("rice", 200, "kg"),
    ("wheat", 150, "kg"),
    ("sugar", 90, "kg"),
    ("salt", 50, "kg"),
    ("turmeric powder", 20, "kg"),
    ("lentils", 60, "kg"),
    ("chickpeas", 40, "kg"),

    # Dairy Products
    ("milk", 100, "liters"),
    ("curd", 40, "kg"),
    ("paneer", 20, "kg"),
    ("cheese", 15, "kg"),
    ("butter", 25, "kg"),

    # Beverages
    ("tea powder", 30, "kg"),
    ("coffee", 20, "kg"),
    ("soft drinks", 100, "bottles"),
    ("juices", 50, "bottles"),

    # Snacks
    ("biscuits", 200, "packets"),
    ("chips", 150, "packets"),
    ("namkeen", 80, "packets"),
    ("chocolates", 90, "bars"),
    
    # Cleaning Products
    ("detergent powder", 40, "kg"),
    ("soap", 100, "bars"),
    ("toothpaste", 70, "tubes"),
    ("shampoo", 50, "bottles"),
    ("handwash", 30, "bottles"),

    # Cooking Essentials
    ("cooking oil", 120, "liters"),
    ("ghee", 40, "kg"),
    ("vinegar", 10, "liters"),
    ("soy sauce", 15, "liters"),
    ("spices mix", 25, "kg"),

    # Stationery & Miscellaneous
    ("notebooks", 100, "pieces"),
    ("pens", 200, "pieces"),
    ("matchboxes", 50, "packs"),
    ("candles", 30, "packs"),
    ("tissue papers", 60, "packs")
]

cursor.execute("DELETE FROM inventory") 

cursor.executemany("INSERT OR IGNORE INTO inventory (name, quantity, unit) VALUES (?, ?, ?)", expanded_data)

conn.commit()
conn.close()

print(" Realistic Shop Inventory Database Created Successfully!")

