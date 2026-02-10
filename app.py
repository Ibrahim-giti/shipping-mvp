from fastapi import FastAPI, Request, HTTPException
import hmac
import hashlib
import base64
import json

app = FastAPI()

SHOPIFY_WEBHOOK_SECRET = "e43a4e106cf1e30897e57d16061b534b97a7c33c929b66490671122d18e0e6c1"

def verify_shopify_hmac(data: bytes, hmac_header: str) -> bool:
    digest = hmac.new(
        SHOPIFY_WEBHOOK_SECRET.encode(),
        data,
        hashlib.sha256
    ).digest()

    calculated_hmac = base64.b64encode(digest).decode()
    return hmac.compare_digest(calculated_hmac, hmac_header or "")


@app.post("/webhooks/shopify/orders-create")
async def shopify_orders_create(request: Request):
    raw_body = await request.body()
    hmac_header = request.headers.get("X-Shopify-Hmac-Sha256")

    if not verify_shopify_hmac(raw_body, hmac_header):
        raise HTTPException(status_code=401, detail="Invalid HMAC")

    order = json.loads(raw_body)

    parsed_order = {
        "order_id": order["id"],
        "email": order.get("email"),
        "weight_grams": order.get("total_weight", 0),
        "shipping_address": order.get("shipping_address"),
        "status": "NEW"
    }

    print("NEW ORDER RECEIVED:")
    print(parsed_order)

    return {"ok": True}
