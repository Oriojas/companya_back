#!/usr/bin/env python3
"""
Test Pinata Connection Script
Simple CLI tool to test your Pinata API connection and credentials
"""

import os
import sys
from datetime import datetime

# Add modules directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "modules"))

try:
    from dotenv import load_dotenv
    from modules.pinata_client import PinataClient
except ImportError as e:
    print(f"❌ Error importing dependencies: {e}")
    print("Make sure to install requirements: pip install -r requirements.txt")
    sys.exit(1)

# Load environment variables
load_dotenv()


def main():
    """Main test function"""
    print("🔧 Testing Pinata IPFS Connection")
    print("=" * 50)

    # Check environment variables
    api_key = os.getenv("PINATA_API_KEY")
    secret_key = os.getenv("PINATA_SECRET_API_KEY")

    if not api_key or not secret_key:
        print("❌ Environment variables not found!")
        print("\nPlease ensure your .env file contains:")
        print("PINATA_API_KEY=your_api_key")
        print("PINATA_SECRET_API_KEY=your_secret_key")
        return False

    print(f"✅ API Key found: {api_key[:10]}...")
    print(f"✅ Secret Key found: {secret_key[:10]}...")
    print()

    try:
        # Initialize client
        print("📡 Initializing Pinata client...")
        client = PinataClient(api_key, secret_key)

        # Test authentication
        print("🔐 Testing authentication...")
        if client.test_authentication():
            print("✅ Authentication successful!")
        else:
            print("❌ Authentication failed!")
            return False

        # Get account info
        print("📊 Getting account information...")
        account_info = client.get_account_info()

        if "error" in account_info:
            print(f"⚠️  Could not get account info: {account_info['error']}")
        else:
            print(f"✅ Pin Count: {account_info.get('pin_count', 'N/A')}")
            print(
                f"✅ Total Pin Size: {account_info.get('pin_size_total', 'N/A')} bytes"
            )

        # Test small JSON upload
        print("\n🧪 Testing JSON upload...")
        test_data = {
            "test": True,
            "timestamp": datetime.now().isoformat(),
            "message": "Connection test successful",
        }

        try:
            cid = client.upload_json(test_data, "connection_test")
            print(f"✅ Test JSON uploaded successfully!")
            print(f"   CID: {cid}")
            print(f"   URI: {client.get_ipfs_uri(cid)}")
            print(f"   Gateway: {client.get_gateway_url(cid)}")

            # Clean up test upload
            print("\n🗑️  Cleaning up test upload...")
            if client.unpin_content(cid):
                print("✅ Test content unpinned successfully")
            else:
                print("⚠️  Could not unpin test content (this is normal)")

        except Exception as e:
            print(f"❌ JSON upload test failed: {e}")
            return False

        print("\n🎉 All tests passed! Your Pinata connection is working correctly.")
        return True

    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
