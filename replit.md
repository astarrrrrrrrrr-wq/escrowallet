# Escrow Bot Replit Project

## Overview

This is a sophisticated Telegram marketplace bot that provides automated USDT trading with escrow protection. The bot features a complete order matching system where buyers and sellers can post orders, get automatically matched, and complete trades with dual confirmation security on the Polygon network.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Architecture
- **Backend**: Python-based application using Flask for web server functionality
- **Bot Framework**: pyTelegramBotAPI library for Telegram integration
- **Blockchain Integration**: Web3.py for Polygon network interaction
- **Data Storage**: JSON file-based storage for simplicity (escrows.json, orders.json, wallets.json, blacklist.json)
- **Trading Engine**: Automatic order matching and deal creation system

### Key Design Decisions
- **Single-file architecture**: All functionality concentrated in main.py for simplicity
- **JSON storage**: Lightweight file-based storage instead of traditional database
- **Polygon network**: Chosen for low transaction fees compared to Ethereum mainnet
- **USDT focus**: Specifically designed for USDT transactions (most common stablecoin)
- **pyTelegramBotAPI**: Switched from python-telegram-bot for better compatibility and stability
- **Marketplace model**: Order-book style trading with automatic matching instead of manual deal creation
- **Dual confirmation**: Both buyer and seller must confirm before automatic USDT release

## Key Components

### 1. Telegram Bot Interface
- Admin-controlled bot with specific authorized usernames
- Group-based operations (specific GROUP_ID)
- Command handlers for marketplace trading and escrow management
- User wallet management system

### 2. Blockchain Integration
- Web3 connection to Polygon network via RPC
- USDT contract interaction for balance checking and transfers
- Wallet management with private key for escrow operations

### 3. Trading & Escrow Management System
- JSON-based order book (buy_orders, sell_orders)
- Automatic order matching and deal creation
- Dual confirmation system (/paid and /received)
- Automatic USDT release when both parties confirm
- Dispute handling with admin intervention
- User wallet address management
- Blacklist functionality for user management
- Multi-threaded operation support

### 4. Web Server Component
- Flask server for health checks and uptime monitoring
- Multiple monitoring endpoints for external services:
  - `/` - Basic "Escrow bot running" message  
  - `/health` - Comprehensive health check (Web3, balance, files)
  - `/status` - Simple "OK" response for UptimeRobot

## Recent Changes

### July 30, 2025 - Enhanced Security and Trading Limits Update
- **Deal Expiry**: Reduced from 24 hours to 15 minutes for faster deal resolution
- **Trading Limits**: Updated to minimum 5 USDT and maximum 50 USDT per transaction
- **Bot Behavior**: Modified to only respond to specific commands, ignoring unknown messages
- **Implementation**: Updated all time calculations from hours to minutes throughout the system
- **Result**: More focused, secure trading environment with tighter controls
- **Status**: ✅ All changes operational, bot running with enhanced parameters

### July 30, 2025 - Critical Indentation Error Fix
- **Issue**: IndentationError in payment monitoring function preventing app startup
- **Root Cause**: Code after `if deal["status"] == "waiting_usdt_deposit":` was incorrectly indented
- **Solution**: Fixed proper indentation for all code blocks within the conditional statement
- **Result**: App now starts successfully with all systems operational
- **Status**: ✅ Bot running, Web3 connected, payment monitoring active

### July 26, 2025 - Critical Bug Fix: MATIC Balance Issue Resolution
- **Root Cause Identified**: Escrow wallet had 0 MATIC balance, preventing USDT withdrawals
- **Error Symptom**: Users receiving "INTERNAL_ERROR: insufficient funds" when trying to withdraw
- **Comprehensive Solution Implemented**:
  - Added `get_matic_balance()` function to monitor gas fees
  - Enhanced `release_usdt_to_buyer()` with pre-transaction MATIC balance validation
  - Created `check_wallet_balances()` with automatic admin notifications for low MATIC
  - Updated `/balance` command for admins to show both USDT and MATIC balances
  - Added `/forcerelease DEAL_ID` command for manual intervention after MATIC funding
  - Improved error messages with clear instructions for funding the escrow wallet
- **Prevention Measures**: Automated alerts when MATIC balance drops below 0.01 MATIC
- **Admin Tools**: Enhanced balance monitoring and force release capabilities

### July 26, 2025 - Major Marketplace Trading System Implementation
- **Complete system redesign**: Transformed from basic escrow to marketplace-style trading
- **Order book system**: Added `/buy` and `/sell` commands for posting orders
- **Automatic matching**: Bot instantly creates deals when buy/sell orders match amounts
- **Wallet management**: Added `/mywallet` command for users to set USDT delivery addresses
- **Dual confirmation system**: Both `/paid` and `/received` commands required for completion
- **Automatic USDT release**: When both parties confirm, USDT auto-transfers to buyer's wallet
- **Dispute handling**: Added `/notreceived` command to flag payment issues
- **Admin override**: New `/release @user` command for dispute resolution
- **Enhanced user experience**: Added `/orders`, `/mystatus` commands for tracking
- **Database expansion**: Added orders.json and wallets.json for marketplace functionality
- **Professional UI**: Maintained emoji and HTML formatting throughout new commands
- **Comprehensive help**: Updated `/help` command with complete trading workflow guide
- **Enhanced messaging**: Clear escrow wallet address delivery to sellers when deals match
- **User-specific notifications**: Personalized messages for buyers and sellers with role-specific instructions

## Data Flow

1. **Order Placement**: Users post `/buy AMOUNT` or `/sell AMOUNT` orders
2. **Automatic Matching**: Bot matches orders with same amount and creates deals
3. **USDT Deposit**: Seller sends USDT to escrow wallet address
4. **Fiat Transfer**: Buyer sends fiat payment to seller via bank transfer
5. **Dual Confirmation**: Both parties confirm with `/paid` and `/received` commands
6. **Automatic Release**: Bot automatically transfers USDT to buyer's wallet
7. **Dispute Resolution**: Admin intervention with `/release` command if issues arise

## External Dependencies

### Required Python Packages
- `web3`: Blockchain interaction
- `python-telegram-bot`: Telegram bot functionality
- `flask`: Web server for monitoring endpoints

### External Services
- **Polygon RPC**: Blockchain network connection
- **Telegram Bot API**: Bot communication platform
- **USDT Contract**: ERC-20 token contract on Polygon

### Network Dependencies
- Polygon network connectivity
- Telegram API access
- Internet connection for RPC calls

## Deployment Strategy

### Environment Configuration
- Environment variables for sensitive data (BOT_TOKEN, PRIVATE_KEY)
- Hardcoded fallback values for development/testing
- Port 8080 for Flask server (compatible with most hosting platforms)

### File Structure
```
/
├── main.py           # Main application file
├── escrows.json      # Active deals/escrow data storage
├── orders.json       # Buy/sell order book
├── wallets.json      # User wallet addresses
├── blacklist.json    # Blacklisted users
└── attached_assets/  # Additional code snippets/backups
```

### Hosting Considerations
- Designed for platforms like Replit, Heroku, or similar
- Continuous uptime requirement for monitoring blockchain
- Web endpoint for health checks and monitoring services

### Security Features
- Admin username verification
- Private key environment variable protection
- Group-specific bot operation
- Blacklist functionality for user management

## Technical Notes

### Blockchain Configuration
- **Network**: Polygon (MATIC)
- **USDT Contract**: 0xc2132D05D31c914a87C6611C10748AeCB8fA48b6
- **Decimals**: 6 (USDT specific)
- **Middleware**: Geth PoA for Polygon compatibility

### Bot Configuration
- **Admin Users**: Indianarmy_1947, Threethirty330
- **Target Group**: -1002830799357
- **Escrow Wallet**: 0x5a2dD9bFe9cB39F6A1AD806747ce29718b1BfB70

The system is designed for simplicity and reliability, focusing on core escrow functionality while maintaining security through admin controls and blockchain verification.