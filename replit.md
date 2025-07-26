# Escrow Bot Replit Project

## Overview

This is a Telegram bot project that provides escrow services for cryptocurrency transactions, specifically for USDT on the Polygon network. The bot acts as an intermediary for peer-to-peer transactions, holding funds in escrow until both parties fulfill their obligations.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Architecture
- **Backend**: Python-based application using Flask for web server functionality
- **Bot Framework**: python-telegram-bot library for Telegram integration
- **Blockchain Integration**: Web3.py for Polygon network interaction
- **Data Storage**: JSON file-based storage for simplicity (escrows.json, blacklist.json)

### Key Design Decisions
- **Single-file architecture**: All functionality concentrated in main.py for simplicity
- **JSON storage**: Lightweight file-based storage instead of traditional database
- **Polygon network**: Chosen for low transaction fees compared to Ethereum mainnet
- **USDT focus**: Specifically designed for USDT transactions (most common stablecoin)
- **pyTelegramBotAPI**: Switched from python-telegram-bot for better compatibility and stability

## Key Components

### 1. Telegram Bot Interface
- Admin-controlled bot with specific authorized usernames
- Group-based operations (specific GROUP_ID)
- Command handlers for escrow management

### 2. Blockchain Integration
- Web3 connection to Polygon network via RPC
- USDT contract interaction for balance checking and transfers
- Wallet management with private key for escrow operations

### 3. Escrow Management System
- JSON-based escrow tracking
- Blacklist functionality for user management
- Multi-threaded operation support

### 4. Web Server Component
- Flask server for health checks and uptime monitoring
- Simple endpoint for external monitoring services

## Data Flow

1. **Escrow Creation**: Admin creates escrow through Telegram commands
2. **Fund Deposit**: Users send USDT to escrow wallet address
3. **Balance Verification**: Bot monitors blockchain for incoming transactions
4. **Escrow Management**: Admin controls release/refund of escrowed funds
5. **Transaction Completion**: Funds transferred to designated recipient

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
├── escrows.json      # Escrow data storage
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