#!/usr/bin/env python3
"""
Quick Pinata IPFS Test Script
Simple test to verify Pinata connection and upload functionality
"""

import json
import os
import sys
import time
from pathlib import Path

# Add modules to path
sys.path.append(str(Path(__file__).parent / "modules"))

from dotenv import load_dotenv


def test_pinata_connection():
    """Test Pinata API connection"""
    print("🔗 Testing Pinata IPFS Connection...")
    print("-" * 40)

    # Load environment variables
    load_dotenv()

    api_key = os.getenv("PINATA_API_KEY")
    secret_key = os.getenv("PINATA_SECRET_API_KEY")
    provider = os.getenv("STORAGE_PROVIDER")

    print(f"📋 Configuration:")
    print(f"   Storage Provider: {provider}")
    print(f"   API Key: {api_key[:10] + '...' if api_key else 'NOT SET'}")
    print(f"   Secret Key: {'SET' if secret_key else 'NOT SET'}")
    print()

    if not api_key or not secret_key:
        print("❌ Pinata API credentials not found!")
        print()
        print("🔧 To fix this:")
        print("1. Go to: https://app.pinata.cloud/developers/api-keys")
        print("2. Sign up for free account")
        print("3. Create API key with full permissions")
        print("4. Update your .env file:")
        print("   PINATA_API_KEY=your_api_key_here")
        print("   PINATA_SECRET_API_KEY=your_secret_key_here")
        print("   STORAGE_PROVIDER=pinata")
        return False

    try:
        # Import and test Pinata client
        from pinata_client import PinataClient

        print("🔧 Initializing Pinata client...")
        client = PinataClient()

        print("🔍 Testing authentication...")
        auth_success = client.test_authentication()

        if auth_success:
            print("✅ Authentication successful!")

            # Get account info
            try:
                account_info = client.get_account_info()
                if account_info:
                    print(f"💰 Account Info:")
                    print(f"   Plan: {account_info.get('plan', 'N/A')}")
                    print(f"   Pin Count: {account_info.get('pin_count', 'N/A')}")
                    print(
                        f"   Pin Size: {account_info.get('pin_size_total', 'N/A')} bytes"
                    )
            except:
                print("ℹ️  Account info not available")

            return True
        else:
            print("❌ Authentication failed!")
            print("   Check your API credentials")
            return False

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you're in the correct directory")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def test_simple_upload():
    """Test simple file upload"""
    print("\n📤 Testing File Upload...")
    print("-" * 40)

    try:
        from pinata_client import PinataClient

        client = PinataClient()

        # Create test content
        test_content = f"Hello from Pinata test! Timestamp: {time.time()}"
        test_bytes = test_content.encode("utf-8")
        filename = f"pinata_test_{int(time.time())}.txt"

        print(f"📄 Uploading test file: {filename}")
        print(f"   Content: {test_content}")
        print(f"   Size: {len(test_bytes)} bytes")

        # Upload file
        cid = client.upload_file(test_bytes, filename)

        print(f"✅ Upload successful!")
        print(f"   CID: {cid}")
        print(f"   IPFS URI: {client.get_ipfs_uri(cid)}")
        print(f"   Gateway URL: {client.get_gateway_url(cid)}")

        # Test JSON upload
        print(f"\n📝 Testing JSON upload...")
        test_json = {
            "name": "Pinata Test NFT",
            "description": "Test NFT metadata for Pinata connection test",
            "test_timestamp": time.time(),
            "attributes": [
                {"trait_type": "Test", "value": "Success"},
                {"trait_type": "Provider", "value": "Pinata IPFS"},
            ],
        }

        json_cid = client.upload_json(test_json, "test_metadata")

        print(f"✅ JSON upload successful!")
        print(f"   CID: {json_cid}")
        print(f"   IPFS URI: {client.get_ipfs_uri(json_cid)}")

        return True

    except Exception as e:
        print(f"❌ Upload test failed: {e}")
        return False


def main():
    """Main test function"""
    print("🚀 Quick Pinata IPFS Test")
    print("=" * 50)

    # Test connection
    connection_ok = test_pinata_connection()

    if not connection_ok:
        print("\n❌ Connection test failed. Fix the issues above and try again.")
        return

    # Test upload
    upload_ok = test_simple_upload()

    # Final results
    print("\n" + "=" * 50)
    if connection_ok and upload_ok:
        print("🎉 ALL TESTS PASSED!")
        print()
        print("✅ Pinata IPFS is working correctly!")
        print("✅ You can now use your Streamlit app with Pinata")
        print()
        print("📋 Next steps:")
        print("1. Run your Streamlit app: streamlit run app.py")
        print("2. Select 'Pinata IPFS' as storage provider")
        print("3. Start uploading your NFTs!")
        print()
        print("🔗 Useful links:")
        print("• Pinata Dashboard: https://app.pinata.cloud/")
        print("• IPFS Gateway: https://gateway.pinata.cloud/ipfs/[CID]")

    else:
        print("⚠️  Some tests failed. Check the errors above.")
        print()
        print("🔧 Common solutions:")
        print("1. Verify your API credentials in .env file")
        print("2. Make sure STORAGE_PROVIDER=pinata")
        print("3. Check your internet connection")
        print("4. Try creating new API keys in Pinata dashboard")


if __name__ == "__main__":
    main()
