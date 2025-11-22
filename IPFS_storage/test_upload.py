#!/usr/bin/env python3
"""
Test Upload Script
Simple script to test file upload functionality and debug issues
"""

import os
import sys
from pathlib import Path

# Add modules directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "modules"))

from dotenv import load_dotenv
from modules.pinata_client import PinataClient

# Load environment variables
load_dotenv()


def create_test_image():
    """Create a simple test image file"""
    try:
        from PIL import Image, ImageDraw

        # Create a simple 100x100 red square
        img = Image.new("RGB", (100, 100), color="red")
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "TEST", fill="white")

        # Save to bytes
        from io import BytesIO

        img_bytes = BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        return img_bytes.getvalue(), "test_image.png"

    except ImportError:
        # Fallback: create a simple text file
        test_content = b"This is a test file for IPFS upload testing"
        return test_content, "test_file.txt"


def test_upload():
    """Test the upload functionality"""
    print("🧪 Testing IPFS Upload Functionality")
    print("=" * 50)

    try:
        # Initialize client
        print("1. Initializing Pinata client...")
        client = PinataClient()

        # Test authentication
        print("2. Testing authentication...")
        if not client.test_authentication():
            print("❌ Authentication failed!")
            return False

        print("✅ Authentication successful")

        # Create test file
        print("3. Creating test file...")
        file_bytes, filename = create_test_image()

        print(f"✅ Test file created: {filename} ({len(file_bytes)} bytes)")

        # Upload file
        print("4. Uploading to IPFS...")
        cid = client.upload_file(
            file_bytes=file_bytes,
            filename=filename,
            metadata={"name": "Test Upload", "type": "test"},
        )

        # Get URIs
        ipfs_uri = client.get_ipfs_uri(cid)
        gateway_url = client.get_gateway_url(cid)

        print("✅ Upload successful!")
        print(f"   CID: {cid}")
        print(f"   IPFS URI: {ipfs_uri}")
        print(f"   Gateway URL: {gateway_url}")

        # Test JSON upload
        print("5. Testing JSON upload...")
        test_json = {"test": True, "message": "This is a test JSON", "image": ipfs_uri}

        json_cid = client.upload_json(test_json, "test_metadata")
        json_uri = client.get_ipfs_uri(json_cid)
        json_gateway = client.get_gateway_url(json_cid)

        print("✅ JSON upload successful!")
        print(f"   Metadata CID: {json_cid}")
        print(f"   Metadata URI: {json_uri}")
        print(f"   Metadata Gateway: {json_gateway}")

        # Verify uploads
        print("6. Verifying uploads...")
        print(f"   Image gateway: {gateway_url}")
        print(f"   Metadata gateway: {json_gateway}")

        print("\n🎉 All tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main test function"""
    # Check environment
    if not Path(".env").exists():
        print("❌ .env file not found!")
        print("Please copy .env.example to .env and configure your Pinata credentials")
        return

    # Check credentials
    if not os.getenv("PINATA_API_KEY") or not os.getenv("PINATA_SECRET_API_KEY"):
        print("❌ Pinata credentials not found!")
        print("Please configure PINATA_API_KEY and PINATA_SECRET_API_KEY in .env")
        return

    # Run test
    success = test_upload()

    if not success:
        print("\n💡 Troubleshooting tips:")
        print("1. Check your Pinata API credentials")
        print("2. Verify your internet connection")
        print("3. Check if your Pinata account has available quota")
        print("4. Try visiting https://app.pinata.cloud to verify your account")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
