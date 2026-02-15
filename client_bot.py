"""
Client Telegram Bot - Runs on user device and receives trading signals
This is the main bot that users interact with
"""

import logging
import time
import threading
import uuid
import json
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from telegram.request import HTTPXRequest
from telegram.request import HTTPXRequest
import requests
from config import (
    CLIENT_BOT_TOKEN, 
    USER_CHAT_ID, 
    LICENSE_SERVER_URL,
    SIGNAL_SERVER_URL,
    SIGNAL_POLL_INTERVAL,
    LICENSE_CHECK_INTERVAL,
    DEBUG_MODE,
    AUTO_EXECUTE_TRADES,
    DEVICE_ID_FILE
)
from utils import LicenseManager

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO if DEBUG_MODE else logging.WARNING
)
logger = logging.getLogger(__name__)

# Global state
license_status = {"active": False, "device_id": None}
last_signal_id = None

def generate_device_id():
    """Generate unique device ID"""
    return str(uuid.uuid4())

def load_device_id():
    """Load or create device ID"""
    if os.path.exists(DEVICE_ID_FILE):
        with open(DEVICE_ID_FILE, 'r') as f:
            return f.read().strip()
    
    device_id = generate_device_id()
    with open(DEVICE_ID_FILE, 'w') as f:
        f.write(device_id)
    
    return device_id

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command - show bot status"""
    message = """
ðŸ¤– Austin Maxi Bot - Trading Automation

ðŸ“Š Status: """
    
    if license_status["active"]:
        message += f"âœ… Licensed\nDevice ID: {license_status['device_id'][:12]}..."
    else:
        message += f"â³ Waiting for License Activation\nDevice ID: {license_status['device_id'][:12]}..."
    
    message += """

Available commands:
/status - Check license and bot status
/device - Show device ID
/signals - Get signal history
/manual <BUY/SELL> <PAIR> <STRENGTH> - Send manual signal
/help - Show help

ðŸ’¡ How it works:
1. Your device is registered and awaits activation by admin
2. Once activated, you'll receive trading signals automatically
3. Signals appear as Telegram notifications
4. If auto-trading is enabled, trades execute automatically
"""
    
    await update.message.reply_text(message)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check bot status"""
    device_id = license_status.get("device_id", "Unknown")
    
    message = "ðŸ” Bot Status\n\n"
    message += f"Device ID: {device_id[:12]}...\n"
    message += f"License: {'âœ… Active' if license_status['active'] else 'â³ Pending'}\n"
    message += f"Auto Trading: {'ðŸŸ¢ Enabled' if AUTO_EXECUTE_TRADES else 'ðŸ”´ Disabled'}\n"
    message += f"Last Check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    await update.message.reply_text(message)

async def device_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show device ID"""
    device_id = license_status.get("device_id", "Unknown")
    
    message = f"""
ðŸ“± Your Device ID:

{device_id}

Share this with your admin to activate your bot.
Admin will use: /activate {device_id[:12]}...

âš ï¸ Keep this ID secret!
"""
    
    await update.message.reply_text(message)

async def get_signals_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get signal history"""
    try:
        response = requests.get(f"{SIGNAL_SERVER_URL}/signals?limit=5")
        data = response.json()
        signals = data.get('signals', [])
        
        if not signals:
            await update.message.reply_text("No signals received yet.")
            return
        
        message = "ðŸ“ˆ Recent Signals (Last 5)\n\n"
        for signal in reversed(signals):
            message += f"ðŸ”¹ {signal['pair']} {signal['direction']}\n"
            message += f"   Timeframe: {signal['timeframe']}\n"
            message += f"   Strength: {'ðŸ’ª STRONG' if signal['strength'] == 'STRONG' else 'âš¡ WEAK'}\n"
            message += f"   Time: {signal['timestamp'][:19]}\n\n"
        
        await update.message.reply_text(message)
    
    except Exception as e:
        await update.message.reply_text(f"âŒ Error: {str(e)}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Help command"""
    help_text = """
ðŸ“š Help

/status - Check bot status and license
/device - Show your unique device ID
/signals - View recent signals
/manual <BUY/SELL> <PAIR> <STRONG/WEAK> - Test a signal

Example: /manual BUY EURUSD STRONG

ðŸ” License System:
- Your device needs to be activated by admin
- Admin runs: /activate <your device id>
- Once active, you'll receive trading signals

ðŸ“Š Signals:
- Signals come from TradingView, AI, or manual input
- Each signal has: pair, direction, timeframe, strength
- Bot automatically notifies you via Telegram

âš™ï¸ Auto Trading:
- If enabled, bot executes trades automatically on Pocket Option
- You can still use YES/IGNORE buttons to approve trades

For more info, contact your admin.
"""
    
    await update.message.reply_text(help_text)

async def manual_signal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a manual signal for testing"""
    if len(context.args) < 3:
        await update.message.reply_text(
            "âŒ Usage: /manual <BUY/SELL> <PAIR> <STRONG/WEAK>\n"
            "Example: /manual BUY EURUSD STRONG"
        )
        return
    
    direction = context.args[0].upper()
    pair = context.args[1].upper()
    strength = context.args[2].upper()
    
    if direction not in ['BUY', 'SELL']:
        await update.message.reply_text("âŒ Direction must be BUY or SELL")
        return
    
    if strength not in ['STRONG', 'WEAK']:
        await update.message.reply_text("âŒ Strength must be STRONG or WEAK")
        return
    
    try:
        signal = {
            "pair": pair,
            "direction": direction,
            "timeframe": "1M",
            "strength": strength,
            "source": "Manual"
        }
        
        response = requests.post(f"{SIGNAL_SERVER_URL}/signal", json=signal)
        
        if response.status_code == 201:
            await update.message.reply_text(f"âœ… Signal sent: {direction} {pair} ({strength})")
        else:
            await update.message.reply_text("âŒ Error sending signal")
    
    except Exception as e:
        await update.message.reply_text(f"âŒ Error: {str(e)}")

def check_license():
    """Background task to check license status"""
    global license_status
    
    device_id = license_status.get("device_id")
    
    try:
        response = requests.get(f"{LICENSE_SERVER_URL}/check/{device_id}")
        
        if response.status_code == 200:
            data = response.json()
            license_status["active"] = data.get("licensed", False)
            
            if license_status["active"]:
                logger.info(f"âœ… License Active for device {device_id[:12]}...")
            else:
                logger.info(f"â³ License Pending for device {device_id[:12]}...")
        else:
            license_status["active"] = False
            logger.warning("License check failed")
    
    except Exception as e:
        logger.error(f"License check error: {str(e)}")

def poll_signals(application: Application):
    """Background task to poll for new signals"""
    global last_signal_id
    
    while True:
        try:
            if not license_status["active"]:
                time.sleep(LICENSE_CHECK_INTERVAL)
                check_license()
                continue
            
            response = requests.get(f"{SIGNAL_SERVER_URL}/latest")
            
            if response.status_code == 200:
                data = response.json()
                signal = data.get('signal')
                
                if signal and signal.get('id') != last_signal_id:
                    last_signal_id = signal.get('id')
                    
                    # Send signal to user
                    message = f"""
ðŸ“ˆ New Trading Signal!

Pair: <b>{signal['pair']}</b>
Direction: <b>{signal['direction']}</b>
Timeframe: {signal['timeframe']}
Strength: {'ðŸ’ª <b>STRONG</b>' if signal['strength'] == 'STRONG' else 'âš¡ WEAK'}
Time: {signal['timestamp'][:19]}

Entry: {signal.get('entry_price', 'N/A')}
SL: {signal.get('stop_loss', 'N/A')}
TP: {signal.get('take_profit', 'N/A')}

Source: {signal.get('source', 'Unknown')}
"""
                    
                    try:
                        if AUTO_EXECUTE_TRADES:
                            keyboard = [
                                [InlineKeyboardButton("âœ… Execute", callback_data="execute_signal"),
                                 InlineKeyboardButton("âŒ Ignore", callback_data="ignore_signal")]
                            ]
                            reply_markup = InlineKeyboardMarkup(keyboard)
                            asyncio.run(
                                application.bot.send_message(
                                    chat_id=USER_CHAT_ID,
                                    text=message,
                                    parse_mode='HTML',
                                    reply_markup=reply_markup
                                )
                            )
                        else:
                            asyncio.run(
                                application.bot.send_message(
                                    chat_id=USER_CHAT_ID,
                                    text=message,
                                    parse_mode='HTML'
                                )
                            )
                    except Exception as e:
                        logger.error(f"Error sending message: {str(e)}")
        
        except Exception as e:
            logger.error(f"Signal polling error: {str(e)}")
        
        time.sleep(SIGNAL_POLL_INTERVAL)

async def signal_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle signal approval/rejection"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "execute_signal":
        await query.edit_message_text(text=query.message.text + "\n\nâœ… Signal execution approved!")
        logger.info("User approved signal execution")
    
    elif query.data == "ignore_signal":
        await query.edit_message_text(text=query.message.text + "\n\nâŒ Signal ignored by user")
        logger.info("User ignored signal")

def main() -> None:
    """Start the bot"""
    import asyncio
    
    # Load or create device ID
    device_id = load_device_id()
    license_status["device_id"] = device_id
    # Ensure device is registered with the license server
    try:
        registered = LicenseManager.register_device(device_id)
        if registered:
            logger.info(f"Device {device_id[:12]}... registered with license server")
        else:
            logger.warning(f"Failed to register device {device_id[:12]}... with license server")
    except Exception as e:
        logger.error(f"Error registering device: {e}")
    
    logger.info(f"ðŸ¤– Client Bot Started")
    logger.info(f"ðŸ“± Device ID: {device_id}")
    
    # Build application
    application = Application.builder().token(CLIENT_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("device", device_command))
    application.add_handler(CommandHandler("signals", get_signals_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("manual", manual_signal))
    application.add_handler(CallbackQueryHandler(signal_callback))
    
    # Start background tasks
    threading.Thread(target=lambda: poll_signals(application), daemon=True).start()
    threading.Thread(target=lambda: (
        check_license(),
        time.sleep(LICENSE_CHECK_INTERVAL)
    ), daemon=True).start()
    
    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    import asyncio
    main()


