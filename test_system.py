"""
Test Script - Verify Austin Maxi Bot Components
Run this to test all components are working correctly
"""

import requests
import json
from datetime import datetime
from config import (
    LICENSE_SERVER_URL,
    SIGNAL_SERVER_URL,
    ADMIN_CHAT_ID,
    USER_CHAT_ID
)

class TestRunner:
    """Run tests for all components"""
    
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
    
    def test(self, name: str, func):
        """Run a test"""
        try:
            result = func()
            status = "✅ PASSED" if result else "❌ FAILED"
            self.results.append(f"{status} - {name}")
            if result:
                self.passed += 1
            else:
                self.failed += 1
        except Exception as e:
            self.results.append(f"❌ ERROR - {name}: {str(e)}")
            self.failed += 1
    
    def report(self):
        """Print test report"""
        print("\n" + "="*50)
        print("Test Results")
        print("="*50 + "\n")
        
        for result in self.results:
            print(result)
        
        print("\n" + "="*50)
        print(f"Passed: {self.passed} | Failed: {self.failed}")
        print("="*50 + "\n")
        
        return self.failed == 0

def test_license_server_health():
    """Test License Server is running"""
    try:
        response = requests.get(f"{LICENSE_SERVER_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

def test_signal_server_health():
    """Test Signal Server is running"""
    try:
        response = requests.get(f"{SIGNAL_SERVER_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

def test_device_registration():
    """Test device registration"""
    try:
        device_id = f"test_device_{datetime.now().timestamp()}"
        response = requests.post(
            f"{LICENSE_SERVER_URL}/register",
            json={"device_id": device_id},
            timeout=5
        )
        return response.status_code in [200, 201]
    except:
        return False

def test_signal_posting():
    """Test posting a signal"""
    try:
        signal = {
            "pair": "EURUSD",
            "direction": "BUY",
            "timeframe": "1M",
            "strength": "STRONG"
        }
        response = requests.post(
            f"{SIGNAL_SERVER_URL}/signal",
            json=signal,
            timeout=5
        )
        return response.status_code == 201
    except:
        return False

def test_signal_retrieval():
    """Test retrieving latest signal"""
    try:
        response = requests.get(
            f"{SIGNAL_SERVER_URL}/latest",
            timeout=5
        )
        return response.status_code == 200
    except:
        return False

def test_device_list():
    """Test listing devices"""
    try:
        response = requests.get(
            f"{LICENSE_SERVER_URL}/devices",
            timeout=5
        )
        return response.status_code == 200
    except:
        return False

def test_config():
    """Test configuration"""
    checks = [
        (ADMIN_CHAT_ID > 0, "Admin Chat ID configured"),
        (USER_CHAT_ID > 0, "User Chat ID configured"),
        (len(LICENSE_SERVER_URL) > 0, "License Server URL configured"),
        (len(SIGNAL_SERVER_URL) > 0, "Signal Server URL configured"),
    ]
    
    print("\n" + "="*50)
    print("Configuration Check")
    print("="*50 + "\n")
    
    all_passed = True
    for check, desc in checks:
        status = "✅" if check else "❌"
        print(f"{status} {desc}")
        if not check:
            all_passed = False
    
    print("\n")
    return all_passed

def main():
    """Run all tests"""
    print("\n" + "="*50)
    print("Austin Maxi Bot - Component Test")
    print("="*50 + "\n")
    
    # Test configuration first
    if not test_config():
        print("⚠️  Configuration issues detected!")
        print("Please update config.py with correct values.\n")
    
    # Run server tests
    runner = TestRunner()
    
    print("Testing servers...\n")
    
    runner.test("License Server Health", test_license_server_health)
    runner.test("Signal Server Health", test_signal_server_health)
    runner.test("Device Registration", test_device_registration)
    runner.test("Signal Posted", test_signal_posting)
    runner.test("Signal Retrieved", test_signal_retrieval)
    runner.test("Device List", test_device_list)
    
    # Print report
    all_passed = runner.report()
    
    if all_passed:
        print("✅ All tests passed! System is ready.\n")
        print("Next steps:")
        print("1. Configure your Telegram bot tokens in config.py")
        print("2. Run admin bot: python admin_bot.py")
        print("3. Run client bot: python client_bot.py")
        print("4. Use /activate <device_id> in admin bot to activate device")
        print("")
    else:
        print("❌ Some tests failed. Check the errors above.\n")
        print("Make sure all servers are running:")
        print("1. python server.py (License Server)")
        print("2. python signal_bot.py (Signal Server)")
        print("")
    
    return all_passed

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
