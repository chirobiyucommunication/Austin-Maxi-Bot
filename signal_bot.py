"""
Signal Server - Delivers trading signals to client bots
Runs on Render or localhost on port 5001
Receives signals from TradingView webhooks, AI, or manual input
"""

from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

SIGNALS_FILE = "data/signals.json"

def load_signals():
    """Load signals from JSON file"""
    if os.path.exists(SIGNALS_FILE):
        with open(SIGNALS_FILE, 'r') as f:
            return json.load(f)
    return {"signals": [], "last_signal": None, "last_updated": datetime.now().isoformat()}

def save_signals(data):
    """Save signals to JSON file"""
    data["last_updated"] = datetime.now().isoformat()
    with open(SIGNALS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/', methods=['GET'])
def home():
    """Health check endpoint"""
    return jsonify({"status": "Signal Server Running"}), 200

@app.route('/signal', methods=['POST'])
def receive_signal():
    """
    Receive a new trading signal
    Request body:
    {
        "pair": "EURUSD",
        "direction": "BUY",
        "timeframe": "1M",
        "strength": "STRONG",
        "entry_price": 1.0850,
        "stop_loss": 1.0840,
        "take_profit": 1.0870,
        "source": "TradingView"  # Optional
    }
    """
    try:
        data = request.json
        
        # Validate required fields
        required = ['pair', 'direction', 'timeframe', 'strength']
        if not all(field in data for field in required):
            return jsonify({"error": f"Missing required fields: {required}"}), 400
        
        # Validate direction
        if data['direction'] not in ['BUY', 'SELL']:
            return jsonify({"error": "direction must be BUY or SELL"}), 400
        
        # Validate strength
        if data['strength'] not in ['WEAK', 'STRONG']:
            return jsonify({"error": "strength must be WEAK or STRONG"}), 400
        
        # Create signal object
        signal = {
            "id": datetime.now().isoformat(),
            "pair": data['pair'],
            "direction": data['direction'],
            "timeframe": data['timeframe'],
            "strength": data['strength'],
            "entry_price": data.get('entry_price'),
            "stop_loss": data.get('stop_loss'),
            "take_profit": data.get('take_profit'),
            "source": data.get('source', 'Manual'),
            "timestamp": datetime.now().isoformat()
        }
        
        signals = load_signals()
        signals["signals"].append(signal)
        signals["last_signal"] = signal
        save_signals(signals)
        
        return jsonify({
            "message": "Signal received",
            "signal": signal
        }), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/latest', methods=['GET'])
def get_latest_signal():
    """
    Get the latest signal
    Response: {"signal": {...}, "timestamp": "..."}
    """
    try:
        signals = load_signals()
        last_signal = signals.get('last_signal')
        
        if not last_signal:
            return jsonify({"signal": None, "message": "No signals yet"}), 200
        
        return jsonify({
            "signal": last_signal,
            "timestamp": signals.get('last_updated')
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/signals', methods=['GET'])
def get_all_signals():
    """
    Get all signals
    Optional query: ?limit=10 (get last 10 signals)
    """
    try:
        limit = request.args.get('limit', type=int, default=None)
        signals = load_signals()
        signal_list = signals.get('signals', [])
        
        if limit:
            signal_list = signal_list[-limit:]
        
        return jsonify({
            "signals": signal_list,
            "count": len(signal_list),
            "last_updated": signals.get('last_updated')
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/signal/<signal_id>', methods=['GET'])
def get_signal(signal_id):
    """
    Get a specific signal by ID (timestamp)
    """
    try:
        signals = load_signals()
        for signal in signals.get('signals', []):
            if signal['id'] == signal_id:
                return jsonify({"signal": signal}), 200
        
        return jsonify({"error": "Signal not found"}), 404
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/clear', methods=['POST'])
def clear_signals():
    """
    Clear all signals (Admin use)
    Request: {"admin_password": "password"}
    """
    try:
        data = request.json or {}
        admin_password = data.get('admin_password', '')
        
        if admin_password != "ADMIN_SECRET":
            return jsonify({"error": "Unauthorized"}), 401
        
        signals = {"signals": [], "last_signal": None, "last_updated": datetime.now().isoformat()}
        save_signals(signals)
        
        return jsonify({"message": "All signals cleared"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    app.run(debug=True, port=5001, host='0.0.0.0')
