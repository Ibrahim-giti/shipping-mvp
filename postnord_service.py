import os
import requests
import sqlite3

# ==============================
# CONFIGURATION
# ==============================

# Variables d'environnement (OBLIGATOIRE)
POSTNORD_API_KEY = os.getenv("POSTNORD_API_KEY")
POSTNORD_CUSTOMER_ID = os.getenv("POSTNORD_CUSTOMER_ID")

# Base de données SQLite
DB_PATH = "livraisons.db"

# PostNord API
POSTNORD_BASE_URL = "https://api2.postnord.com/rest/shipping/v2"

# ==============================
# DATABASE
# ==============================

def get_order_from_db(order_id):
    """
    Récupère une commande depuis la base SQLite.
    Champs attendus dans la table `commandes` :
    - shopify_order_id
    - name
    - adresse_complete
    - zip
    - city
    - country_code
    - email
    - poids (en grammes)
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM commandes WHERE shopify_order_id = ?",
        (order_id,)
    )

    order = cursor.fetchone()
    conn.close()
    return order

# ==============================
# POSTNORD – CRÉATION EXPÉDITION
# ==============================

def create_postnord_shipment(order):
    url = f"{POSTNORD_BASE_URL}/shipments"

    payload = {
        "customerNumber": POSTNORD_CUSTOMER_ID,
        "service": {
            "code": "19"  # MyPack Collect (à confirmer dans ton contrat)
        },
        "consignee": {
            "name": order["name"],
            "address1": order["adresse_complete"],
            "postcode": order["zip"],
            "city": order["city"],
            "countryCode": order["country_code"],
            "email": order["email"]
        },
        "sender": {
            "name": "Ta Boutique",
            "address1": "Rue du Port",
            "postcode": "75000",
            "city": "Paris",
            "countryCode": "FR"
        },
        "parcels": [
            {
                "weight": order["poids"] / 1000  # grammes → kg
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "apikey": POSTNORD_API_KEY
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code not in (200, 201):
        raise Exception(f"Erreur création expédition PostNord : {response.text}")

    data = response.json()
    return data["shipments"][0]["shipmentId"]

# ==============================
# POSTNORD – QR CODE (MOBILE LABEL)
# ==============================

def get_postnord_mobile_label(shipment_id):
    url = f"{POSTNORD_BASE_URL}/labels/{shipment_id}"

    params = {
        "type": "MOBILE_LABEL",
        "format": "PNG"
    }

    headers = {
        "apikey": POSTNORD_API_KEY
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Erreur récupération QR PostNord : {response.text}")

    data = response.json()
    return data["labels"][0]["url"]

# ==============================
# FONCTION PRINCIPALE
# ==============================

def generate_postnord_qr(order_id):
    if not POSTNORD_API_KEY or not POSTNORD_CUSTOMER_ID:
        raise Exception("Variables d'environnement PostNord manquantes")

    order = get_order_from_db(order_id)
    if not order:
        raise Exception("Commande introuvable dans la base")

    print(f"📦 Création expédition pour {order['name']}...")

    shipment_id = create_postnord_shipment(order)
    print(f"✅ Expédition créée (ID: {shipment_id})")

    qr_url = get_postnord_mobile_label(shipment_id)
    print(f"📱 QR code généré : {qr_url}")

    return qr_url

# ==============================
# TEST MANUEL
# ==============================

if __name__ == "__main__":
    # Remplace par un vrai shopify_order_id présent dans ta DB
    TEST_ORDER_ID = "8209829119"

    try:
        generate_postnord_qr(TEST_ORDER_ID)
    except Exception as e:
        print("❌", e)
