from fastapi import FastAPI, Request, HTTPException
import hmac, hashlib, base64, json
from database import init_db, save_order

app = FastAPI()
init_db()

SHOPIFY_WEBHOOK_SECRET = "e43a4e106cf1e30897e57d16061b534b97a7c33c929b66490671122d18e0e6c1"

@app.post("/webhooks/shopify/orders-create")
async def shopify_orders_create(request: Request):
    raw_body = await request.body()
    hmac_header = request.headers.get("X-Shopify-Hmac-Sha256")

    # ... (Garde ton code de vérification HMAC ici) ...

    order = json.loads(raw_body)
    
    # On récupère l'adresse de livraison
    shipping_addr = order.get("shipping_address", {})
    
    # Extraction du nom complet (Shopify fournit souvent 'name' qui est 'Prénom + Nom')
    # Ou on le reconstruit nous-mêmes pour être sûr :
    first_name = shipping_addr.get("first_name", "")
    last_name = shipping_addr.get("last_name", "")
    full_name = f"{first_name} {last_name}".strip()

    save_order(
        str(order.get("id")),
        order.get("email"),
        order.get("total_weight", 0),
        shipping_addr, # On passe tout le dictionnaire de l'adresse
        full_name      # On ajoute le nom extrait explicitement
    )
    
    return {"status": "stored"}