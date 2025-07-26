import os
import json
import time
import threading
from web3 import Web3

from flask import Flask

import telebot

# === BOT & WALLET CONFIG ===
BOT_TOKEN = os.getenv("BOT_TOKEN", "7705638552:AAHN7YJ-8fB6l_CMp_L9tbZDfNMdpQj2Fc4")
ADMIN_USERNAMES = ["Indianarmy_1947", "Threethirty330","@ASTARR000"]
GROUP_ID = -1002830799357

ESCROW_WALLET = "0x5a2dD9bFe9cB39F6A1AD806747ce29718b1BfB70"
PRIVATE_KEY = os.getenv("PRIVATE_KEY", "26ff32efb7b61a3602cc693b77f824427353f20dccbd4497f25322e3c53fdd4b")

# === POLYGON CONFIG ===
RPC_URL = "https://polygon-rpc.com"
USDT_CONTRACT = "0xc2132d05d31c914a87c6611c10748aeb04b58e8f"
USDT_DECIMALS = 6

# === WEB3 SETUP ===
from web3.middleware import geth_poa_middleware
web3 = Web3(Web3.HTTPProvider(RPC_URL))
web3.middleware_onion.inject(geth_poa_middleware, layer=0)

print("Connected to Web3:", web3.is_connected())

# === USDT CONTRACT ABI ===
abi = json.loads("""
[
    {
        "name": "balanceOf",
        "type": "function",
        "inputs": [
            {
                "name": "account",
                "type": "address"
            }
        ],
        "outputs": [
            {
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view"
    },
    {
        "name": "transfer",
        "type": "function",
        "inputs": [
            {
                "name": "recipient",
                "type": "address"
            },
            {
                "name": "amount",
                "type": "uint256"
            }
        ],
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "stateMutability": "nonpayable"
    }
]
""")

usdt = web3.eth.contract(
    address=Web3.to_checksum_address(USDT_CONTRACT),
    abi=abi
)
print(f"✅ USDT Contract initialized at: {usdt.address}")

# === ESCROW DB ===
DB_FILE = "escrows.json"
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({}, f)

def load_db():
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

# === BLACKLIST DB ===
BLACKLIST_FILE = "blacklist.json"
if not os.path.exists(BLACKLIST_FILE):
    with open(BLACKLIST_FILE, "w") as f:
        json.dump([], f)

def load_blacklist():
    with open(BLACKLIST_FILE, "r") as f:
        return json.load(f)

def save_blacklist(data):
    with open(BLACKLIST_FILE, "w") as f:
        json.dump(data, f, indent=2)

# === TELEGRAM BOT SETUP ===
bot = telebot.TeleBot(BOT_TOKEN)

def is_admin(username):
    return username in ADMIN_USERNAMES

def get_usdt_balance():
    try:
        checksum_address = Web3.to_checksum_address(ESCROW_WALLET)
        web3.eth.get_block('latest')  # Sync
        balance = usdt.functions.balanceOf(checksum_address).call()
        print(f"✅ Fetched raw USDT balance: {balance} (scaled: {balance / (10 ** USDT_DECIMALS)} USDT)")
        return balance / (10 ** USDT_DECIMALS)
    except Exception as e:
        print(f"⚠️ Error fetching balance: {e}")
        return 0

# === BOT COMMAND HANDLERS ===
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🤖 Escrow bot is online and ready!")

@bot.message_handler(commands=['deal'])
def deal(message):
    if message.chat.id != GROUP_ID:
        return
    
    args = message.text.split()[1:]  # Get arguments after /deal
    if len(args) != 4:
        bot.reply_to(message, "❗ Usage: /deal @buyer @seller SELLER_WALLET AMOUNT")
        return

    buyer, seller, seller_wallet, amount = args

    blacklist = load_blacklist()
    if buyer in blacklist or seller in blacklist:
        bot.reply_to(message, "🚫 One of the parties is blacklisted as a scammer. Deal rejected.")
        return

    try:
        amount = float(amount)
    except:
        bot.reply_to(message, "❌ Invalid amount format.")
        return

    tx_id = str(int(time.time()))
    db = load_db()
    db[tx_id] = {
        "buyer": buyer,
        "seller": seller,
        "seller_wallet": seller_wallet,
        "amount": amount,
        "status": "waiting_payment"
    }
    save_db(db)

    bot.reply_to(message,
        f"🤝 <b>Deal Started!</b>\n"
        f"💼 <b>Buyer:</b> {buyer}\n"
        f"🛒 <b>Seller:</b> {seller}\n"
        f"🏷️ <b>Amount:</b> {amount} USDT\n"
        f"📬 <b>Send USDT to Escrow Wallet:</b>\n<code>{ESCROW_WALLET}</code>\n\n"
        f"✅ After sending, confirm with:\n<code>/confirm {tx_id}</code>",
        parse_mode='HTML'
    )

@bot.message_handler(commands=['confirm'])
def confirm(message):
    if message.chat.id != GROUP_ID:
        return
    
    args = message.text.split()[1:]
    if len(args) != 1:
        bot.reply_to(message, "Usage: /confirm TX_ID")
        return

    tx_id = args[0]
    db = load_db()
    tx = db.get(tx_id)
    if not tx:
        bot.reply_to(message, "❌ Invalid TX_ID.")
        return

    if tx["status"] != "paid":
        bot.reply_to(message, "⏳ Escrow not funded or already completed.")
        return

    try:
        amount = int(tx["amount"] * (10 ** USDT_DECIMALS))
        nonce = web3.eth.get_transaction_count(Web3.to_checksum_address(ESCROW_WALLET))
        txn = usdt.functions.transfer(
            Web3.to_checksum_address(tx["seller_wallet"]),
            amount
        ).build_transaction({
            'from': Web3.to_checksum_address(ESCROW_WALLET),
            'gas': 100000,
            'gasPrice': web3.to_wei('30', 'gwei'),
            'nonce': nonce
        })
        signed_txn = web3.eth.account.sign_transaction(txn, PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        db[tx_id]["status"] = "released"
        save_db(db)
        bot.reply_to(message,
            f"✅ USDT released to {tx['seller']}!\n🔗 Tx Hash: <code>{web3.to_hex(tx_hash)}</code>",
            parse_mode="HTML"
        )
    except Exception as e:
        bot.reply_to(message, f"❌ Error releasing payment: {e}")

@bot.message_handler(commands=['dispute'])
def dispute(message):
    if not is_admin(message.from_user.username):
        bot.reply_to(message, "🚫 Only admins can handle disputes.")
        return
    
    args = message.text.split()[1:]
    if len(args) != 2:
        bot.reply_to(message, "Usage: /dispute TX_ID REFUND_WALLET")
        return

    tx_id, refund_wallet = args
    db = load_db()
    tx = db.get(tx_id)
    if not tx:
        bot.reply_to(message, "❌ Invalid TX_ID.")
        return
    if tx["status"] != "paid":
        bot.reply_to(message, "❌ Escrow not in paid status.")
        return

    try:
        amount = int(tx["amount"] * (10 ** USDT_DECIMALS))
        nonce = web3.eth.get_transaction_count(Web3.to_checksum_address(ESCROW_WALLET))
        txn = usdt.functions.transfer(
            Web3.to_checksum_address(refund_wallet),
            amount
        ).build_transaction({
            'from': Web3.to_checksum_address(ESCROW_WALLET),
            'gas': 100000,
            'gasPrice': web3.to_wei('30', 'gwei'),
            'nonce': nonce
        })
        signed_txn = web3.eth.account.sign_transaction(txn, PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        db[tx_id]["status"] = "refunded"
        save_db(db)
        bot.reply_to(message,
            f"💸 Refunded successfully.\n🔗 Tx Hash: <code>{web3.to_hex(tx_hash)}</code>",
            parse_mode="HTML"
        )
    except Exception as e:
        bot.reply_to(message, f"❌ Refund error: {e}")

@bot.message_handler(commands=['scammer'])
def scammer(message):
    if not is_admin(message.from_user.username):
        bot.reply_to(message, "🚫 Only admins can mark scammers.")
        return
    
    args = message.text.split()[1:]
    if len(args) != 1:
        bot.reply_to(message, "Usage: /scammer @username")
        return
    
    user = args[0]
    blacklist = load_blacklist()
    if user not in blacklist:
        blacklist.append(user)
        save_blacklist(blacklist)
        bot.reply_to(message, f"⚠️ {user} marked as a scammer. Escrow will not deal with them.")
    else:
        bot.reply_to(message, "Already blacklisted.")

# === PAYMENT MONITORING ===
def monitor_payments():
    last_balance = get_usdt_balance()
    while True:
        try:
            db = load_db()
            new_balance = get_usdt_balance()
            if new_balance > last_balance:
                diff = new_balance - last_balance
                for tx_id, tx in db.items():
                    if tx["status"] == "waiting_payment" and tx["amount"] <= diff:
                        tx["status"] = "paid"
                        save_db(db)
                        bot.send_message(
                            chat_id=GROUP_ID,
                            text=f"💰 Payment of {tx['amount']} USDT received for TX_ID {tx_id}!\n"
                                 f"{tx['seller']} may now proceed with delivery.\n"
                                 f"{tx['buyer']}, confirm with /confirm {tx_id}"
                        )
                        break
                last_balance = new_balance
        except Exception as e:
            print(f"⚠️ Error in payment monitoring: {e}")
        time.sleep(30)  # Check every 30 seconds

# === FLASK SERVER FOR KEEPALIVE ===
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Escrow bot running."

def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False)

# === MAIN EXECUTION ===
if __name__ == "__main__":
    # Start background threads
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    monitor_thread = threading.Thread(target=monitor_payments, daemon=True)
    monitor_thread.start()

    # Start the bot
    print("🤖 Starting Escrow bot...")
    bot.polling(non_stop=True, interval=0)
    print("🤖 Escrow bot is now running.")
