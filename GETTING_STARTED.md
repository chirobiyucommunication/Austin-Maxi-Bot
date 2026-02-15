# Austin Maxi Bot - Getting Started Guide

Welcome to Austin Maxi Bot! This guide will walk you through the setup process step by step.

## 📋 Prerequisites

Before you start, you'll need:

- **Python 3.8+** - [Download here](https://www.python.org/downloads/)
- **Telegram Account** - [telegram.org](https://telegram.org)
- **Two Telegram Bots** - Created via @BotFather
- **Pocket Option Account** - [pocketoption.com](https://pocketoption.com) (Optional for testing)

---

## 🚀 Step 1: Create Telegram Bots

1. Open Telegram and find **@BotFather**
2. Send `/start` then `/newbot`
3. Give your bot a name (e.g., "MyAdminBot")
4. Give your bot a username (e.g., "my_admin_bot")
5. Copy the token - Save this!

**Repeat for a second bot (Client Bot)**

You now have:
- `ADMIN_BOT_TOKEN` - For device management
- `CLIENT_BOT_TOKEN` - For user/trading

---

## 🔑 Step 2: Get Your Chat ID

1. Start the bot you just created
2. Send `/start` to the bot
3. Check the bot's logs to find your Chat ID (you'll see it when we run the bot)

Or use this method:
1. Message [@userinfobot](https://t.me/userinfobot)
2. Your user ID will be displayed

Save this as your `ADMIN_CHAT_ID` (and `USER_CHAT_ID` if different)

---

## 📦 Step 3: Install Austin Maxi Bot

### Windows

```bash
# Clone/extract the Austin Maxi Bot folder
cd Austin-Maxi-Bot

# Run the startup script
START_ALL.bat
```

### Mac/Linux

```bash
# Clone/extract the Austin Maxi Bot folder
cd Austin-Maxi-Bot

# Run the startup script
chmod +x start_all.sh
./start_all.sh
```

### Manual Installation

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install Playwright
playwright install chromium
```

---

## ⚙️ Step 4: Configure the Bot

Edit `config.py`:

```python
# Get your tokens from @BotFather
ADMIN_BOT_TOKEN = "YOUR_ADMIN_BOT_TOKEN"
CLIENT_BOT_TOKEN = "YOUR_CLIENT_BOT_TOKEN"

# Your Telegram chat ID (number only)
ADMIN_CHAT_ID = 123456789
USER_CHAT_ID = 123456789

# Trading settings
TRADE_AMOUNT = 10  # Per trade
AUTO_EXECUTE_TRADES = True  # Auto execute or ask for approval
```

---

## ✅ Step 5: Test Everything Works

```bash
# In the Austin-Maxi-Bot folder
python test_system.py
```

You should see:
```
✅ License Server Health
✅ Signal Server Health
✅ Device Registration
✅ Signal Posted
✅ Signal Retrieved
✅ Device List
```

If any fail, make sure servers are running!

---

## 🤖 Step 6: Start the Bot

### Option A: Automatic (Recommended)

**Windows:**
```bash
START_ALL.bat
```

**Mac/Linux:**
```bash
./start_all.sh
```

This starts all services automatically in separate windows.

### Option B: Manual (4 terminals)

**Terminal 1 - License Server:**
```bash
python server.py
```

**Terminal 2 - Signal Server:**
```bash
python signal_bot.py
```

**Terminal 3 - Admin Bot:**
```bash
python admin_bot.py
```

**Terminal 4 - Client Bot:**
```bash
python client_bot.py
```

---

## 💬 Step 7: First Time Setup

### In your Client Bot chat on Telegram:

Send: `/start`

You'll see:
```
🤖 Austin Maxi Bot - Trading Automation
📱 Device ID: abc123def456...
```

Copy your Device ID!

### In your Admin Bot chat on Telegram:

Send: `/activate abc123def456`

(Replace with your actual Device ID)

You'll see:
```
✅ Device activated!
Device: abc123def456
Status: Active
```

### Back in Client Bot:

Send: `/status`

Should show:
```
License: ✅ Active
```

---

## 💡 Step 8: Test a Trading Signal

In Admin Bot, send:

```
/signal_test
```

In Client Bot, you should immediately receive:
```
📈 New Trading Signal!
Pair: EURUSD
Direction: BUY
Strength: STRONG
```

**Success!** Your bot is working! 🎉

---

## 📊 What Each Bot Does

### Admin Bot Commands
- `/start` - Show help
- `/devices` - List all registered devices
- `/activate <device_id>` - Activate a device
- `/pending` - Show devices waiting activation
- `/signal_test` - Send test signal

### Client Bot Commands
- `/start` - Show status and info
- `/status` - Check license and bot status
- `/device` - Show your device ID
- `/signals` - View recent signals
- `/manual BUY EURUSD STRONG` - Test a signal manually

---

## 🔐 Step 9: Pocket Option Setup (Optional)

For auto-trading to work:

1. Edit `config.py`:

```python
POCKET_OPTION_EMAIL = "your@email.com"
POCKET_OPTION_PASSWORD = "your_password"
TRADE_AMOUNT = 10  # Amount per trade
AUTO_EXECUTE_TRADES = True  # Enable auto trading
```

2. The bot will automatically trade when:
   - License is active
   - Signal strength is STRONG
   - You approve (if enabled)

---

## 📁 File Locations

After starting, you'll have:

- `data/licenses.json` - All registered devices
- `data/signals.json` - All received signals
- `data/trade_log.json` - All executed trades
- `device_id.txt` - Your device's unique ID

Check these files to monitor activity!

---

## 🚀 Next Steps

### Test Locally First
- Keep all services running on localhost
- Send practice signals with `/signal_test`
- Verify trades show in trade_log.json

### Deploy to Production
- See [DEPLOYMENT.md](DEPLOYMENT.md)
- Use Render for 24/7 hosting
- Keep Telegram bots running on your computer

### Integrate with TradingView
- Set up webhook to Signal Server
- Configure alerts to send signals automatically
- See [DEPLOYMENT.md](DEPLOYMENT.md) for webhook format

---

## 🐛 Troubleshooting

### Bot Not Responding
- Check it's running: Look for the terminal window
- Verify bot token is correct in config.py
- Restart the bot

### No Signal Received
- Make sure License is active: Send `/status` in client bot
- Test with `/signal_test` in admin bot
- Check signal server is running

### License Check Fails
- Make sure license server is running (Terminal 1)
- Check Device ID is registered
- Activate device with `/activate <device_id>`

### "Connection refused" errors
- Make sure ALL services are running
- Windows: Check each terminal window
- Mac/Linux: Check `./start_all.sh` started all services

---

## 📞 Getting Help

1. Check the [README.md](README.md) for detailed documentation
2. Review [DEPLOYMENT.md](DEPLOYMENT.md) for advanced setup
3. Look at logs in the terminal windows for error messages
4. Verify config.py has all required values filled in

---

## ✨ Features Unlocked!

Once everything is working:

✅ **Real-time trading signals** - Receive alerts in Telegram
✅ **Auto-trading** - Trades execute automatically on Pocket Option
✅ **License protection** - Only registered devices can trade
✅ **Trade logging** - Track all your trades
✅ **Admin control** - Manage devices and signals

---

## 🎯 Common Next Questions

**Q: Can I run this on a VPS/Server?**
A: Yes! See DEPLOYMENT.md for Render setup.

**Q: Can I add more users?**
A: Yes! Generate device IDs and activate them for each user.

**Q: How do I stop the bot?**
A: Close the terminal windows or press Ctrl+C.

**Q: Is my Pocket Option password safe?**
A: It's stored locally only. For extra security, use environment variables.

**Q: Can I edit the code?**
A: Yes! It's fully open source. See comments in files for guidance.

---

## 🎉 You're All Set!

Your Austin Maxi Bot is now ready to trade!

**Remember:**
- Start small with test signals
- Monitor your trades carefully
- Use risk management settings
- Keep your device ID secret

Happy trading! 📈

---

**Version:** 1.0
**Last Updated:** February 14, 2026
