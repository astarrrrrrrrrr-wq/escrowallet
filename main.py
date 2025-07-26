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
from web3.middleware.geth_poa import geth_poa_middleware
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
    welcome_msg = (
        "🤖 <b>Welcome to Secure Escrow Bot!</b>\n\n"
        "🛡️ Your trusted intermediary for safe crypto transactions\n\n"
        "📋 <b>Available Commands:</b>\n"
        "🤝 /deal - Start a new escrow deal\n"
        "✅ /confirm - Confirm deal completion\n"
        "💰 /balance - Check escrow wallet balance\n"
        "📊 /status - View deal status\n"
        "📝 /list - List all active deals\n"
        "💡 /help - Show detailed help\n"
        "ℹ️ /info - Bot and wallet information\n\n"
        "🔒 <b>Admin Commands:</b>\n"
        "🚫 /scammer - Report scammer\n"
        "🗂️ /deals - View all deals\n"
        "🚨 /emergency - Emergency refund\n\n"
        "💬 For support, contact our admins!"
    )
    bot.reply_to(message, welcome_msg, parse_mode='HTML')

@bot.message_handler(commands=['help'])
def help_command(message):
    help_msg = (
        "📖 <b>Detailed Help Guide</b>\n\n"
        "🤝 <b>/deal @buyer @seller WALLET_ADDRESS AMOUNT</b>\n"
        "   Start a new escrow transaction\n"
        "   Example: <code>/deal @john @mike 0x123...abc 100</code>\n\n"
        "✅ <b>/confirm TX_ID</b>\n"
        "   Buyer confirms product/service received\n"
        "   Example: <code>/confirm 1234567890</code>\n\n"
        "💰 <b>/balance</b>\n"
        "   Check current escrow wallet balance\n\n"
        "📊 <b>/status TX_ID</b>\n"
        "   Check status of specific transaction\n\n"
        "📝 <b>/list</b>\n"
        "   Show your active transactions\n\n"
        "ℹ️ <b>/info</b>\n"
        "   Display bot and wallet information\n\n"
        "🛡️ <b>Security:</b> All funds are held securely until both parties confirm completion!"
    )
    bot.reply_to(message, help_msg, parse_mode='HTML')

@bot.message_handler(commands=['info'])
def info_command(message):
    balance = get_usdt_balance()
    info_msg = (
        "ℹ️ <b>Escrow Bot Information</b>\n\n"
        "🏦 <b>Escrow Wallet:</b>\n<code>{}</code>\n\n"
        "💰 <b>Current Balance:</b> {} USDT\n"
        "🌐 <b>Network:</b> Polygon (MATIC)\n"
        "🪙 <b>Token:</b> USDT (6 decimals)\n"
        "🔒 <b>Security:</b> Multi-admin controlled\n"
        "⚡ <b>Status:</b> Online & Monitoring\n\n"
        "📞 <b>Need Help?</b> Contact our admins for support!"
    ).format(ESCROW_WALLET, balance)
    bot.reply_to(message, info_msg, parse_mode='HTML')

@bot.message_handler(commands=['balance'])
def balance_command(message):
    balance = get_usdt_balance()
    balance_msg = (
        "💰 <b>Escrow Wallet Balance</b>\n\n"
        "🏦 <b>Address:</b>\n<code>{}</code>\n\n"
        "💵 <b>Current Balance:</b> {} USDT\n"
        "🌐 <b>Network:</b> Polygon\n"
        "⏰ <b>Last Updated:</b> Just now\n\n"
        "✅ All funds are secure and monitored 24/7!"
    ).format(ESCROW_WALLET, balance)
    bot.reply_to(message, balance_msg, parse_mode='HTML')

@bot.message_handler(commands=['status'])
def status_command(message):
    args = message.text.split()[1:]
    if len(args) != 1:
        bot.reply_to(message, "❗ Usage: /status TX_ID\nExample: <code>/status 1234567890</code>", parse_mode='HTML')
        return
    
    tx_id = args[0]
    db = load_db()
    tx = db.get(tx_id)
    
    if not tx:
        bot.reply_to(message, "❌ <b>Transaction not found!</b>\n\nPlease check the TX_ID and try again.", parse_mode='HTML')
        return
    
    status_emoji = {
        "waiting_payment": "⏳",
        "paid": "💰", 
        "completed": "✅",
        "refunded": "🔄"
    }
    
    status_msg = (
        "📊 <b>Transaction Status</b>\n\n"
        "🆔 <b>TX ID:</b> <code>{}</code>\n"
        "💼 <b>Buyer:</b> {}\n"
        "🛒 <b>Seller:</b> {}\n"
        "💵 <b>Amount:</b> {} USDT\n"
        "📍 <b>Status:</b> {} {}\n"
        "🏦 <b>Seller Wallet:</b>\n<code>{}</code>\n\n"
        "⏰ <b>Created:</b> {}"
    ).format(
        tx_id, tx['buyer'], tx['seller'], tx['amount'],
        status_emoji.get(tx['status'], '❓'), tx['status'].replace('_', ' ').title(),
        tx['seller_wallet'], 
        time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(int(tx_id)))
    )
    bot.reply_to(message, status_msg, parse_mode='HTML')

@bot.message_handler(commands=['list'])
def list_command(message):
    username = message.from_user.username
    if not username:
        bot.reply_to(message, "❌ Please set a Telegram username to use this feature.")
        return
    
    db = load_db()
    user_deals = []
    
    for tx_id, tx in db.items():
        if f"@{username}" in [tx['buyer'], tx['seller']]:
            user_deals.append((tx_id, tx))
    
    if not user_deals:
        bot.reply_to(message, 
            "📝 <b>No Active Deals</b>\n\n"
            "You don't have any current escrow transactions.\n"
            "Use /deal to start a new escrow!", 
            parse_mode='HTML'
        )
        return
    
    list_msg = "📝 <b>Your Active Deals</b>\n\n"
    for tx_id, tx in user_deals[-5:]:  # Show last 5 deals
        status_emoji = {"waiting_payment": "⏳", "paid": "💰", "completed": "✅", "refunded": "🔄"}
        role = "💼 Buyer" if f"@{username}" == tx['buyer'] else "🛒 Seller"
        
        list_msg += (
            f"🆔 <code>{tx_id}</code>\n"
            f"{role} | {status_emoji.get(tx['status'], '❓')} {tx['status'].replace('_', ' ').title()}\n"
            f"💵 {tx['amount']} USDT\n"
            f"👥 {tx['buyer']} ↔️ {tx['seller']}\n\n"
        )
    
    list_msg += "📊 Use /status TX_ID for detailed information"
    bot.reply_to(message, list_msg, parse_mode='HTML')

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
        bot.reply_to(message, "🚫 <b>Access Denied!</b>\n\nOnly authorized admins can mark scammers.", parse_mode='HTML')
        return
    
    args = message.text.split()[1:]
    if len(args) != 1:
        bot.reply_to(message, 
            "❗ <b>Usage Error</b>\n\n"
            "📋 <b>Correct format:</b> <code>/scammer @username</code>\n"
            "📝 <b>Example:</b> <code>/scammer @baduser123</code>", 
            parse_mode='HTML'
        )
        return
    
    user = args[0]
    blacklist = load_blacklist()
    if user not in blacklist:
        blacklist.append(user)
        save_blacklist(blacklist)
        bot.reply_to(message, 
            f"🚨 <b>Scammer Alert!</b>\n\n"
            f"⚠️ {user} has been marked as a scammer\n"
            f"🛡️ Escrow will reject all future deals with this user\n"
            f"📊 Total blacklisted users: {len(blacklist)}", 
            parse_mode='HTML'
        )
    else:
        bot.reply_to(message, 
            f"ℹ️ <b>Already Blacklisted</b>\n\n"
            f"{user} is already on the scammer list!", 
            parse_mode='HTML'
        )

@bot.message_handler(commands=['deals'])
def deals_admin(message):
    if not is_admin(message.from_user.username):
        bot.reply_to(message, "🚫 <b>Admin Only Command</b>\n\nThis command is restricted to authorized admins.", parse_mode='HTML')
        return
    
    db = load_db()
    if not db:
        bot.reply_to(message, "📊 <b>No Active Deals</b>\n\nThere are currently no escrow transactions.", parse_mode='HTML')
        return
    
    deals_msg = "🗂️ <b>All Escrow Deals</b>\n\n"
    status_count = {"waiting_payment": 0, "paid": 0, "completed": 0, "refunded": 0}
    
    for tx_id, tx in list(db.items())[-10:]:  # Show last 10 deals
        status_emoji = {"waiting_payment": "⏳", "paid": "💰", "completed": "✅", "refunded": "🔄"}
        status_count[tx.get('status', 'unknown')] += 1
        
        deals_msg += (
            f"🆔 <code>{tx_id}</code>\n"
            f"👥 {tx['buyer']} ↔️ {tx['seller']}\n"
            f"💵 {tx['amount']} USDT | {status_emoji.get(tx['status'], '❓')} {tx['status'].replace('_', ' ').title()}\n\n"
        )
    
    summary = (
        f"\n📈 <b>Summary:</b>\n"
        f"⏳ Waiting Payment: {status_count['waiting_payment']}\n"
        f"💰 Paid: {status_count['paid']}\n"
        f"✅ Completed: {status_count['completed']}\n"
        f"🔄 Refunded: {status_count['refunded']}\n"
        f"📊 Total Deals: {len(db)}"
    )
    
    deals_msg += summary
    bot.reply_to(message, deals_msg, parse_mode='HTML')

@bot.message_handler(commands=['emergency'])
def emergency_refund(message):
    if not is_admin(message.from_user.username):
        bot.reply_to(message, "🚫 <b>Emergency Protocol Access Denied</b>\n\nOnly authorized admins can execute emergency refunds.", parse_mode='HTML')
        return
    
    args = message.text.split()[1:]
    if len(args) != 2:
        bot.reply_to(message, 
            "🚨 <b>Emergency Refund Protocol</b>\n\n"
            "📋 <b>Usage:</b> <code>/emergency TX_ID REFUND_WALLET</code>\n"
            "⚠️ <b>Warning:</b> This will immediately refund the transaction!\n"
            "📝 <b>Example:</b> <code>/emergency 1234567890 0x123...abc</code>", 
            parse_mode='HTML'
        )
        return

    tx_id, refund_wallet = args
    db = load_db()
    tx = db.get(tx_id)
    
    if not tx:
        bot.reply_to(message, 
            "❌ <b>Transaction Not Found</b>\n\n"
            f"No escrow transaction found with ID: <code>{tx_id}</code>", 
            parse_mode='HTML'
        )
        return
        
    if tx["status"] not in ["paid", "waiting_payment"]:
        bot.reply_to(message, 
            f"⚠️ <b>Invalid Status for Refund</b>\n\n"
            f"Transaction status: {tx['status']}\n"
            f"Can only refund 'paid' transactions.", 
            parse_mode='HTML'
        )
        return

    try:
        amount = int(tx["amount"] * (10 ** USDT_DECIMALS))
        nonce = web3.eth.get_transaction_count(Web3.to_checksum_address(ESCROW_WALLET))
        
        bot.reply_to(message, 
            f"🚨 <b>Emergency Refund Initiated</b>\n\n"
            f"🆔 TX ID: <code>{tx_id}</code>\n"
            f"💵 Amount: {tx['amount']} USDT\n"
            f"🏦 Refund to: <code>{refund_wallet}</code>\n"
            f"⏳ Processing blockchain transaction...", 
            parse_mode='HTML'
        )
        
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
        
        db[tx_id]["status"] = "emergency_refunded"
        db[tx_id]["refund_hash"] = web3.to_hex(tx_hash)
        save_db(db)
        
        bot.reply_to(message,
            f"✅ <b>Emergency Refund Completed</b>\n\n"
            f"💸 {tx['amount']} USDT refunded successfully\n"
            f"🔗 <b>Transaction Hash:</b>\n<code>{web3.to_hex(tx_hash)}</code>\n"
            f"👤 <b>Refunded to:</b> {refund_wallet}\n\n"
            f"🛡️ Transaction marked as emergency refunded",
            parse_mode="HTML"
        )
    except Exception as e:
        bot.reply_to(message, 
            f"❌ <b>Emergency Refund Failed</b>\n\n"
            f"Error: {str(e)}\n"
            f"Please try again or contact technical support.", 
            parse_mode='HTML'
        )

@bot.message_handler(commands=['blacklist'])
def view_blacklist(message):
    if not is_admin(message.from_user.username):
        bot.reply_to(message, "🚫 <b>Admin Only Command</b>\n\nThis command is restricted to authorized admins.", parse_mode='HTML')
        return
    
    blacklist = load_blacklist()
    if not blacklist:
        bot.reply_to(message, "📝 <b>Blacklist is Empty</b>\n\nNo users are currently blacklisted.", parse_mode='HTML')
        return
    
    blacklist_msg = f"🚫 <b>Blacklisted Users</b>\n\n"
    for i, user in enumerate(blacklist, 1):
        blacklist_msg += f"{i}. {user}\n"
    
    blacklist_msg += f"\n📊 Total: {len(blacklist)} blacklisted users"
    bot.reply_to(message, blacklist_msg, parse_mode='HTML')

@bot.message_handler(commands=['stats'])
def stats_command(message):
    db = load_db()
    blacklist = load_blacklist()
    balance = get_usdt_balance()
    
    if not db:
        total_deals = 0
        status_count = {"waiting_payment": 0, "paid": 0, "completed": 0, "refunded": 0}
        total_volume = 0
    else:
        total_deals = len(db)
        status_count = {"waiting_payment": 0, "paid": 0, "completed": 0, "refunded": 0}
        total_volume = 0
        
        for tx in db.values():
            status = tx.get('status', 'unknown')
            if status in status_count:
                status_count[status] += 1
            total_volume += tx.get('amount', 0)
    
    stats_msg = (
        "📊 <b>Escrow Bot Statistics</b>\n\n"
        "💼 <b>Deal Summary:</b>\n"
        f"📝 Total Deals: {total_deals}\n"
        f"⏳ Waiting Payment: {status_count['waiting_payment']}\n"
        f"💰 Paid & Active: {status_count['paid']}\n"
        f"✅ Completed: {status_count['completed']}\n"
        f"🔄 Refunded: {status_count['refunded']}\n\n"
        f"💵 <b>Financial:</b>\n"
        f"🏦 Current Balance: {balance} USDT\n"
        f"📈 Total Volume: {total_volume:.2f} USDT\n\n"
        f"🛡️ <b>Security:</b>\n"
        f"🚫 Blacklisted Users: {len(blacklist)}\n"
        f"🔒 Admins: {len(ADMIN_USERNAMES)}\n\n"
        f"⚡ <b>Status:</b> Online & Monitoring 24/7"
    )
    
    bot.reply_to(message, stats_msg, parse_mode='HTML')

# Add a catch-all handler for unknown commands
@bot.message_handler(func=lambda message: message.text.startswith('/'))
def unknown_command(message):
    unknown_msg = (
        "❓ <b>Unknown Command</b>\n\n"
        "📋 <b>Available Commands:</b>\n"
        "🤝 /deal - Start new escrow\n"
        "✅ /confirm - Confirm completion\n"
        "💰 /balance - Check balance\n"
        "📊 /status - Deal status\n"
        "📝 /list - Your deals\n"
        "💡 /help - Detailed help\n"
        "ℹ️ /info - Bot information\n"
        "📊 /stats - Bot statistics\n\n"
        "🔒 <b>Admin Commands:</b>\n"
        "🚫 /scammer - Mark scammer\n"
        "🗂️ /deals - All deals\n"
        "🚨 /emergency - Emergency refund\n"
        "📝 /blacklist - View blacklist\n\n"
        "💬 Need help? Use /help for detailed instructions!"
    )
    bot.reply_to(message, unknown_msg, parse_mode='HTML')

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

@app.route('/health')
def health_check():
    try:
        # Check Web3 connection
        is_connected = web3.is_connected()
        
        # Check USDT balance (verifies blockchain connectivity)
        balance = get_usdt_balance()
        
        # Check if database files exist
        import os
        db_exists = os.path.exists('escrows.json')
        blacklist_exists = os.path.exists('blacklist.json')
        
        if is_connected and balance is not None:
            return {
                "status": "healthy",
                "web3_connected": is_connected,
                "usdt_balance": balance,
                "database_files": {
                    "escrows": db_exists,
                    "blacklist": blacklist_exists
                },
                "timestamp": time.time()
            }, 200
        else:
            return {
                "status": "unhealthy",
                "web3_connected": is_connected,
                "error": "Connection or balance check failed"
            }, 503
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }, 500

@app.route('/status')
def simple_status():
    return "OK", 200

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
