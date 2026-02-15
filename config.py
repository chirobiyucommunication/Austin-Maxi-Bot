"""
Configuration file for Austin Maxi Bot
All settings in one place for easy management
"""
import os
from dotenv import load_dotenv

load_dotenv()
# ==== TELEGRAM SETTINGS ====
ADMIN_BOT_TOKEN = os.getenv('ADMIN_BOT_TOKEN', '7963422097:AAFoY3eoqIGHJ6FX0J3D6zM6B21n_v99woA')
CLIENT_BOT_TOKEN = os.getenv('CLIENT_BOT_TOKEN', '8295602848:AAE5ckn6MLztaVexxhgiAzJUbtWWO_nxsso')
ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID', '8273267839'))
USER_CHAT_ID = int(os.getenv('USER_CHAT_ID', '8273267839'))

# ==== SERVER SETTINGS ====
LICENSE_SERVER_URL = os.getenv('LICENSE_SERVER_URL', 'http://localhost:5000')
SIGNAL_SERVER_URL = os.getenv('SIGNAL_SERVER_URL', 'http://localhost:5001')

# ==== POLLING SETTINGS ====
SIGNAL_POLL_INTERVAL = int(os.getenv('SIGNAL_POLL_INTERVAL', '5'))
LICENSE_CHECK_INTERVAL = int(os.getenv('LICENSE_CHECK_INTERVAL', '60'))

# ==== TRADING SETTINGS ====
AUTO_EXECUTE_TRADES = os.getenv('AUTO_EXECUTE_TRADES', 'True').lower() == 'true'
POCKET_OPTION_URL = "https://app.pocketoption.com"
POCKET_OPTION_EMAIL = os.getenv('POCKET_OPTION_EMAIL', 'your_email@example.com')
POCKET_OPTION_PASSWORD = os.getenv('POCKET_OPTION_PASSWORD', 'your_password')

# ==== TRADE EXECUTION SETTINGS ====
TRADE_AMOUNT = float(os.getenv('TRADE_AMOUNT', '10'))
MAX_TRADES_PER_DAY = int(os.getenv('MAX_TRADES_PER_DAY', '20'))
MAX_LOSS_LIMIT = float(os.getenv('MAX_LOSS_LIMIT', '200'))

# ==== SIGNAL STRENGTH FILTER ====
MINIMUM_SIGNAL_STRENGTH = "WEAK"  # Only execute WEAK or STRONG
EXECUTE_ON_STRONG_ONLY = True  # Only execute STRONG signals automatically

# ==== LOGGING ====
DEBUG_MODE = os.getenv('DEBUG_MODE', 'True').lower() == 'true'
LOG_TRADES = os.getenv('LOG_TRADES', 'True').lower() == 'true'
LOG_FILE = "data/trade_log.json"
DEVICES_FILE = "data/licenses.json"
SIGNALS_FILE = "data/signals.json"

# ==== DEVICE SETTINGS ====
DEVICE_ID_FILE = "device_id.txt"
