#!/usr/bin/env python3
"""
Simple Filecoin Cloud Upload Test Script
Tests basic functionality without complex error handling
"""

import json
import os
import sys
import time
from pathlib import Path

# Add modules to path
sys.path.append(str(Path(__file__).parent / "modules"))

from filecoin_client import FilecoinCloudClient
from metadata_builder import build_nft_metadata


def create_test_image() -> bytes:
    """Create a minimal test PNG image"""
    # Minimal 1x1 pixel PNG (transparent)
    png_data = bytes(
        [
            0x89,
            0x50,
            0x4E,
            0x47,
            0x0D,
            0x0A,
            0x1A,
            0x0A,  # PNG signature
            0x00,
            0x00,
            0x00,
            0x0D,
            0x49,
            0x48,
            0x44,
            0x52,  # IHDR chunk
            0x00,
            0x00,
            0x00,
            0x01,
            0x00,
            0x00,
            0x00,
            0x01,  # 1x1 pixel
            0x08,
            0x06,
            0x00,
            0x00,
            0x00,
            0x1F,
            0x15,
            0xC4,  # RGBA, CRC
            0x89,
            0x00,
            0x00,
            0x00,
            0x0A,
            0x49,
            0x44,
            0x41,  # IDAT chunk
            0x54,
            0x08,
            0x1D,
            0x01,
            0x00,
            0x05,
            0x00,
            0xFA,  # Compressed data
            0xFF,
            0x21,
            0x1A,
            0xD3,
            0xB3,
            0x00,
            0x00,
            0x00,  #
            0x00,
            0x49,
            0x45,
            0x4E,
            0x44,
            0xAE,
            0x42,
            0x60,  # IEND chunk
            0x82,
        ]
    )

    # Pad to meet 127 byte minimum for Filecoin
    if len(png_data) < 127:
        padding = b"\x00" * (127 - len(png_data))
        png_data += padding

    return png_data


def main():
    """Simple test of Filecoin Cloud functionality"""
    print("🚀 Simple Filecoin Cloud Upload Test")
    print("=" * 50)

    # Load environment variables
    from dotenv import load_dotenv

    load_dotenv()

    try:
        # Initialize client
        print("🔧 Initializing Filecoin Cloud client...")
        client = FilecoinCloudClient()

        # Test connection
        print("🔗 Testing connection...")
        auth_success = client.test_authentication()

        if not auth_success:
            print("❌ Authentication failed!")
            return

        print("✅ Connection successful!")

        # Get balance
        print("💰 Checking balance...")
        balance = client.get_balance()
        if "error" not in balance:
            print(f"   USDFC: {balance.get('USDFC', 'N/A')}")
            print(f"   FIL: {balance.get('FIL', 'N/A')}")
        else:
            print(f"   Error: {balance['error']}")

        # Test cost estimation
        print("💰 Testing cost estimation...")
        cost = client.estimate_cost(1024 * 1024, 30)  # 1MB for 30 days
        print(f"   1MB for 30 days: {cost:.6f} USDFC")

        # Create test image
        print("📸 Creating test image...")
        test_image = create_test_image()
        filename = f"test_nft_{int(time.time())}.png"
        print(f"   Size: {len(test_image)} bytes")

        # Upload image
        print("📤 Uploading image to Filecoin Cloud...")
        image_cid = client.upload_file(test_image, filename)
        print(f"✅ Image uploaded!")
        print(f"   CID: {image_cid}")
        print(f"   URI: {client.get_ipfs_uri(image_cid)}")

        # Create metadata
        print("📝 Creating NFT metadata...")
        image_uri = client.get_ipfs_uri(image_cid)

        metadata = build_nft_metadata(
            name="Test NFT Filecoin Cloud",
            description="Test NFT for Filecoin Cloud integration",
            image_uri=image_uri,
            actividad="Testing",
            usuario="System Test",
            acompanante="Auto",
            tiempo=42,
        )

        print(f"   Name: {metadata['name']}")
        print(f"   Attributes: {len(metadata['attributes'])}")

        # Upload metadata
        print("📤 Uploading metadata to Filecoin Cloud...")
        metadata_cid = client.upload_json(metadata, "test_metadata")
        print(f"✅ Metadata uploaded!")
        print(f"   CID: {metadata_cid}")
        print(f"   URI: {client.get_ipfs_uri(metadata_cid)}")

        # Final results
        print("\n🎉 Upload Test Completed Successfully!")
        print("=" * 50)
        print("🔗 Generated URIs:")
        print(f"   Image URI:    {client.get_ipfs_uri(image_cid)}")
        print(f"   Metadata URI: {client.get_ipfs_uri(metadata_cid)}")
        print(f"   Token URI:    {client.get_ipfs_uri(metadata_cid)}")
        print()
        print("📋 Use the Token URI in your smart contract!")
        print("✅ Filecoin Cloud is working correctly!")

        # Test download
        print("\n📥 Testing file retrieval...")
        try:
            downloaded_image = client.download_file(image_cid)
            downloaded_metadata = client.download_json(metadata_cid)

            print(f"✅ Retrieved image: {len(downloaded_image)} bytes")
            print(f"✅ Retrieved metadata: {downloaded_metadata['name']}")
        except Exception as e:
            print(f"⚠️  Download test failed: {e}")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Make sure bridge service is running: cd bridge && npm start")
        print("2. Check your .env file has correct FILECOIN_PRIVATE_KEY")
        print("3. Run diagnostic: python troubleshoot_filecoin.py")
        print("4. Get more tokens from: https://faucet.calibration.fildev.network/")


if __name__ == "__main__":
    main()
