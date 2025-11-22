#!/usr/bin/env python3
"""
Complete Filecoin Cloud Upload Test Script
Tests end-to-end functionality including image upload and metadata generation
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

# Add modules to path
sys.path.append(str(Path(__file__).parent / "modules"))

from filecoin_client import FilecoinCloudClient
from metadata_builder import build_nft_metadata


def create_test_image() -> bytes:
    """
    Create a simple test image (PNG format)
    """
    # Minimal PNG file data (1x1 pixel transparent PNG)
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


def test_filecoin_connection():
    """
    Test basic Filecoin Cloud connection
    """
    print("🔗 Testing Filecoin Cloud Connection...")
    print("-" * 50)

    try:
        client = FilecoinCloudClient()

        # Test authentication
        is_authenticated = client.test_authentication()

        if is_authenticated:
            print("✅ Filecoin Cloud connection successful")

            # Get balance info
            balance = client.get_balance()
            print(f"💰 Balance: {balance['USDFC']} USDFC, {balance['FIL']} FIL")

            return True
        else:
            print("❌ Authentication failed")
            return False

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def test_image_upload(client: FilecoinCloudClient) -> Optional[str]:
    """
    Test image upload to Filecoin Cloud
    """
    print("\n📤 Testing Image Upload...")
    print("-" * 50)

    try:
        # Create test image
        test_image_data = create_test_image()
        filename = f"test_nft_{int(time.time())}.png"

        print(f"📸 Uploading test image: {filename} ({len(test_image_data)} bytes)")

        # Upload to Filecoin
        start_time = time.time()
        image_cid = client.upload_file(test_image_data, filename)
        upload_time = time.time() - start_time

        print(f"✅ Image uploaded successfully!")
        print(f"   CID: {image_cid}")
        print(f"   URI: {client.get_ipfs_uri(image_cid)}")
        print(f"   Upload time: {upload_time:.2f}s")

        return image_cid

    except Exception as e:
        print(f"❌ Image upload failed: {e}")
        return None


def test_metadata_upload(client: FilecoinCloudClient, image_cid: str) -> Optional[str]:
    """
    Test NFT metadata upload to Filecoin Cloud
    """
    print("\n📝 Testing Metadata Upload...")
    print("-" * 50)

    try:
        # Generate NFT metadata
        image_uri = client.get_ipfs_uri(image_cid)

        metadata = build_nft_metadata(
            name="Test NFT Filecoin",
            description="Test NFT created for Filecoin Cloud integration testing",
            image_uri=image_uri,
            actividad="Testing",
            usuario="System Test",
            acompanante="Automated Script",
            tiempo=42,
        )

        print(f"🏗️  Generated metadata:")
        print(json.dumps(metadata, indent=2))

        # Upload metadata to Filecoin
        start_time = time.time()
        metadata_cid = client.upload_json(metadata, "test_nft_metadata")
        upload_time = time.time() - start_time

        print(f"\n✅ Metadata uploaded successfully!")
        print(f"   CID: {metadata_cid}")
        print(f"   URI: {client.get_ipfs_uri(metadata_cid)}")
        print(f"   Upload time: {upload_time:.2f}s")

        return metadata_cid

    except Exception as e:
        print(f"❌ Metadata upload failed: {e}")
        return None


def test_retrieval(client: FilecoinCloudClient, image_cid: str, metadata_cid: str):
    """
    Test file retrieval from Filecoin Cloud
    """
    print("\n📥 Testing File Retrieval...")
    print("-" * 50)

    try:
        # Test image retrieval
        print(f"🔍 Retrieving image with CID: {image_cid}")
        start_time = time.time()
        retrieved_image = client.download_file(image_cid)
        retrieval_time = time.time() - start_time

        print(f"✅ Image retrieved successfully!")
        print(f"   Size: {len(retrieved_image)} bytes")
        print(f"   Retrieval time: {retrieval_time:.2f}s")

        # Test metadata retrieval
        print(f"\n🔍 Retrieving metadata with CID: {metadata_cid}")
        start_time = time.time()
        retrieved_metadata = client.download_json(metadata_cid)
        retrieval_time = time.time() - start_time

        print(f"✅ Metadata retrieved successfully!")
        print(f"   NFT Name: {retrieved_metadata.get('name', 'Unknown')}")
        print(f"   Attributes: {len(retrieved_metadata.get('attributes', []))}")
        print(f"   Retrieval time: {retrieval_time:.2f}s")

        return True

    except Exception as e:
        print(f"❌ Retrieval failed: {e}")
        return False


def test_cost_estimation(client: FilecoinCloudClient):
    """
    Test cost estimation functionality
    """
    print("\n💰 Testing Cost Estimation...")
    print("-" * 50)

    try:
        # Test different file sizes
        test_sizes = [
            (1024, "1 KB"),
            (1024 * 1024, "1 MB"),
            (10 * 1024 * 1024, "10 MB"),
            (100 * 1024 * 1024, "100 MB"),
        ]

        for size_bytes, size_desc in test_sizes:
            cost = client.estimate_cost(size_bytes, duration_days=30)
            print(f"📊 {size_desc:>8}: {cost:.6f} USDFC (30 days)")

        print("✅ Cost estimation working correctly")
        return True

    except Exception as e:
        print(f"❌ Cost estimation failed: {e}")
        return False


def generate_test_report(results: Dict[str, Any]):
    """
    Generate a comprehensive test report
    """
    print("\n" + "=" * 60)
    print("🧪 FILECOIN CLOUD TEST REPORT")
    print("=" * 60)

    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result.get("success", False))

    print(f"📊 Test Summary: {passed_tests}/{total_tests} tests passed")
    print()

    for test_name, result in results.items():
        status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
        duration = result.get("duration", "N/A")

        print(f"{status} {test_name}")
        if not result.get("success", False) and "error" in result:
            print(f"   Error: {result['error']}")
        if duration != "N/A":
            print(f"   Duration: {duration:.2f}s")
        print()

    if results.get("nft_uris"):
        print("🔗 Generated NFT URIs:")
        for uri_type, uri in results["nft_uris"].items():
            print(f"   {uri_type}: {uri}")
        print()

    if passed_tests == total_tests:
        print("🎉 All tests passed! Filecoin Cloud is fully functional.")
        print(
            "📋 You can now use Filecoin Cloud for NFT storage in your Streamlit app."
        )
    else:
        print("⚠️  Some tests failed. Check the errors above and your configuration.")

    print("=" * 60)


def save_test_log(results: Dict[str, Any]):
    """
    Save test results to log file
    """
    log_dir = Path("uploads/logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"filecoin_test_{int(time.time())}.json"

    test_log = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "test_type": "filecoin_cloud_complete_test",
        "results": results,
        "environment": {
            "rpc_url": os.getenv("FILECOIN_RPC_URL"),
            "bridge_url": os.getenv("FILECOIN_BRIDGE_URL", "http://localhost:3001"),
        },
    }

    with open(log_file, "w") as f:
        json.dump(test_log, f, indent=2)

    print(f"📝 Test log saved to: {log_file}")


def main():
    """
    Main test function
    """
    print("🚀 Filecoin Cloud Complete Upload Test")
    print("=" * 60)
    print()

    # Load environment variables
    from dotenv import load_dotenv

    load_dotenv()

    results = {}
    nft_uris = {}

    # Test 1: Connection
    start_time = time.time()
    connection_success = test_filecoin_connection()
    results["connection"] = {
        "success": connection_success,
        "duration": time.time() - start_time,
    }

    if not connection_success:
        print("\n❌ Connection failed. Cannot continue with upload tests.")
        generate_test_report(results)
        return

    # Initialize client
    client = FilecoinCloudClient()

    # Test 2: Cost Estimation
    start_time = time.time()
    try:
        cost_success = test_cost_estimation(client)
        results["cost_estimation"] = {
            "success": cost_success,
            "duration": time.time() - start_time,
        }
    except Exception as e:
        results["cost_estimation"] = {
            "success": False,
            "duration": time.time() - start_time,
            "error": str(e),
        }

    # Test 3: Image Upload
    start_time = time.time()
    try:
        image_cid = test_image_upload(client)
        results["image_upload"] = {
            "success": image_cid is not None,
            "duration": time.time() - start_time,
            "cid": image_cid,
        }

        if image_cid:
            nft_uris["image"] = client.get_ipfs_uri(image_cid)

    except Exception as e:
        results["image_upload"] = {
            "success": False,
            "duration": time.time() - start_time,
            "error": str(e),
        }
        image_cid = None

    # Test 4: Metadata Upload
    if image_cid:
        start_time = time.time()
        try:
            metadata_cid = test_metadata_upload(client, image_cid)
            results["metadata_upload"] = {
                "success": metadata_cid is not None,
                "duration": time.time() - start_time,
                "cid": metadata_cid,
            }

            if metadata_cid:
                nft_uris["metadata"] = client.get_ipfs_uri(metadata_cid)
                nft_uris["token_uri"] = client.get_ipfs_uri(
                    metadata_cid
                )  # Main URI for smart contracts

        except Exception as e:
            results["metadata_upload"] = {
                "success": False,
                "duration": time.time() - start_time,
                "error": str(e),
            }
            metadata_cid = None
    else:
        results["metadata_upload"] = {
            "success": False,
            "duration": 0,
            "error": "Skipped due to image upload failure",
        }
        metadata_cid = None

    # Test 5: File Retrieval
    if image_cid and metadata_cid:
        start_time = time.time()
        try:
            retrieval_success = test_retrieval(client, image_cid, metadata_cid)
            results["retrieval"] = {
                "success": retrieval_success,
                "duration": time.time() - start_time,
            }
        except Exception as e:
            results["retrieval"] = {
                "success": False,
                "duration": time.time() - start_time,
                "error": str(e),
            }
    else:
        results["retrieval"] = {
            "success": False,
            "duration": 0,
            "error": "Skipped due to upload failures",
        }

    # Add URIs to results
    results["nft_uris"] = nft_uris

    # Generate final report
    generate_test_report(results)

    # Save test log
    save_test_log(results)


if __name__ == "__main__":
    main()
