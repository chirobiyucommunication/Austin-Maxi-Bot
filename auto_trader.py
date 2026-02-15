"""
Auto-Trader - Executes trades on Pocket Option using browser automation
Uses Playwright to interact with Pocket Option web platform
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Page, Browser
from config import (
    POCKET_OPTION_URL,
    POCKET_OPTION_EMAIL,
    POCKET_OPTION_PASSWORD,
    TRADE_AMOUNT,
    MAX_TRADES_PER_DAY,
    MAX_LOSS_LIMIT,
    LOG_TRADES,
    LOG_FILE
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class PocketOptionTrader:
    """Automate trading on Pocket Option"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.logged_in = False
        self.trades_today = 0
        self.loss_today = 0.0
        self.trade_log = self.load_trade_log()
    
    def load_trade_log(self) -> list:
        """Load trade log from file"""
        try:
            with open(LOG_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def save_trade_log(self):
        """Save trade log to file"""
        if LOG_TRADES:
            with open(LOG_FILE, 'w') as f:
                json.dump(self.trade_log, f, indent=2)
    
    async def initialize(self):
        """Initialize Playwright and browser"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=False,  # Show browser for debugging
                args=["--disable-blink-features=AutomationControlled"]
            )
            self.page = await self.browser.new_page()
            logger.info("✅ Browser initialized")
        except Exception as e:
            logger.error(f"❌ Browser initialization failed: {str(e)}")
            raise
    
    async def login(self) -> bool:
        """Login to Pocket Option"""
        try:
            logger.info("🔐 Logging in to Pocket Option...")
            
            await self.page.goto(POCKET_OPTION_URL, wait_until='networkidle')
            
            # Wait for login form
            await self.page.wait_for_selector('input[type="email"]', timeout=10000)
            
            # Fill email
            await self.page.fill('input[type="email"]', POCKET_OPTION_EMAIL)
            
            # Fill password
            await self.page.fill('input[type="password"]', POCKET_OPTION_PASSWORD)
            
            # Click login button
            await self.page.click('button[type="submit"]')
            
            # Wait for dashboard
            await self.page.wait_for_selector('[data-testid="assets"]', timeout=15000)
            
            self.logged_in = True
            logger.info("✅ Successfully logged in")
            return True
        
        except Exception as e:
            logger.error(f"❌ Login failed: {str(e)}")
            self.logged_in = False
            return False
    
    async def select_asset(self, pair: str) -> bool:
        """Select trading asset/pair"""
        try:
            logger.info(f"🎯 Selecting asset: {pair}")
            
            # Click on assets dropdown
            await self.page.click('[data-testid="assets"]')
            
            # Wait for dropdown
            await self.page.wait_for_selector('.asset-item', timeout=5000)
            
            # Search for pair
            search_field = await self.page.query_selector('input.asset-search')
            if search_field:
                await search_field.type(pair)
            
            # Click on the matching asset
            await self.page.click(f'text="{pair}"')
            
            logger.info(f"✅ Asset selected: {pair}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Asset selection failed: {str(e)}")
            return False
    
    async def set_expiration(self, timeframe: str) -> bool:
        """Set trade expiration time"""
        try:
            logger.info(f"⏱️  Setting timeframe: {timeframe}")
            
            # Timeframe mapping
            timeframe_map = {
                "1M": "1",
                "5M": "5",
                "15M": "15",
                "1H": "60",
            }
            
            expiration = timeframe_map.get(timeframe, "1")
            
            # Click expiration selector
            await self.page.click('[data-testid="expiration"]')
            
            # Select timeframe
            await self.page.click(f'[data-value="{expiration}"]')
            
            logger.info(f"✅ Timeframe set: {timeframe}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Timeframe setting failed: {str(e)}")
            return False
    
    async def execute_trade(self, signal: Dict[str, Any]) -> bool:
        """Execute a trade based on signal"""
        try:
            if not self.logged_in:
                if not await self.login():
                    return False
            
            pair = signal['pair']
            direction = signal['direction']
            timeframe = signal['timeframe']
            
            logger.info(f"📊 Executing trade: {pair} {direction} {timeframe}")
            
            # Check limits
            if self.trades_today >= MAX_TRADES_PER_DAY:
                logger.warning(f"⚠️  Max trades per day reached ({MAX_TRADES_PER_DAY})")
                return False
            
            if self.loss_today >= MAX_LOSS_LIMIT:
                logger.warning(f"⚠️  Max loss limit reached (${MAX_LOSS_LIMIT})")
                return False
            
            # Select asset
            if not await self.select_asset(pair):
                return False
            
            # Set expiration
            if not await self.set_expiration(timeframe):
                return False
            
            # Set trade amount
            amount_field = await self.page.query_selector('input[data-testid="amount"]')
            if amount_field:
                await amount_field.clear()
                await amount_field.type(str(TRADE_AMOUNT))
            
            # Click BUY or SELL button
            button_selector = f'button[data-action="{direction.lower()}"]'
            await self.page.click(button_selector)
            
            # Wait for confirmation
            await asyncio.sleep(2)
            
            # Log trade
            trade_record = {
                "timestamp": datetime.now().isoformat(),
                "pair": pair,
                "direction": direction,
                "timeframe": timeframe,
                "amount": TRADE_AMOUNT,
                "status": "executed"
            }
            self.trade_log.append(trade_record)
            self.save_trade_log()
            
            self.trades_today += 1
            logger.info(f"✅ Trade executed: {pair} {direction} (Trade #{self.trades_today})")
            
            return True
        
        except Exception as e:
            logger.error(f"❌ Trade execution failed: {str(e)}")
            return False
    
    async def close(self):
        """Close browser"""
        try:
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            logger.info("✅ Browser closed")
        except Exception as e:
            logger.error(f"Error closing browser: {str(e)}")

async def test_trader():
    """Test the trader"""
    trader = PocketOptionTrader()
    
    try:
        await trader.initialize()
        
        # Test login
        if await trader.login():
            # Test trade
            test_signal = {
                "pair": "EURUSD",
                "direction": "BUY",
                "timeframe": "1M",
                "strength": "STRONG"
            }
            
            await trader.execute_trade(test_signal)
        
    finally:
        await trader.close()

if __name__ == "__main__":
    # Test the trader
    asyncio.run(test_trader())
