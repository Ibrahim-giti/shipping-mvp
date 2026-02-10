# Shopify PostNord Delivery QR Automation

Year: 2026

---

## Contents

Main Components:
- main.py (FastAPI server for webhook reception)
- shopify_webhook_handler.py (handling and verification of Shopify webhooks)
- postnord_qr_generator.py (prepares data for QR code generation)

Secondary Components:
- utils.py (utility functions)
- requirements.txt (Python dependencies)

Others:
- this README

---

## Project Description

This project automates the creation of **PostNord delivery QR codes** for Shopify orders.  
The workflow is as follows:

1. A customer places an order on Shopify.  
2. Shopify sends a **webhook** to our application with the order information (email, address, weight, etc.).  
3. The application **verifies the webhook authenticity** using a shared secret (HMAC SHA256).  
4. If the webhook is valid, the order data is extracted and stored.  
5. The data is then ready to automatically generate a **PostNord delivery QR code**, automating the shipping process.  

---

## Command

ngrok http 8000 : launch ngrok 
uvicorn app:app --reload : run the python code
