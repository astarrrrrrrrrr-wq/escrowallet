"""
Payment Forwarding Integration for Escrow Bot
This module handles automatic payment forwarding to the escrow wallet
"""

import requests
import json
import time
from datetime import datetime

class PaymentForwarder:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.cryptoapis.io/v2"
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
    
    def create_forwarding_address(self, user_id, deal_id, amount):
        """
        Create a unique forwarding address for a user's deal
        Payments to this address automatically forward to escrow wallet
        """
        endpoint = f"{self.base_url}/blockchain/bitcoin/mainnet/addresses/forwarding"
        
        payload = {
            "context": f"Deal {deal_id} for user {user_id}",
            "data": {
                "callback_url": f"https://your-bot-domain.com/webhook/payment-received",
                "confirmation_count": 1,
                "destination": "0x5a2dD9bFe9cB39F6A1AD806747ce29718b1BfB70",  # Your escrow wallet
                "fee_address": "0x5a2dD9bFe9cB39F6A1AD806747ce29718b1BfB70",  # Optional fee collection
                "fee_percentage": "1.5",  # 1.5% processing fee
                "metadata": {
                    "deal_id": deal_id,
                    "user_id": user_id,
                    "amount": str(amount),
                    "created_at": datetime.now().isoformat()
                }
            }
        }
        
        try:
            response = requests.post(endpoint, headers=self.headers, json=payload)
            if response.status_code == 201:
                data = response.json()
                return {
                    "success": True,
                    "forwarding_address": data["data"]["address"],
                    "reference_id": data["data"]["reference_id"],
                    "qr_code": f"https://chart.googleapis.com/chart?chs=300x300&cht=qr&chl={data['data']['address']}"
                }
            else:
                return {"success": False, "error": response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_forwarding_status(self, reference_id):
        """Check the status of a forwarding address"""
        endpoint = f"{self.base_url}/blockchain/bitcoin/mainnet/addresses/forwarding/{reference_id}"
        
        try:
            response = requests.get(endpoint, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": response.text}
        except Exception as e:
            return {"error": str(e)}

class WebhookHandler:
    """Handle incoming payment notifications"""
    
    @staticmethod
    def verify_webhook(payload, signature, secret):
        """Verify webhook authenticity"""
        import hmac
        import hashlib
        
        expected = hmac.new(
            secret.encode(), 
            payload.encode(), 
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected)
    
    @staticmethod
    def process_payment_webhook(webhook_data):
        """Process incoming payment webhook"""
        try:
            event_type = webhook_data.get("event")
            transaction = webhook_data.get("data", {})
            
            if event_type == "address.coins_received":
                deal_id = transaction.get("metadata", {}).get("deal_id")
                amount = float(transaction.get("amount", 0))
                tx_hash = transaction.get("transaction_id")
                
                return {
                    "deal_id": deal_id,
                    "amount": amount,
                    "tx_hash": tx_hash,
                    "status": "payment_received",
                    "timestamp": transaction.get("timestamp")
                }
            
            elif event_type == "address.coins_forwarded":
                return {
                    "status": "payment_forwarded",
                    "escrow_tx_hash": transaction.get("transaction_id")
                }
            
        except Exception as e:
            return {"error": str(e)}

# Example usage for your bot
def integrate_payment_forwarding():
    """Example integration with your existing bot"""
    
    # Initialize payment forwarder
    forwarder = PaymentForwarder(
        api_key="YOUR_CRYPTO_APIS_KEY",
        api_secret="YOUR_CRYPTO_APIS_SECRET"
    )
    
    # When a deal is created, generate forwarding address
    deal_id = "1754213457"
    user_id = "@username"
    amount = 50  # USDT amount
    
    result = forwarder.create_forwarding_address(user_id, deal_id, amount)
    
    if result["success"]:
        forwarding_address = result["forwarding_address"]
        
        # Send this address to the seller instead of escrow wallet
        message = f"""
        🎯 <b>Direct Payment Address Generated</b>
        
        📍 <b>Send exactly {amount} USDT to:</b>
        <code>{forwarding_address}</code>
        
        ⚡ <b>Auto-Forward:</b> Payments automatically go to escrow
        🔒 <b>Secure:</b> Funds instantly secured in escrow contract
        📊 <b>Real-time:</b> Instant confirmation when payment received
        
        🆔 Deal ID: <code>{deal_id}</code>
        """
        
        return message, forwarding_address
    else:
        return f"Error creating payment address: {result['error']}", None

# Webhook endpoint for Flask app
def setup_webhook_endpoint(app, bot):
    """Add webhook endpoint to your Flask app"""
    
    @app.route('/webhook/payment-received', methods=['POST'])
    def payment_webhook():
        try:
            webhook_data = request.get_json()
            
            # Verify webhook (implement signature verification)
            # if not WebhookHandler.verify_webhook(request.data, request.headers.get('signature'), WEBHOOK_SECRET):
            #     return "Unauthorized", 401
            
            result = WebhookHandler.process_payment_webhook(webhook_data)
            
            if "deal_id" in result:
                # Update deal status in your database
                deal_id = result["deal_id"]
                amount = result["amount"]
                
                # Send confirmation to Telegram
                bot.send_message(
                    chat_id=GROUP_ID,
                    text=f"💰 <b>Payment Received!</b>\n\n"
                         f"🆔 Deal: <code>{deal_id}</code>\n"
                         f"💵 Amount: {amount} USDT\n"
                         f"✅ Auto-forwarded to escrow\n"
                         f"🔗 TX: <code>{result['tx_hash']}</code>",
                    parse_mode='HTML'
                )
            
            return "OK", 200
            
        except Exception as e:
            return f"Error: {str(e)}", 500