"""
Admin Telegram Bot - Manages device registration and activation
Admins use this to activate devices sent by client bots
"""

import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.request import HTTPXRequest as Request
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
from telegram.error import NetworkError
import requests
import json
from config import ADMIN_BOT_TOKEN, LICENSE_SERVER_URL, ADMIN_CHAT_ID

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Store pending devices for approval
pending_devices = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command"""
    user_id = update.effective_user.id
    
    # Only admin can use this bot
    if user_id != ADMIN_CHAT_ID:
        await safe_send(context.bot, update.effective_chat.id, "❌ Unauthorized. Only admin can use this bot.")
        return
    
    message = """
🤖 Welcome to Austin Maxi Bot Admin Panel

Available commands:
/start - Show this message
/devices - List all registered and activated devices
/activate <device_id> - Activate a device
/deactivate <device_id> - Deactivate a device
/pending - Show pending device registrations
/help - Show help

When a client bot tries to register, it will appear here with a device ID.
You can then activate it using /activate <device_id>
"""
    await safe_send(context.bot, update.effective_chat.id, message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Help command"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_CHAT_ID:
        await safe_send(context.bot, update.effective_chat.id, "❌ Unauthorized.")
        return
    
    help_text = """
📋 Command Help:

/activate <device_id>
  - Activates a device so it can run
  - Example: /activate abc123def456

/deactivate <device_id>
  - Deactivates a device (stops it from running)
  - Example: /deactivate abc123def456

/devices
  - Shows all registered devices and their status

/pending
  - Shows devices waiting for activation

/signal_test
  - Send a test signal to the signal server
"""
    await safe_send(context.bot, update.effective_chat.id, help_text)

async def list_devices(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all devices"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_CHAT_ID:
        await safe_send(context.bot, update.effective_chat.id, "❌ Unauthorized.")
        return
    
    try:
        response = requests.get(f"{LICENSE_SERVER_URL}/devices")
        data = response.json()
        
        message = "📱 Device List\n\n"
        message += f"Registered: {len(data.get('registered_devices', []))}\n"
        message += f"Activated: {len(data.get('activated_devices', []))}\n\n"
        
        if data.get('registered_devices'):
            message += "✅ Active Devices:\n"
            for device in data.get('activated_devices', []):
                message += f"  • {device}\n"
        
        if len(data.get('registered_devices', [])) > len(data.get('activated_devices', [])):
            message += "\n⏳ Pending Activation:\n"
            for device in data.get('registered_devices', []):
                if device not in data.get('activated_devices', []):
                    message += f"  • {device}\n"
        
        await safe_send(context.bot, update.effective_chat.id, message)
    
    except Exception as e:
        logger.error(f"Error in list_devices: {e}")
        await safe_send(context.bot, update.effective_chat.id, f"❌ Error: {str(e)}")

async def activate_device_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Activate a device"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_CHAT_ID:
        await safe_send(context.bot, update.effective_chat.id, "❌ Unauthorized.")
        return
    
    if not context.args:
        await safe_send(context.bot, update.effective_chat.id, "❌ Usage: /activate <device_id>")
        return
    
    device_id = context.args[0]
    
    try:
        response = requests.post(
            f"{LICENSE_SERVER_URL}/activate",
            json={
                "device_id": device_id,
                "admin_password": "ADMIN_SECRET"
            }
        )
        
        if response.status_code == 200:
            await safe_send(
                context.bot,
                update.effective_chat.id,
                f"✅ Device activated!\n\nDevice ID: {device_id}\nStatus: Active\n\nThe client bot can now receive signals."
            )
        else:
            error = response.json()
            await safe_send(context.bot, update.effective_chat.id, f"❌ Error: {error.get('error', 'Unknown error')}")
    
    except Exception as e:
        logger.error(f"Error in activate_device_command: {e}")
        await safe_send(context.bot, update.effective_chat.id, f"❌ Error: {str(e)}")

async def deactivate_device_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Deactivate a device"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_CHAT_ID:
        await safe_send(context.bot, update.effective_chat.id, "❌ Unauthorized.")
        return
    
    if not context.args:
        await safe_send(context.bot, update.effective_chat.id, "❌ Usage: /deactivate <device_id>")
        return
    
    device_id = context.args[0]
    
    try:
        response = requests.post(
            f"{LICENSE_SERVER_URL}/deactivate",
            json={
                "device_id": device_id,
                "admin_password": "ADMIN_SECRET"
            }
        )
        
        if response.status_code == 200:
            await safe_send(
                context.bot,
                update.effective_chat.id,
                f"✅ Device deactivated!\n\nDevice ID: {device_id}\nStatus: Inactive\n\nThe client bot will no longer receive signals."
            )
        else:
            await safe_send(context.bot, update.effective_chat.id, f"❌ Error: Device not found")
    
    except Exception as e:
        logger.error(f"Error in deactivate_device_command: {e}")
        await safe_send(context.bot, update.effective_chat.id, f"❌ Error: {str(e)}")

async def pending_devices(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show pending devices"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_CHAT_ID:
        await safe_send(context.bot, update.effective_chat.id, "❌ Unauthorized.")
        return
    
    try:
        response = requests.get(f"{LICENSE_SERVER_URL}/devices")
        data = response.json()
        
        registered = set(data.get('registered_devices', []))
        activated = set(data.get('activated_devices', []))
        pending = registered - activated
        
        if not pending:
            await safe_send(context.bot, update.effective_chat.id, "✅ No pending devices!")
            return
        
        message = "⏳ Pending Activation:\n\n"
        for device in pending:
            message += f"📱 {device}\n"
            # Add inline button to activate
            keyboard = [[InlineKeyboardButton("✅ Activate", callback_data=f"activate_{device}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await safe_send(context.bot, update.effective_chat.id, message, reply_markup=reply_markup)
            message = ""
    
    except Exception as e:
        logger.error(f"Error in pending_devices: {e}")
        await safe_send(context.bot, update.effective_chat.id, f"❌ Error: {str(e)}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button clicks"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if user_id != ADMIN_CHAT_ID:
        try:
            await query.answer("❌ Unauthorized")
        except Exception as e:
            logger.debug(f"Failed to answer callback query: {e}")
        return

    try:
        await query.answer()
    except Exception as e:
        logger.debug(f"Failed to answer callback query: {e}")
    
    if query.data.startswith("activate_"):
        device_id = query.data.replace("activate_", "")
        
        try:
            response = requests.post(
                f"{LICENSE_SERVER_URL}/activate",
                json={
                    "device_id": device_id,
                    "admin_password": "ADMIN_SECRET"
                }
            )
            
            if response.status_code == 200:
                try:
                    await query.edit_message_text(
                        f"✅ Device Activated!\n\nDevice: {device_id}\nStatus: Active"
                    )
                except Exception as e:
                    logger.debug(f"Failed to edit callback message: {e}")
            else:
                try:
                    await query.edit_message_text(f"❌ Error: Could not activate device")
                except Exception as e:
                    logger.debug(f"Failed to edit callback message: {e}")
        
        except Exception as e:
            logger.error(f"Error activating device via callback: {e}")
            try:
                await query.edit_message_text(f"❌ Error: {str(e)}")
            except Exception:
                logger.debug("Failed to edit callback message for error")

async def signal_test(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a test signal"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_CHAT_ID:
        await safe_send(context.bot, update.effective_chat.id, "❌ Unauthorized.")
        return
    
    try:
        from config import SIGNAL_SERVER_URL
        
        test_signal = {
            "pair": "EURUSD",
            "direction": "BUY",
            "timeframe": "1M",
            "strength": "STRONG",
            "entry_price": 1.0850,
            "stop_loss": 1.0840,
            "take_profit": 1.0870,
            "source": "AdminTest"
        }
        
        response = requests.post(f"{SIGNAL_SERVER_URL}/signal", json=test_signal)
        
        if response.status_code == 201:
            await safe_send(
                context.bot,
                update.effective_chat.id,
                "✅ Test signal sent!\n\nPair: EURUSD\nDirection: BUY\nStrength: STRONG\n\nClient bots should receive this signal shortly."
            )
        else:
            await safe_send(context.bot, update.effective_chat.id, "❌ Error sending signal")
    
    except Exception as e:
        logger.error(f"Error in signal_test: {e}")
        await safe_send(context.bot, update.effective_chat.id, f"❌ Error: {str(e)}")


async def safe_send(bot: Bot, chat_id: int, text: str, **kwargs):
    """Send a message and handle network errors gracefully."""
    try:
        return await bot.send_message(chat_id=chat_id, text=text, **kwargs)
    except NetworkError as e:
        logger.error(f"NetworkError sending message to {chat_id}: {e}")
    except Exception as e:
        logger.error(f"Error sending message to {chat_id}: {e}")
    return None


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Global error handler to avoid crashes on Telegram API failures."""
    logger.exception("Unhandled exception while processing update")
    try:
        if update and getattr(update, 'effective_chat', None):
            await safe_send(context.bot, update.effective_chat.id, "⚠️ An internal error occurred.")
    except Exception:
        logger.debug("Failed to notify user about the internal error")

def main() -> None:
    """Start the bot"""
    # Use a custom Request with longer timeouts to avoid transient connection timeouts
    # Allow optional proxy via HTTPS_PROXY or HTTP_PROXY environment variables
    proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy') or os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
    if proxy:
        logger.info(f"Using proxy from environment: {proxy}")

    request = Request(
        connection_pool_size=4,
        proxy_url=proxy,
        read_timeout=30,
        write_timeout=30,
        connect_timeout=30,
        pool_timeout=10,
    )

    bot = Bot(token=ADMIN_BOT_TOKEN, request=request)
    application = Application.builder().bot(bot).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("devices", list_devices))
    application.add_handler(CommandHandler("activate", activate_device_command))
    application.add_handler(CommandHandler("deactivate", deactivate_device_command))
    application.add_handler(CommandHandler("pending", pending_devices))
    application.add_handler(CommandHandler("signal_test", signal_test))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    print("🤖 Admin Bot Started!")
    print(f"Admin Chat ID: {ADMIN_CHAT_ID}")
    
    # Start the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
