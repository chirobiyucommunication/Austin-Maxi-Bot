"""
Utility functions for Austin Maxi Bot
"""

import requests
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from config import LICENSE_SERVER_URL, SIGNAL_SERVER_URL

logger = logging.getLogger(__name__)

class LicenseManager:
    """Manage device licensing"""
    
    @staticmethod
    def register_device(device_id: str) -> bool:
        """Register a new device"""
        try:
            response = requests.post(
                f"{LICENSE_SERVER_URL}/register",
                json={"device_id": device_id}
            )
            return response.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return False
    
    @staticmethod
    def check_license(device_id: str) -> Dict[str, Any]:
        """Check if device is licensed"""
        try:
            response = requests.get(f"{LICENSE_SERVER_URL}/check/{device_id}")
            if response.status_code == 200:
                return response.json()
            return {"licensed": False}
        except Exception as e:
            logger.error(f"License check error: {str(e)}")
            return {"licensed": False}

class SignalManager:
    """Manage trading signals"""
    
    @staticmethod
    def send_signal(signal: Dict[str, Any]) -> bool:
        """Send a trading signal"""
        try:
            response = requests.post(
                f"{SIGNAL_SERVER_URL}/signal",
                json=signal
            )
            return response.status_code == 201
        except Exception as e:
            logger.error(f"Signal send error: {str(e)}")
            return False
    
    @staticmethod
    def get_latest_signal() -> Optional[Dict[str, Any]]:
        """Get the latest trading signal"""
        try:
            response = requests.get(f"{SIGNAL_SERVER_URL}/latest")
            if response.status_code == 200:
                data = response.json()
                return data.get('signal')
            return None
        except Exception as e:
            logger.error(f"Signal fetch error: {str(e)}")
            return None
    
    @staticmethod
    def get_signal_history(limit: int = 10) -> list:
        """Get signal history"""
        try:
            response = requests.get(f"{SIGNAL_SERVER_URL}/signals?limit={limit}")
            if response.status_code == 200:
                data = response.json()
                return data.get('signals', [])
            return []
        except Exception as e:
            logger.error(f"Signal history error: {str(e)}")
            return []

class SignalValidator:
    """Validate trading signals"""
    
    REQUIRED_FIELDS = ['pair', 'direction', 'timeframe', 'strength']
    VALID_DIRECTIONS = ['BUY', 'SELL']
    VALID_STRENGTHS = ['WEAK', 'STRONG']
    VALID_TIMEFRAMES = ['1M', '5M', '15M', '30M', '1H', '4H', '1D']
    
    @classmethod
    def validate(cls, signal: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate a signal
        Returns: (is_valid, error_message)
        """
        # Check required fields
        for field in cls.REQUIRED_FIELDS:
            if field not in signal:
                return False, f"Missing required field: {field}"
        
        # Validate direction
        if signal['direction'] not in cls.VALID_DIRECTIONS:
            return False, f"Invalid direction: {signal['direction']}"
        
        # Validate strength
        if signal['strength'] not in cls.VALID_STRENGTHS:
            return False, f"Invalid strength: {signal['strength']}"
        
        # Validate timeframe
        if signal['timeframe'] not in cls.VALID_TIMEFRAMES:
            return False, f"Invalid timeframe: {signal['timeframe']}"
        
        return True, "Valid"

def create_signal(
    pair: str,
    direction: str,
    timeframe: str,
    strength: str,
    entry_price: Optional[float] = None,
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None,
    source: str = "Manual"
) -> Dict[str, Any]:
    """Create a properly formatted signal"""
    
    signal = {
        "pair": pair.upper(),
        "direction": direction.upper(),
        "timeframe": timeframe.upper(),
        "strength": strength.upper(),
        "source": source,
        "timestamp": datetime.now().isoformat()
    }
    
    if entry_price is not None:
        signal["entry_price"] = entry_price
    
    if stop_loss is not None:
        signal["stop_loss"] = stop_loss
    
    if take_profit is not None:
        signal["take_profit"] = take_profit
    
    return signal

def validate_and_send_signal(signal: Dict[str, Any]) -> bool:
    """Validate and send a signal"""
    is_valid, message = SignalValidator.validate(signal)
    
    if not is_valid:
        logger.error(f"Signal validation failed: {message}")
        return False
    
    return SignalManager.send_signal(signal)

class TradeLogger:
    """Log trades to file"""
    
    def __init__(self, filename: str = "data/trade_log.json"):
        self.filename = filename
    
    def log_trade(self, trade: Dict[str, Any]):
        """Log a trade"""
        try:
            trades = self.load_trades()
            trades.append({
                **trade,
                "logged_at": datetime.now().isoformat()
            })
            
            with open(self.filename, 'w') as f:
                json.dump(trades, f, indent=2)
        
        except Exception as e:
            logger.error(f"Trade logging error: {str(e)}")
    
    def load_trades(self) -> list:
        """Load trades from log"""
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except Exception as e:
            logger.error(f"Trade loading error: {str(e)}")
            return []
    
    def get_daily_stats(self) -> Dict[str, Any]:
        """Get today's trading statistics"""
        trades = self.load_trades()
        
        today = datetime.now().date()
        today_trades = [
            t for t in trades
            if datetime.fromisoformat(t['logged_at']).date() == today
        ]
        
        return {
            "total_trades": len(today_trades),
            "wins": len([t for t in today_trades if t.get('status') == 'win']),
            "losses": len([t for t in today_trades if t.get('status') == 'loss']),
            "trades": today_trades
        }

# Export main classes
__all__ = [
    'LicenseManager',
    'SignalManager',
    'SignalValidator',
    'TradeLogger',
    'create_signal',
    'validate_and_send_signal'
]
