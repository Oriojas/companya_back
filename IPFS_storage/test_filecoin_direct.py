#!/usr/bin/env python3
"""
Test script specifically for Filecoin Direct client
Tests direct Filecoin network integration without Synapse SDK
"""

import json
import os
import sys
import time
from datetime import datetime
from io import BytesIO
from pathlib import Path

from PIL import Image

# Add modules to path
sys.path.append(str(Path(__file__).parent / "modules"))

from dotenv import load_dotenv
from filecoin_direct_client import FilecoinDirectClient

# Load environment variables
load_dotenv()


class FilecoinDirectTester:
    """Test suite for Filecoin Direct client"""

    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {},
        }

    def log(self, message, test_type="INFO"):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if test_type == "PASS":
            print(f"[{timestamp}] ✅ {message}")
        elif test_type == "FAIL":
            print(f"[{timestamp}] ❌ {message}")
        elif test_type == "WARN":
            print(f"[{timestamp}] ⚠️  {message}")
        else:
            print(f"[{timestamp}] ℹ️  {message}")

    def create_test_image(self, width=100, height=100, color=(255, 0, 0)) -> bytes:
        """Create a test image"""
        img = Image.new("RGB", (width, height), color=color)
        img_bytes = BytesIO()
        img.save(img_bytes, format="PNG")
        return img_bytes.getvalue()

    def create_test_json(self, name="test_nft") -> dict:
        """Create test JSON metadata"""
        return {
            "name": name,
            "description": "Test NFT metadata for Filecoin Direct testing",
            "image": "ipfs://placeholder_will_be_replaced",
            "attributes": [
                {"trait_type": "Storage", "value": "Filecoin Direct"},
                {"trait_type": "Test", "value": "True"},
                {"trait_type": "Timestamp", "value": datetime.now().isoformat()},
            ],
            "external_url": "https://github.com/filecoin-project",
            "test_data": {
                "uploader": "filecoin_direct_tester",
                "version": "1.0",
                "test_id": int(time.time()),
            },
        }

    def test_client_initialization(self) -> dict:
        """Test client initialization"""
        self.log("Testing Filecoin Direct client initialization...")

        test_result = {
            "test": "client_initialization",
            "success": False,
            "error": None,
            "duration": 0,
        }

        start_time = time.time()

        try:
            client = FilecoinDirectClient()
            test_result["duration"] = time.time() - start_time
            test_result["success"] = True
            test_result["wallet_address"] = client.wallet_address
            test_result["network"] = client.rpc_url
            self.log("Client initialization successful", "PASS")
            return test_result

        except Exception as e:
            test_result["duration"] = time.time() - start_time
            test_result["error"] = str(e)
            self.log(f"Client initialization failed: {e}", "FAIL")
            return test_result

    def test_network_connection(self, client) -> dict:
        """Test network connection"""
        self.log("Testing Filecoin network connection...")

        test_result = {
            "test": "network_connection",
            "success": False,
            "error": None,
            "duration": 0,
        }

        start_time = time.time()

        try:
            auth_result = client.test_authentication()
            test_result["duration"] = time.time() - start_time
            test_result["success"] = auth_result

            if auth_result:
                self.log("Network connection successful", "PASS")
            else:
                test_result["error"] = "Authentication failed"
                self.log("Network connection failed", "FAIL")

            return test_result

        except Exception as e:
            test_result["duration"] = time.time() - start_time
            test_result["error"] = str(e)
            self.log(f"Network connection error: {e}", "FAIL")
            return test_result

    def test_wallet_balance(self, client) -> dict:
        """Test wallet balance retrieval"""
        self.log("Testing wallet balance retrieval...")

        test_result = {
            "test": "wallet_balance",
            "success": False,
            "error": None,
            "duration": 0,
            "balance": None,
        }

        start_time = time.time()

        try:
            balance_info = client.get_balance()
            test_result["duration"] = time.time() - start_time

            if balance_info.get("success"):
                balances = balance_info.get("balances", {})
                test_result["success"] = True
                test_result["balance"] = balances
                self.log(f"Balance: {balances.get('FIL', '0')} FIL", "PASS")
            else:
                test_result["error"] = balance_info.get("error", "Unknown error")
                self.log(f"Balance check failed: {test_result['error']}", "FAIL")

            return test_result

        except Exception as e:
            test_result["duration"] = time.time() - start_time
            test_result["error"] = str(e)
            self.log(f"Balance check error: {e}", "FAIL")
            return test_result

    def test_storage_info(self, client) -> dict:
        """Test storage information retrieval"""
        self.log("Testing storage information retrieval...")

        test_result = {
            "test": "storage_info",
            "success": False,
            "error": None,
            "duration": 0,
            "providers": None,
        }

        start_time = time.time()

        try:
            storage_info = client.get_storage_info()
            test_result["duration"] = time.time() - start_time

            if storage_info.get("success"):
                info = storage_info.get("info", {})
                test_result["success"] = True
                test_result["providers"] = info.get("totalProviders", 0)
                test_result["network"] = info.get("network", "unknown")
                self.log(
                    f"Network: {test_result['network']}, Providers: {test_result['providers']}",
                    "PASS",
                )
            else:
                test_result["error"] = storage_info.get("error", "Unknown error")
                self.log(f"Storage info failed: {test_result['error']}", "FAIL")

            return test_result

        except Exception as e:
            test_result["duration"] = time.time() - start_time
            test_result["error"] = str(e)
            self.log(f"Storage info error: {e}", "FAIL")
            return test_result

    def test_image_upload(self, client, image_data: bytes, filename: str) -> dict:
        """Test image upload"""
        self.log(f"Testing image upload: {filename}")

        test_result = {
            "test": "image_upload",
            "filename": filename,
            "size": len(image_data),
            "success": False,
            "cid": None,
            "error": None,
            "duration": 0,
        }

        start_time = time.time()

        try:
            cid = client.upload_file(image_data, filename, {"type": "test_image"})
            test_result["duration"] = time.time() - start_time
            test_result["success"] = True
            test_result["cid"] = cid
            self.log(f"Image upload successful: {cid}", "PASS")
            return test_result

        except Exception as e:
            test_result["duration"] = time.time() - start_time
            test_result["error"] = str(e)
            self.log(f"Image upload failed: {e}", "FAIL")
            return test_result

    def test_json_upload(self, client, json_data: dict, name: str) -> dict:
        """Test JSON upload"""
        self.log(f"Testing JSON upload: {name}")

        test_result = {
            "test": "json_upload",
            "name": name,
            "size": len(json.dumps(json_data)),
            "success": False,
            "cid": None,
            "error": None,
            "duration": 0,
        }

        start_time = time.time()

        try:
            cid = client.upload_json(json_data, name)
            test_result["duration"] = time.time() - start_time
            test_result["success"] = True
            test_result["cid"] = cid
            self.log(f"JSON upload successful: {cid}", "PASS")
            return test_result

        except Exception as e:
            test_result["duration"] = time.time() - start_time
            test_result["error"] = str(e)
            self.log(f"JSON upload failed: {e}", "FAIL")
            return test_result

    def test_download_verification(
        self, client, cid: str, original_data: bytes
    ) -> dict:
        """Test download and verify data integrity"""
        self.log(f"Testing download verification for CID: {cid}")

        test_result = {
            "test": "download_verification",
            "cid": cid,
            "success": False,
            "data_matches": False,
            "error": None,
            "duration": 0,
        }

        start_time = time.time()

        try:
            downloaded_data = client.download_file(cid)
            test_result["duration"] = time.time() - start_time
            test_result["success"] = True
            test_result["data_matches"] = downloaded_data == original_data

            if test_result["data_matches"]:
                self.log(f"Download verification successful - data matches", "PASS")
            else:
                self.log(f"Download verification failed - data mismatch", "FAIL")

            return test_result

        except Exception as e:
            test_result["duration"] = time.time() - start_time
            test_result["error"] = str(e)
            self.log(f"Download verification error: {e}", "FAIL")
            return test_result

    def test_uri_generation(self, client, cid: str) -> dict:
        """Test URI generation"""
        self.log(f"Testing URI generation for CID: {cid}")

        test_result = {
            "test": "uri_generation",
            "cid": cid,
            "success": False,
            "ipfs_uri": None,
            "gateway_url": None,
            "error": None,
        }

        try:
            ipfs_uri = client.get_ipfs_uri(cid)
            gateway_url = client.get_gateway_url(cid)

            test_result["success"] = True
            test_result["ipfs_uri"] = ipfs_uri
            test_result["gateway_url"] = gateway_url

            self.log(f"IPFS URI: {ipfs_uri}", "PASS")
            self.log(f"Gateway URL: {gateway_url}", "PASS")

            return test_result

        except Exception as e:
            test_result["error"] = str(e)
            self.log(f"URI generation error: {e}", "FAIL")
            return test_result

    def run_comprehensive_test(self):
        """Run comprehensive Filecoin Direct test suite"""
        self.log("🚀 Starting Filecoin Direct comprehensive tests")
        self.log("=" * 60)

        # Test 1: Client Initialization
        init_result = self.test_client_initialization()
        self.results["tests"].append(init_result)

        if not init_result["success"]:
            self.log("❌ Cannot continue - client initialization failed", "FAIL")
            self._generate_summary()
            self._print_summary()
            return

        # Initialize client for subsequent tests
        try:
            client = FilecoinDirectClient()
        except Exception as e:
            self.log(f"❌ Failed to create client: {e}", "FAIL")
            self._generate_summary()
            self._print_summary()
            return

        # Test 2: Network Connection
        network_result = self.test_network_connection(client)
        self.results["tests"].append(network_result)

        # Test 3: Wallet Balance
        balance_result = self.test_wallet_balance(client)
        self.results["tests"].append(balance_result)

        # Test 4: Storage Info
        storage_result = self.test_storage_info(client)
        self.results["tests"].append(storage_result)

        # Test 5: Image Upload
        test_image = self.create_test_image(200, 200, (0, 255, 0))  # Green test image
        image_result = self.test_image_upload(client, test_image, "test_image.png")
        self.results["tests"].append(image_result)

        # Test 6: URI Generation (if upload was successful)
        if image_result["success"]:
            uri_result = self.test_uri_generation(client, image_result["cid"])
            self.results["tests"].append(uri_result)

            # Test 7: Download Verification
            download_result = self.test_download_verification(
                client, image_result["cid"], test_image
            )
            self.results["tests"].append(download_result)

        # Test 8: JSON Upload
        test_json = self.create_test_json("filecoin_direct_test")
        json_result = self.test_json_upload(client, test_json, "test_metadata")
        self.results["tests"].append(json_result)

        # Test 9: Complete NFT Workflow
        if image_result["success"] and json_result["success"]:
            self.log("Testing complete NFT workflow...")

            # Update JSON with actual image CID
            nft_metadata = self.create_test_json("complete_nft_test")
            nft_metadata["image"] = client.get_ipfs_uri(image_result["cid"])

            nft_result = self.test_json_upload(
                client, nft_metadata, "complete_nft_metadata"
            )
            self.results["tests"].append(nft_result)

            if nft_result["success"]:
                self.log(f"🎉 Complete NFT workflow successful!", "PASS")
                self.log(f"   Image CID: {image_result['cid']}")
                self.log(f"   Metadata CID: {nft_result['cid']}")
                self.log(f"   Token URI: {client.get_ipfs_uri(nft_result['cid'])}")

        # Generate summary and save results
        self._generate_summary()
        self._save_results()

        self.log("=" * 60)
        self.log("🏁 Filecoin Direct tests completed")
        self._print_summary()

    def _generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.results["tests"])
        passed_tests = sum(1 for test in self.results["tests"] if test["success"])
        failed_tests = total_tests - passed_tests

        # Calculate success rate
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        # Group by test type
        test_types = {}
        for test in self.results["tests"]:
            test_type = test["test"]
            if test_type not in test_types:
                test_types[test_type] = {"total": 0, "passed": 0}
            test_types[test_type]["total"] += 1
            if test["success"]:
                test_types[test_type]["passed"] += 1

        self.results["summary"] = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": f"{success_rate:.1f}%",
            "test_types": test_types,
        }

    def _save_results(self):
        """Save test results to file"""
        results_file = Path(__file__).parent / "filecoin_direct_test_results.json"
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2)
        self.log(f"Results saved to: {results_file}")

    def _print_summary(self):
        """Print test summary"""
        summary = self.results["summary"]

        print("\n📊 FILECOIN DIRECT TEST SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']} ✅")
        print(f"Failed: {summary['failed']} ❌")
        print(f"Success Rate: {summary['success_rate']}")
        print("")

        print("📈 BY TEST TYPE:")
        for test_type, stats in summary["test_types"].items():
            rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            print(f"{test_type}: {stats['passed']}/{stats['total']} ({rate:.1f}%)")

        print("")

        # Recommendations based on results
        if summary["passed"] == summary["total_tests"]:
            print("🎉 ALL TESTS PASSED!")
            print(
                "✅ Filecoin Direct is fully functional and ready for production use."
            )
        elif summary["passed"] > summary["total_tests"] * 0.7:
            print("✅ Most tests passed - Filecoin Direct is working well.")
            print("💡 Check failed tests for minor issues.")
        else:
            print(
                "⚠️  Several tests failed - check configuration and network connectivity."
            )

        print("")

        # Show failed tests
        failed_tests = [test for test in self.results["tests"] if not test["success"]]
        if failed_tests:
            print("❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   • {test['test']}: {test.get('error', 'Unknown error')}")

        print("")
        print("🔗 Next Steps:")
        if summary["passed"] == summary["total_tests"]:
            print("   • Use Filecoin Direct in your Streamlit app")
            print("   • Test with larger files")
            print("   • Monitor storage deals")
        else:
            print("   • Check your .env configuration")
            print("   • Verify network connectivity")
            print("   • Ensure wallet has sufficient balance")


def main():
    """Main test runner"""
    print("🔷 Filecoin Direct Test Suite")
    print("Testing direct Filecoin network integration")

    # Check environment setup
    if not os.getenv("FILECOIN_PRIVATE_KEY"):
        print("❌ FILECOIN_PRIVATE_KEY not found in environment variables")
        print("Please configure your .env file with:")
        print("  FILECOIN_PRIVATE_KEY=your_private_key_here")
        print("  FILECOIN_WALLET_ADDRESS=your_wallet_address_here")
        sys.exit(1)

    tester = FilecoinDirectTester()
    tester.run_comprehensive_test()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test runner failed: {e}")
        sys.exit(1)
