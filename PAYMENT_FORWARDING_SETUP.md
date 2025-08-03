# Payment Forwarding Setup Guide

## Overview

Your escrow bot now supports automatic payment forwarding similar to C wallet functionality. Users can send USDT to unique addresses that automatically forward payments to your escrow wallet.

## Features Added

### ✅ Automatic Address Generation
- Unique payment addresses for each deal
- Automatic forwarding to escrow wallet
- QR code generation for mobile wallets

### ✅ Real-time Notifications
- Webhook endpoint for instant payment detection
- Telegram notifications when payments received
- Deal status auto-updates

### ✅ User Commands
- `/directpay DEAL_ID` - Generate direct payment address
- Updated `/help` - Includes new payment features
- Graceful fallback to escrow wallet

## Setup Instructions

### Step 1: Get Crypto APIs Account (Optional)

1. Sign up at https://cryptoapis.io/
2. Get your API key from the dashboard
3. Add environment variable: `CRYPTO_APIS_KEY=your_api_key_here`

### Step 2: Configure Webhook Secret

Add environment variable for webhook security:
```
WEBHOOK_SECRET=your_secure_random_string_here
```

### Step 3: Update Replit App URL

In `main.py`, update line 2542:
```python
"callback_url": "https://YOUR-REPLIT-APP-NAME.replit.app/webhook/payment-received",
```

Replace `YOUR-REPLIT-APP-NAME` with your actual Replit app domain.

## How It Works

### For Users WITHOUT API Key (Current Setup)
- Uses standard escrow wallet: `0x5a2dD9bFe9cB39F6A1AD806747ce29718b1BfB70`
- Manual payment detection via balance monitoring
- All existing functionality continues working

### For Users WITH API Key (Enhanced Setup)
- Generates unique payment addresses per deal
- Automatic forwarding to escrow wallet
- Real-time webhook notifications
- QR codes for easy mobile payments

## User Experience Examples

### Standard Payment (No API Key)
```
🏦 Send USDT to Escrow Wallet:
0x5a2dD9bFe9cB39F6A1AD806747ce29718b1BfB70
🔄 Bot will automatically detect your payment
```

### Direct Payment (With API Key)
```
💫 Direct Payment Address Ready!
📍 Send Payment To:
0xABC123...unique_address
⚡ Auto-Forward: Payments automatically go to escrow
🔗 QR Code: [Click to view QR code]
```

## API Pricing

### Crypto APIs Pricing
- Free tier: 100 requests/hour
- Basic plan: $99/month for 10,000 requests
- Enterprise plans available for high volume

### Cost Breakdown
- Address creation: ~0.1 requests per deal
- Webhook notifications: Free (incoming)
- Payment forwarding: 1.5% fee (configurable)

## Testing

### Test Without API Key
1. Create a deal: `/buy 5` then `/sell 5`
2. Send USDT to escrow wallet
3. Verify bot detects payment automatically

### Test With API Key
1. Add `CRYPTO_APIS_KEY` environment variable
2. Create a deal: `/buy 5` then `/sell 5`
3. Use `/directpay DEAL_ID` to get unique address
4. Send USDT to unique address
5. Verify automatic forwarding and notifications

## Security Features

### Address Verification
- Each address linked to specific deal ID
- Metadata tracking for all transactions
- Automatic deal status updates

### Webhook Security
- HMAC signature verification
- IP whitelisting support
- Rate limiting protection

### Fallback Protection
- Graceful degradation if API unavailable
- Standard escrow wallet always works
- No disruption to existing users

## Troubleshooting

### Common Issues

**"Feature Not Available" Error**
- API key not configured
- Falls back to standard escrow wallet
- No functionality lost

**Webhook Not Receiving**
- Check Replit app URL in code
- Verify webhook secret matches
- Check Crypto APIs dashboard logs

**Address Creation Failed**
- API key invalid or expired
- Rate limit exceeded
- Falls back to escrow wallet

### Debug Commands

Check if payment forwarding is active:
```
/info  # Shows current escrow wallet status
```

Generate direct payment address:
```
/directpay DEAL_ID  # Creates or shows existing address
```

## Integration Benefits

### For Users
- **Easier Payments**: No need to remember escrow wallet
- **Mobile Friendly**: QR codes for quick scanning
- **Real-time Updates**: Instant confirmation notifications
- **Unique Addresses**: Each deal has dedicated payment address

### For Operators
- **Automated Workflow**: Less manual intervention needed
- **Better Tracking**: Each payment linked to specific deal
- **Professional UX**: Modern payment experience
- **Scalable**: Handles multiple concurrent deals

## Next Steps

1. **Test Current Setup**: Verify existing functionality works
2. **Get API Key**: Sign up for Crypto APIs (optional)
3. **Update Config**: Add environment variables
4. **Test Enhanced**: Try direct payment features
5. **Monitor Usage**: Check API usage and costs

The system is designed to work perfectly with or without the payment forwarding API, ensuring no disruption to your current operations while offering enhanced features when configured.