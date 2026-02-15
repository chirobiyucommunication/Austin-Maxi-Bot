# Austin Maxi Bot - Complete Trading Automation System

A full-featured trading automation bot for Pocket Option with license management, signal delivery, and auto-trading capabilities.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Components](#components)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)

---

## ✨ Features

✅ **License System** - Device-based activation for authorized users
✅ **Signal Delivery** - Real-time trading signals via HTTP API
✅ **Telegram Integration** - Admin and user communication
✅ **Auto-Trading** - Browser automation for Pocket Option
✅ **Trade Logging** - Complete trade history and statistics
✅ **Risk Management** - Daily limits and loss controls
✅ **Modular Design** - Easy to extend and customize

---

## 🏗️ Architecture

```
┌─────────────────────┐
│  TradingView / AI   │
└──────────┬──────────┘
           │
           ▼
┌──────────────────────────┐
│   Signal Server (5001)   │ ◄── Receives signals
├──────────────────────────┤
│ /signal (POST)           │
│ /latest (GET)            │
│ signals.json             │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│   Client Bot            │◄── User Device
├──────────────────────────┤
│ ✓ Polls /latest         │
│ ✓ Checks License        │
│ ✓ Sends Notifications   │
│ ✓ Auto-Trades           │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│  Pocket Option Web       │◄── Trade Execution
├──────────────────────────┤
│ Playwright Automation    │
└──────────────────────────┘

┌──────────────────────────┐
│ License Server (5000)    │
├──────────────────────────┤
│ /register (POST)         │
│ /activate (POST)         │
│ /check (GET)             │
│ licenses.json            │
└──────────────────────────┘
        ▲
        │
┌──────────────────────────┐
│  Admin Bot (Telegram)    │◄── Admin Control
├──────────────────────────┤
│ Device Activation        │
│ Signal Testing           │
│ Device Management        │
└──────────────────────────┘
```

---

## 📦 Installation

### Prerequisites

- Python 3.8+
- pip or conda
- Telegram Bot accounts (from @BotFather)
- Pocket Option account
- Render.com account (for hosting) - Optional

### Step 1: Clone/Download

```bash
cd Austin-Maxi-Bot
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium  # For browser automation
```

### Step 4: Configure

Copy and edit the configuration:

```bash
cp config.py config.py
```

Edit `config.py` with your:
- Telegram bot tokens
- Admin/User chat IDs
- Server URLs
- Pocket Option credentials

---

## ⚙️ Configuration

### 1. Telegram Setup

Get your bot tokens from [@BotFather](https://t.me/BotFather):

```python
ADMIN_BOT_TOKEN = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
CLIENT_BOT_TOKEN = "987654:XYZ-ABC1234def-ghI_kl-mn1o2p3q4r5"
```

Get your chat IDs by sending `/start` to your bot, then checking logs.

### 2. License Server Config

```python
LICENSE_SERVER_URL = "http://localhost:5000"  # Local
# OR
LICENSE_SERVER_URL = "https://your-app.onrender.com"  # Production
```

### 3. Signal Server Config

```python
SIGNAL_SERVER_URL = "http://localhost:5001"
```

### 4. Pocket Option Config

```python
POCKET_OPTION_EMAIL = "your@email.com"
POCKET_OPTION_PASSWORD = "yourpassword"
TRADE_AMOUNT = 10  # Amount per trade
```

### 5. Trading Settings

```python
AUTO_EXECUTE_TRADES = True  # False for manual approval
EXECUTE_ON_STRONG_ONLY = True
MAX_TRADES_PER_DAY = 20
MAX_LOSS_LIMIT = 200
```

---

## 🚀 Components

### 1. License Server (`server.py`)

Manages device licensing. Run on Render or localhost:

```bash
python server.py
```

**Endpoints:**
- `POST /register` - Register new device
- `POST /activate` - Activate device (admin only)
- `GET /check/<device_id>` - Check license status
- `GET /devices` - List all devices
- `POST /deactivate` - Deactivate device

**Example:**
```bash
# Register device
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"device_id": "abc123def456"}'

# Activate device (admin)
curl -X POST http://localhost:5000/activate \
  -H "Content-Type: application/json" \
  -d '{"device_id": "abc123def456", "admin_password": "ADMIN_SECRET"}'
```

### 2. Signal Server (`signal_bot.py`)

Delivers trading signals. Run on Render or localhost:

```bash
python signal_bot.py
```

**Endpoints:**
- `POST /signal` - Receive new signal
- `GET /latest` - Get latest signal
- `GET /signals` - Get signal history
- `POST /clear` - Clear signals (admin)

**Example Signal:**
```bash
curl -X POST http://localhost:5001/signal \
  -H "Content-Type: application/json" \
  -d '{
    "pair": "EURUSD",
    "direction": "BUY",
    "timeframe": "1M",
    "strength": "STRONG",
    "entry_price": 1.0850,
    "stop_loss": 1.0840,
    "take_profit": 1.0870,
    "source": "TradingView"
  }'
```

### 3. Admin Bot (`admin_bot.py`)

Manages devices and signals from Telegram:

```bash
python admin_bot.py
```

**Commands:**
- `/start` - Show help
- `/devices` - List all devices
- `/activate <device_id>` - Activate device
- `/deactivate <device_id>` - Deactivate device
- `/pending` - Show pending activations
- `/signal_test` - Send test signal

### 4. Client Bot (`client_bot.py`)

Runs on user device, receives signals:

```bash
python client_bot.py
```

**Commands:**
- `/start` - Show status
- `/status` - Check license and bot status
- `/device` - Show device ID
- `/signals` - View recent signals
- `/manual <BUY/SELL> <PAIR> <STRONG/WEAK>` - Test signal
- `/help` - Show help

### 5. Auto-Trader (`auto_trader.py`)

Executes trades on Pocket Option via browser automation:

```python
from auto_trader import PocketOptionTrader
import asyncio

trader = PocketOptionTrader()

signal = {
    "pair": "EURUSD",
    "direction": "BUY",
    "timeframe": "1M"
}

asyncio.run(trader.execute_trade(signal))
```

### 6. Utilities (`utils.py`)

Helper functions for license, signal, and trade management:

```python
from utils import (
    LicenseManager,
    SignalManager,
    create_signal,
    validate_and_send_signal,
    TradeLogger
)

# Check license
license_status = LicenseManager.check_license("device_id")

# Get latest signal
signal = SignalManager.get_latest_signal()

# Create and send signal
new_signal = create_signal(
    pair="GBPUSD",
    direction="SELL",
    timeframe="5M",
    strength="STRONG"
)
validate_and_send_signal(new_signal)

# Log trades
logger = TradeLogger()
logger.log_trade({"pair": "EURUSD", "direction": "BUY", "profit": 50})

# Get daily stats
stats = logger.get_daily_stats()
```

---

## 🚦 Quick Start

### Local Testing

**Terminal 1 - License Server:**
```bash
python server.py
# Running on http://localhost:5000
```

**Terminal 2 - Signal Server:**
```bash
python signal_bot.py
# Running on http://localhost:5001
```

**Terminal 3 - Admin Bot:**
```bash
python admin_bot.py
# Admin bot is running
```

**Terminal 4 - Client Bot:**
```bash
python client_bot.py
# Client bot connected, Device ID: abc123...
```

### Register & Activate Device

1. Start client bot - it generates a Device ID
2. In admin bot, use: `/activate <device_id>`
3. Client bot receives activation confirmation
4. Send test signal from admin: `/signal_test`
5. Client bot receives and displays the signal

---

## 📡 API Documentation

### License Server API

#### Register Device
```
POST /register
Content-Type: application/json

{
  "device_id": "unique-device-id-123"
}

Response (201):
{
  "message": "Device registered successfully",
  "device_id": "unique-device-id-123",
  "status": "pending_activation"
}
```

#### Activate Device
```
POST /activate
Content-Type: application/json

{
  "device_id": "unique-device-id-123",
  "admin_password": "ADMIN_SECRET"
}

Response (200):
{
  "message": "Device activated successfully",
  "device_id": "unique-device-id-123",
  "status": "active"
}
```

#### Check License
```
GET /check/unique-device-id-123

Response (200):
{
  "licensed": true,
  "device_id": "unique-device-id-123",
  "status": "active"
}
```

### Signal Server API

#### Send Signal
```
POST /signal
Content-Type: application/json

{
  "pair": "EURUSD",
  "direction": "BUY",
  "timeframe": "1M",
  "strength": "STRONG",
  "entry_price": 1.0850,
  "stop_loss": 1.0840,
  "take_profit": 1.0870,
  "source": "TradingView"
}

Response (201):
{
  "message": "Signal received",
  "signal": { ... }
}
```

#### Get Latest Signal
```
GET /latest

Response (200):
{
  "signal": { ... },
  "timestamp": "2026-02-14T10:30:00"
}
```

#### Get Signal History
```
GET /signals?limit=10

Response (200):
{
  "signals": [ ... ],
  "count": 10,
  "last_updated": "2026-02-14T10:30:00"
}
```

---

## 📊 File Structure

```
Austin-Maxi-Bot/
├── server.py              # License server
├── signal_bot.py          # Signal server
├── admin_bot.py           # Admin Telegram bot
├── client_bot.py          # Client Telegram bot
├── auto_trader.py         # Pocket Option automation
├── utils.py               # Utility functions
├── config.py              # Configuration
├── requirements.txt       # Dependencies
├── data/
│   ├── licenses.json      # Device licenses
│   ├── signals.json       # Trading signals
│   └── trade_log.json     # Trade history
└── README.md              # This file
```

---

## 🐛 Troubleshooting

### License Check Fails
- Ensure license server is running: `python server.py`
- Check `LICENSE_SERVER_URL` in config.py
- Verify device is registered: `/devices` in admin bot

### No Signals Received
- Ensure signal server is running: `python signal_bot.py`
- Test with: `/signal_test` in admin bot
- Check `SIGNAL_SERVER_URL` in config.py

### Telegram Bot Not Responding
- Verify bot token is correct
- Check Telegram chat IDs are valid
- Ensure bot is running: `python admin_bot.py` or `python client_bot.py`

### Auto-Trading Not Working
- Check Pocket Option credentials in config.py
- Ensure Playwright is installed: `playwright install chromium`
- Check Pocket Option hasn't changed login process
- See browser window for debugging (headless=False)

### High CPU Usage
- Increase `SIGNAL_POLL_INTERVAL` in config.py
- Increase `LICENSE_CHECK_INTERVAL` in config.py

---

## 🔒 Security Notes

⚠️ **Important:**
- Change `ADMIN_SECRET` in all files
- Never share device IDs
- Use HTTPS for production (Render supports this)
- Keep Pocket Option password secure
- Use environment variables for sensitive data

## 🚀 Deployment to Render

1. Create Render account at render.com
2. Connect GitHub repository
3. Deploy License Server:
   - Service name: `austin-maxi-license`
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn server:app`

4. Deploy Signal Server:
   - Service name: `austin-maxi-signal`
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn signal_bot:app`

5. Update config.py with Render URLs

---

## 📝 License

MIT License - Use freely for personal use

---

## 💡 Tips

- Start with local testing before deploying to Render
- Test all signals with `/signal_test` before using real trades
- Monitor trade log for performance analysis
- Use `/manual` command to test signals without real trades
- Regularly check device activations for security

---

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review bot logs for error messages
3. Test components individually
4. Verify configuration is correct

---

**Last Updated:** February 14, 2026

Happy Trading! 📈
