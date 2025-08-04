# Escrow Bot Replit Project

## Overview
This project is a sophisticated Telegram marketplace bot designed for automated USDT trading with escrow protection on the Polygon network. Its primary purpose is to provide a secure and efficient platform for users to buy and sell USDT, featuring an automatic order matching system and dual confirmation security for transactions. The bot aims to simplify peer-to-peer cryptocurrency trading by automating the escrow process, enhancing trust and reducing friction in digital asset exchanges.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture
### Core Architecture
- **Backend**: Python with Flask for web server.
- **Bot Framework**: pyTelegramBotAPI for Telegram integration.
- **Blockchain Integration**: Web3.py for Polygon network interaction.
- **Data Storage**: JSON file-based for simplicity (`escrows.json`, `orders.json`, `wallets.json`, `blacklist.json`).
- **Trading Engine**: Automatic order matching and deal creation.

### Key Design Decisions
- **Single-file architecture**: All core functionality in `main.py`.
- **JSON storage**: Lightweight file-based storage for persistence.
- **Polygon Network**: Chosen for its low transaction fees, suitable for frequent USDT transactions.
- **USDT Focus**: Specifically designed for USDT transactions as a widely adopted stablecoin.
- **Marketplace Model**: Implements an order-book style trading system with automatic matching, rather than manual deal creation, to streamline transactions.
- **Dual Confirmation**: Both buyer and seller must confirm actions for secure USDT release.
- **UI/UX**: Utilizes Telegram's messaging capabilities with emoji and HTML formatting for clear, user-specific notifications and a professional user interface.

### Feature Specifications
- **Telegram Bot Interface**: Admin-controlled with specific authorized users, group-based operations, and command handlers for trading, escrow, and user wallet management.
- **Blockchain Integration**: Connects to Polygon RPC, interacts with USDT contract for balance checks and transfers, and manages private keys for escrow operations.
- **Trading & Escrow Management**: Features JSON-based order books, automatic order matching, dual confirmation (`/paid`, `/received`), automatic USDT release, dispute handling with admin intervention, user wallet address management, and a blacklist function.
- **Web Server Component**: Flask server for health checks (`/`, `/health`, `/status`) and uptime monitoring.
- **Deal Workflow**: Comprehensive system for order placement, automatic matching, USDT deposit, fiat transfer, dual confirmation, automatic release, and dispute resolution.
- **Security Features**: Includes admin username verification, private key environment variable protection, group-specific bot operation, blacklist functionality, race condition prevention, multi-tier rate limiting, duplicate order prevention, and enhanced payment verification for fraud detection.

## External Dependencies
### Required Python Packages
- `web3`: For blockchain interaction.
- `pyTelegramBotAPI`: For Telegram bot functionality.
- `flask`: For web server functionality.

### External Services
- **Polygon RPC**: Connection to the Polygon blockchain network.
- **Telegram Bot API**: Platform for bot communication.
- **USDT Contract**: ERC-20 token contract on the Polygon network.
- **Crypto APIs**: Integrated for automatic payment forwarding services.

### Network Dependencies
- Consistent Polygon network connectivity.
- Stable Telegram API access.
- Reliable internet connection for all RPC calls.