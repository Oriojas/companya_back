#!/usr/bin/env python3
"""
Storage Providers Test Script
Comprehensive testing for both Pinata and Filecoin Cloud providers
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Add modules directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "modules"))

from dotenv import load_dotenv
from filecoin_client import FilecoinCloudClient
from metadata_builder import build_nft_metadata, validate_metadata
from pinata_client import PinataClient

# Load environment variables
load_dotenv()


def print_header(title: str):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_section(title: str):
    """Print formatted section"""
    print(f"\n🔧 {title}")
    print("-" * 40)


def create_test_data():
    """Create test data for uploads"""
    # Test image data (small PNG-like data)
    test_image = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0fIDATx\x9cc```bPPP\x00\x02\xd2\x02\x01t\xc2\x02\x9e\x00\x00\x00\x00IEND\xaeB`\x82"
    # Pad to ensure minimum size for Filecoin
    test_image += b"\x00" * (127 - len(test_image)) if len(test_image) < 127 else b""

    # Test metadata
    test_metadata = build_nft_metadata(
        name="Test NFT #001",
        description="This is a test NFT created during provider testing",
        image_uri="ipfs://QmTestImageCID",  # Will be replaced
        actividad="Testing",
        usuario="Test User",
        acompanante="Test Assistant",
        tiempo=42,
    )

    return test_image, test_metadata


def test_pinata_provider() -> Dict[str, Any]:
    """Test Pinata provider"""
    print_header("Testing Pinata IPFS Provider")

    results = {
        "provider": "Pinata",
        "connection": False,
        "image_upload": False,
        "metadata_upload": False,
        "image_cid": None,
        "metadata_cid": None,
        "image_uri": None,
        "metadata_uri": None,
        "errors": [],
        "timing": {},
    }

    try:
        print_section("Initializing Pinata Client")

        # Check environment variables
        api_key = os.getenv("PINATA_API_KEY")
        secret_key = os.getenv("PINATA_SECRET_API_KEY")

        if not api_key or not secret_key:
            results["errors"].append("Pinata credentials not found in .env")
            print("❌ Pinata credentials not configured")
            return results

        print(f"✅ API Key: {api_key[:10]}...")
        print(f"✅ Secret Key: {secret_key[:10]}...")

        # Initialize client
        start_time = time.time()
        client = PinataClient()

        # Test authentication
        print_section("Testing Connection")
        if client.test_authentication():
            results["connection"] = True
            print("✅ Pinata connection successful")

            # Get account info
            try:
                account_info = client.get_account_info()
                if "error" not in account_info:
                    print(f"📊 Pin Count: {account_info.get('pin_count', 'N/A')}")
                    print(
                        f"📊 Pin Size: {account_info.get('pin_size_total', 'N/A')} bytes"
                    )
                else:
                    print(f"⚠️  Account info: {account_info.get('error', 'Unknown')}")
            except Exception as e:
                print(f"⚠️  Could not get account info: {e}")
        else:
            results["errors"].append("Pinata authentication failed")
            print("❌ Pinata connection failed")
            return results

        results["timing"]["connection"] = time.time() - start_time

        # Test image upload
        print_section("Testing Image Upload")
        test_image, test_metadata = create_test_data()

        start_time = time.time()
        try:
            image_cid = client.upload_file(
                file_bytes=test_image,
                filename="test_image.png",
                metadata={"name": "test_image", "type": "test"},
            )

            results["image_upload"] = True
            results["image_cid"] = image_cid
            results["image_uri"] = client.get_ipfs_uri(image_cid)
            results["timing"]["image_upload"] = time.time() - start_time

            print(f"✅ Image uploaded successfully")
            print(f"   CID: {image_cid}")
            print(f"   URI: {results['image_uri']}")
            print(f"   Gateway: {client.get_gateway_url(image_cid)}")

        except Exception as e:
            results["errors"].append(f"Image upload failed: {str(e)}")
            print(f"❌ Image upload failed: {e}")
            return results

        # Test metadata upload
        print_section("Testing Metadata Upload")

        # Update metadata with actual image URI
        test_metadata["image"] = results["image_uri"]
        test_metadata["external_url"] = results["image_uri"]

        # Validate metadata
        validation_errors = validate_metadata(test_metadata)
        if validation_errors:
            print("⚠️  Metadata validation warnings:")
            for error in validation_errors:
                print(f"   • {error}")
        else:
            print("✅ Metadata validation passed")

        start_time = time.time()
        try:
            metadata_cid = client.upload_json(
                json_data=test_metadata, name="test_nft_metadata"
            )

            results["metadata_upload"] = True
            results["metadata_cid"] = metadata_cid
            results["metadata_uri"] = client.get_ipfs_uri(metadata_cid)
            results["timing"]["metadata_upload"] = time.time() - start_time

            print(f"✅ Metadata uploaded successfully")
            print(f"   CID: {metadata_cid}")
            print(f"   URI: {results['metadata_uri']}")
            print(f"   Gateway: {client.get_gateway_url(metadata_cid)}")

        except Exception as e:
            results["errors"].append(f"Metadata upload failed: {str(e)}")
            print(f"❌ Metadata upload failed: {e}")
            return results

        print_section("Test Summary")
        print("✅ All Pinata tests passed successfully!")

    except Exception as e:
        results["errors"].append(f"Unexpected error: {str(e)}")
        print(f"❌ Unexpected error: {e}")

    return results


def test_filecoin_provider() -> Dict[str, Any]:
    """Test Filecoin Cloud provider"""
    print_header("Testing Filecoin Cloud Provider")

    results = {
        "provider": "Filecoin Cloud",
        "connection": False,
        "bridge_running": False,
        "balance_check": False,
        "image_upload": False,
        "metadata_upload": False,
        "image_cid": None,
        "metadata_cid": None,
        "image_uri": None,
        "metadata_uri": None,
        "errors": [],
        "timing": {},
        "balances": {},
    }

    try:
        print_section("Checking Configuration")

        # Check environment variables
        private_key = os.getenv("FILECOIN_PRIVATE_KEY")
        rpc_url = os.getenv("FILECOIN_RPC_URL")

        if not private_key:
            results["errors"].append("Filecoin private key not found in .env")
            print("❌ FILECOIN_PRIVATE_KEY not configured")
            return results

        print(f"✅ Private Key: {private_key[:10]}...{private_key[-10:]}")
        print(f"✅ RPC URL: {rpc_url or 'Using default Calibration testnet'}")

        # Initialize client
        print_section("Initializing Filecoin Client")
        start_time = time.time()

        try:
            client = FilecoinCloudClient()
            results["timing"]["initialization"] = time.time() - start_time
            print("✅ Filecoin client initialized")
        except Exception as e:
            results["errors"].append(f"Client initialization failed: {str(e)}")
            print(f"❌ Client initialization failed: {e}")
            return results

        # Test connection
        print_section("Testing Connection")
        start_time = time.time()

        if client.test_authentication():
            results["connection"] = True
            results["bridge_running"] = True
            results["timing"]["connection"] = time.time() - start_time
            print("✅ Filecoin connection successful")
            print("✅ Bridge service is running")
        else:
            results["errors"].append("Filecoin connection failed")
            print("❌ Filecoin connection failed")
            print("💡 Make sure bridge service is running: cd bridge && npm start")
            return results

        # Check balance
        print_section("Checking Wallet Balance")
        try:
            balance_info = client.get_balance()
            if "error" not in balance_info:
                results["balance_check"] = True
                results["balances"] = balance_info.get("balances", {})

                usdfc_balance = float(results["balances"].get("USDFC", "0"))
                fil_balance = float(results["balances"].get("FIL", "0"))

                print("💰 Current balances:")
                print(f"   USDFC: {usdfc_balance:.6f}")
                print(f"   FIL: {fil_balance:.6f}")

                if usdfc_balance < 0.1:
                    print("⚠️  Low USDFC balance - you may need more for storage")
                    print("   Get tokens: https://faucet.calibration.fildev.network/")

                if fil_balance < 0.001:
                    print("⚠️  Low FIL balance - you may need more for gas fees")
                    print("   Get tokens: https://faucet.calibration.fildev.network/")
            else:
                results["errors"].append(
                    f"Balance check failed: {balance_info.get('error')}"
                )
                print(f"❌ Could not check balance: {balance_info.get('error')}")
        except Exception as e:
            results["errors"].append(f"Balance check error: {str(e)}")
            print(f"❌ Balance check failed: {e}")

        # Get storage info
        print_section("Getting Storage Information")
        try:
            storage_info = client.get_storage_info()
            if "error" not in storage_info:
                info = storage_info.get("info", {})
                print(f"📊 Total Providers: {info.get('totalProviders', 'N/A')}")
                print(f"📊 Active Providers: {info.get('activeProviders', 'N/A')}")
            else:
                print(f"⚠️  Could not get storage info: {storage_info.get('error')}")
        except Exception as e:
            print(f"⚠️  Storage info error: {e}")

        # Test image upload
        print_section("Testing Image Upload")
        test_image, test_metadata = create_test_data()

        print(f"📄 Test image size: {len(test_image)} bytes")

        # Estimate cost
        try:
            cost_estimate = client.estimate_cost(len(test_image), 30)
            if "error" not in cost_estimate:
                estimation = cost_estimate.get("estimation", {})
                print(
                    f"💵 Estimated cost: {estimation.get('estimatedCostUSDFC', 'N/A')} USDFC"
                )
        except Exception as e:
            print(f"⚠️  Could not estimate cost: {e}")

        start_time = time.time()
        try:
            image_cid = client.upload_file(
                file_bytes=test_image,
                filename="test_image.png",
                metadata={"name": "test_image", "type": "test"},
            )

            results["image_upload"] = True
            results["image_cid"] = image_cid
            results["image_uri"] = client.get_ipfs_uri(image_cid)
            results["timing"]["image_upload"] = time.time() - start_time

            print(f"✅ Image uploaded successfully")
            print(f"   Piece CID: {image_cid}")
            print(f"   URI: {results['image_uri']}")
            print(f"   Gateway: {client.get_gateway_url(image_cid)}")

        except Exception as e:
            results["errors"].append(f"Image upload failed: {str(e)}")
            print(f"❌ Image upload failed: {e}")
            return results

        # Test metadata upload
        print_section("Testing Metadata Upload")

        # Update metadata with actual image URI
        test_metadata["image"] = results["image_uri"]
        test_metadata["external_url"] = results["image_uri"]

        # Validate metadata
        validation_errors = validate_metadata(test_metadata)
        if validation_errors:
            print("⚠️  Metadata validation warnings:")
            for error in validation_errors:
                print(f"   • {error}")
        else:
            print("✅ Metadata validation passed")

        print(f"📄 Metadata size: {len(json.dumps(test_metadata))} bytes")

        start_time = time.time()
        try:
            metadata_cid = client.upload_json(
                json_data=test_metadata, name="test_nft_metadata"
            )

            results["metadata_upload"] = True
            results["metadata_cid"] = metadata_cid
            results["metadata_uri"] = client.get_ipfs_uri(metadata_cid)
            results["timing"]["metadata_upload"] = time.time() - start_time

            print(f"✅ Metadata uploaded successfully")
            print(f"   Piece CID: {metadata_cid}")
            print(f"   URI: {results['metadata_uri']}")
            print(f"   Gateway: {client.get_gateway_url(metadata_cid)}")

        except Exception as e:
            results["errors"].append(f"Metadata upload failed: {str(e)}")
            print(f"❌ Metadata upload failed: {e}")
            return results

        # Test download (optional)
        print_section("Testing Download")
        try:
            downloaded_data = client.download_file(results["image_cid"])
            if len(downloaded_data) > 0:
                print(f"✅ Download test successful: {len(downloaded_data)} bytes")
            else:
                print("⚠️  Download returned empty data")
        except Exception as e:
            print(f"⚠️  Download test failed: {e}")

        print_section("Test Summary")
        print("✅ All Filecoin Cloud tests passed successfully!")

    except Exception as e:
        results["errors"].append(f"Unexpected error: {str(e)}")
        print(f"❌ Unexpected error: {e}")

    return results


def compare_providers(pinata_results: Dict, filecoin_results: Dict):
    """Compare results from both providers"""
    print_header("Provider Comparison")

    print("🏁 Test Results Summary:")
    print(f"{'Metric':<25} {'Pinata':<15} {'Filecoin Cloud':<15}")
    print("-" * 55)

    # Connection
    pinata_conn = "✅ Pass" if pinata_results["connection"] else "❌ Fail"
    filecoin_conn = "✅ Pass" if filecoin_results["connection"] else "❌ Fail"
    print(f"{'Connection':<25} {pinata_conn:<15} {filecoin_conn:<15}")

    # Image Upload
    pinata_img = "✅ Pass" if pinata_results["image_upload"] else "❌ Fail"
    filecoin_img = "✅ Pass" if filecoin_results["image_upload"] else "❌ Fail"
    print(f"{'Image Upload':<25} {pinata_img:<15} {filecoin_img:<15}")

    # Metadata Upload
    pinata_meta = "✅ Pass" if pinata_results["metadata_upload"] else "❌ Fail"
    filecoin_meta = "✅ Pass" if filecoin_results["metadata_upload"] else "❌ Fail"
    print(f"{'Metadata Upload':<25} {pinata_meta:<15} {filecoin_meta:<15}")

    # Timing comparison
    print(f"\n⏱️  Performance Comparison:")
    print(f"{'Operation':<25} {'Pinata (s)':<15} {'Filecoin (s)':<15}")
    print("-" * 55)

    operations = ["connection", "image_upload", "metadata_upload"]
    for op in operations:
        pinata_time = pinata_results["timing"].get(op, 0)
        filecoin_time = filecoin_results["timing"].get(op, 0)
        print(
            f"{op.replace('_', ' ').title():<25} {pinata_time:.2f:<15} {filecoin_time:.2f:<15}"
        )

    # Final URIs
    print(f"\n🔗 Generated URIs:")
    if pinata_results["metadata_uri"]:
        print(f"Pinata NFT URI:     {pinata_results['metadata_uri']}")
    if filecoin_results["metadata_uri"]:
        print(f"Filecoin NFT URI:   {filecoin_results['metadata_uri']}")

    # Errors
    all_errors = pinata_results["errors"] + filecoin_results["errors"]
    if all_errors:
        print(f"\n❌ Errors Found:")
        for error in all_errors:
            print(f"   • {error}")
    else:
        print(f"\n✅ No errors found in any provider!")


def save_test_results(pinata_results: Dict, filecoin_results: Dict):
    """Save test results to file"""
    results = {
        "timestamp": datetime.now().isoformat(),
        "test_type": "provider_comparison",
        "providers": {"pinata": pinata_results, "filecoin": filecoin_results},
    }

    # Create results directory
    results_dir = Path("uploads/logs")
    results_dir.mkdir(parents=True, exist_ok=True)

    # Save results
    results_file = (
        results_dir / f"provider_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )

    try:
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Test results saved to: {results_file}")
    except Exception as e:
        print(f"\n⚠️  Could not save results: {e}")


def main():
    """Main test function"""
    print_header("IPFS Storage Providers Test Suite")
    print("Testing both Pinata and Filecoin Cloud providers")

    # Check if we have any provider configured
    has_pinata = os.getenv("PINATA_API_KEY") and os.getenv("PINATA_SECRET_API_KEY")
    has_filecoin = os.getenv("FILECOIN_PRIVATE_KEY")

    if not has_pinata and not has_filecoin:
        print("❌ No storage providers configured!")
        print("Please configure at least one provider in your .env file:")
        print("  - For Pinata: PINATA_API_KEY and PINATA_SECRET_API_KEY")
        print("  - For Filecoin: FILECOIN_PRIVATE_KEY")
        return False

    # Test providers
    pinata_results = {
        "provider": "Pinata",
        "connection": False,
        "errors": ["Provider not configured"],
    }
    filecoin_results = {
        "provider": "Filecoin Cloud",
        "connection": False,
        "errors": ["Provider not configured"],
    }

    if has_pinata:
        try:
            pinata_results = test_pinata_provider()
        except Exception as e:
            print(f"❌ Pinata test failed with exception: {e}")
            pinata_results["errors"].append(f"Test exception: {str(e)}")
    else:
        print("⏭️  Skipping Pinata tests (not configured)")

    if has_filecoin:
        try:
            filecoin_results = test_filecoin_provider()
        except Exception as e:
            print(f"❌ Filecoin test failed with exception: {e}")
            filecoin_results["errors"].append(f"Test exception: {str(e)}")
    else:
        print("⏭️  Skipping Filecoin tests (not configured)")

    # Compare results
    if has_pinata or has_filecoin:
        compare_providers(pinata_results, filecoin_results)
        save_test_results(pinata_results, filecoin_results)

    # Recommendations
    print_header("Recommendations")

    if pinata_results["connection"] and filecoin_results["connection"]:
        print("🎉 Both providers are working! Choose based on your needs:")
        print("   📌 Pinata: Fast setup, good for prototyping")
        print("   🟠 Filecoin: More storage, permanent, decentralized")
    elif pinata_results["connection"]:
        print("📌 Pinata is ready to use")
    elif filecoin_results["connection"]:
        print("🟠 Filecoin Cloud is ready to use")
    else:
        print("❌ No providers are working. Check your configuration.")
        return False

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
