import sqlite3
from datetime import datetime

DB_NAME = "livraisons.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS commandes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shopify_order_id TEXT UNIQUE,
            email TEXT,
            poids INTEGER,
            adresse_complete TEXT,
            country_code TEXT,
            zip TEXT,
            city TEXT,
            name TEXT,
            date_reception TEXT,
            statut_livraison TEXT DEFAULT 'A TRAITER',
            postnord_tracking TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_order(order_id, email, weight, addr, customer_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # On prépare l'adresse textuelle
    full_addr_text = f"{addr.get('address1')}, {addr.get('zip')} {addr.get('city')}"
    
    cursor.execute('''
        INSERT INTO commandes (
            shopify_order_id, email, poids, adresse_complete, 
            name, country_code, zip, city, date_reception
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        order_id, 
        email, 
        weight, 
        full_addr_text, 
        customer_name, # <--- Ton nouveau paramètre
        addr.get('country_code'), 
        addr.get('zip'), 
        addr.get('city'), 
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

def get_pending_orders():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # Pour accéder aux colonnes par nom
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM commandes WHERE statut_livraison = 'A TRAITER'")
    orders = cursor.fetchall()
    conn.close()
    return orders