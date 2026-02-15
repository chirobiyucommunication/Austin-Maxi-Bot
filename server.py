"""
License Server - Handles device registration and activation
Runs on Render or localhost on port 5000
"""

from flask import Flask, request, jsonify
import json
import os
from datetime import datetime
import uuid

app = Flask(__name__)

LICENSES_FILE = "data/licenses.json"

def load_licenses():
    """Load licenses from JSON file"""
    if os.path.exists(LICENSES_FILE):
        with open(LICENSES_FILE, 'r') as f:
            return json.load(f)
    return {"registered_devices": [], "activated_devices": [], "last_updated": datetime.now().isoformat()}

def save_licenses(data):
    """Save licenses to JSON file"""
    data["last_updated"] = datetime.now().isoformat()
    with open(LICENSES_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/', methods=['GET'])
def home():
    """Health check endpoint"""
    return jsonify({"status": "License Server Running"}), 200

@app.route('/register', methods=['POST'])
def register_device():
    """
    Register a new device
    Request: {"device_id": "unique-device-id"}
    """
    try:
        data = request.json
        device_id = data.get('device_id')
        
        if not device_id:
            return jsonify({"error": "device_id required"}), 400
        
        licenses = load_licenses()
        
        if device_id in licenses["registered_devices"]:
            return jsonify({"message": "Device already registered", "device_id": device_id}), 200
        
        licenses["registered_devices"].append(device_id)
        save_licenses(licenses)
        
        return jsonify({
            "message": "Device registered successfully",
            "device_id": device_id,
            "status": "pending_activation"
        }), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/activate', methods=['POST'])
def activate_device():
    """
    Activate a registered device (Admin only)
    Request: {"device_id": "unique-device-id", "admin_password": "password"}
    """
    try:
        data = request.json
        device_id = data.get('device_id')
        admin_password = data.get('admin_password', '')
        
        # Simple auth - in production, use proper auth
        if admin_password != "ADMIN_SECRET":
            return jsonify({"error": "Unauthorized"}), 401
        
        if not device_id:
            return jsonify({"error": "device_id required"}), 400
        
        licenses = load_licenses()
        
        if device_id not in licenses["registered_devices"]:
            return jsonify({"error": "Device not registered"}), 404
        
        if device_id in licenses["activated_devices"]:
            return jsonify({"message": "Device already activated"}), 200
        
        licenses["activated_devices"].append(device_id)
        save_licenses(licenses)
        
        return jsonify({
            "message": "Device activated successfully",
            "device_id": device_id,
            "status": "active"
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/check/<device_id>', methods=['GET'])
def check_license(device_id):
    """
    Check if a device is licensed
    Returns: {"licensed": true/false, "device_id": "...", "status": "active/inactive/not_found"}
    """
    try:
        licenses = load_licenses()
        
        if device_id not in licenses["registered_devices"]:
            return jsonify({"licensed": False, "device_id": device_id, "status": "not_found"}), 404
        
        if device_id in licenses["activated_devices"]:
            return jsonify({"licensed": True, "device_id": device_id, "status": "active"}), 200
        else:
            return jsonify({"licensed": False, "device_id": device_id, "status": "inactive"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/devices', methods=['GET'])
def list_devices():
    """
    List all registered and activated devices (Admin view)
    """
    try:
        licenses = load_licenses()
        return jsonify(licenses), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/deactivate', methods=['POST'])
def deactivate_device():
    """
    Deactivate a device (Admin only)
    Request: {"device_id": "unique-device-id", "admin_password": "password"}
    """
    try:
        data = request.json
        device_id = data.get('device_id')
        admin_password = data.get('admin_password', '')
        
        if admin_password != "ADMIN_SECRET":
            return jsonify({"error": "Unauthorized"}), 401
        
        licenses = load_licenses()
        
        if device_id in licenses["activated_devices"]:
            licenses["activated_devices"].remove(device_id)
            save_licenses(licenses)
            return jsonify({"message": "Device deactivated"}), 200
        
        return jsonify({"error": "Device not found in activated list"}), 404
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Create data directory if not exists
    os.makedirs('data', exist_ok=True)
    
    # Run on port 5000
    app.run(debug=True, port=5000, host='0.0.0.0')
