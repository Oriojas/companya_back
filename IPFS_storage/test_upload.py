#!/usr/bin/env python3
"""
Comprehensive upload test for Filecoin and IPFS Direct services
Tests both Filecoin Cloud (via bridge) and direct IPFS upload methods
"""

import json
import os
import sys
import time
from datetime import datetime
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image

# Add modules to path
sys.path.append(str(Path(__file__).parent / "modules"))

from dotenv import load_dotenv
from filecoin_pin_client import FilecoinPinClient
from ipfs_direct_client import IPFSDirectClient
from lighthouse_client import LighthouseClient

# Load environment variables
load_dotenv()


class UploadTester:
    """Comprehensive upload testing class"""

    def __init__(self):
        self.bridge_url = os.getenv("FILECOIN_BRIDGE_URL", "http://localhost:3001")
        self.ipfs_client = IPFSDirectClient()

        # Initialize other clients
        self.lighthouse_client = None
        self.filecoin_pin_client = None

        try:
            if os.getenv("LIGHTHOUSE_API_KEY"):
                self.lighthouse_client = LighthouseClient()
        except:
            pass

        try:
            if os.getenv("FILECOIN_PRIVATE_KEY"):
                self.filecoin_pin_client = FilecoinPinClient()
        except:
            pass

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

    def create_test_json(self, name="test_metadata") -> dict:
        """Create test JSON metadata"""
        return {
            "name": name,
            "description": "Test NFT metadata for upload testing",
            "image": "placeholder_will_be_replaced",
            "attributes": [
                {"trait_type": "Test", "value": "True"},
                {"trait_type": "Timestamp", "value": datetime.now().isoformat()},
            ],
            "test_data": {
                "uploader": "upload_tester",
                "version": "1.0",
                "test_id": int(time.time()),
            },
        }

    def test_bridge_health(self) -> bool:
        """Test if Filecoin bridge is healthy"""
        self.log("Testing Filecoin bridge health...")
        try:
            response = requests.get(f"{self.bridge_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log(f"Bridge service: {data.get('status', 'unknown')}", "PASS")
                    return True

            self.log("Bridge service not responding correctly", "FAIL")
            return False

        except Exception as e:
            self.log(f"Bridge service error: {e}", "FAIL")
            return False

    def test_bridge_balance(self) -> dict:
        """Test bridge balance"""
        self.log("Checking Filecoin bridge balance...")
        try:
            response = requests.get(f"{self.bridge_url}/balance", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    balances = data.get("balances", {})
                    self.log(
                        f"USDFC: {balances.get('USDFC', '0')}, FIL: {balances.get('FIL', '0')}",
                        "PASS",
                    )
                    return balances

            self.log("Could not get balance information", "WARN")
            return {}

        except Exception as e:
            self.log(f"Balance check error: {e}", "FAIL")
            return {}

    def test_filecoin_image_upload(self, image_data: bytes, filename: str) -> dict:
        """Test image upload to Filecoin"""
        self.log(f"Testing Filecoin image upload: {filename}")

        test_result = {
            "method": "filecoin_bridge",
            "type": "image",
            "filename": filename,
            "size": len(image_data),
            "success": False,
            "cid": None,
            "error": None,
            "duration": 0,
        }

        start_time = time.time()

        try:
            files = {"file": (filename, image_data, "image/png")}
            data = {
                "filename": filename,
                "metadata": json.dumps({"type": "test_image"}),
            }

            response = requests.post(
                f"{self.bridge_url}/upload/file", files=files, data=data, timeout=120
            )

            test_result["duration"] = time.time() - start_time

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    test_result["success"] = True
                    test_result["cid"] = result.get("pieceCid")
                    self.log(
                        f"Filecoin upload successful: {test_result['cid']}", "PASS"
                    )
                else:
                    test_result["error"] = result.get("error", "Unknown error")
                    self.log(f"Filecoin upload failed: {test_result['error']}", "FAIL")
            else:
                test_result["error"] = f"HTTP {response.status_code}: {response.text}"
                self.log(f"Filecoin upload failed: {test_result['error']}", "FAIL")

        except Exception as e:
            test_result["duration"] = time.time() - start_time
            test_result["error"] = str(e)
            self.log(f"Filecoin upload exception: {e}", "FAIL")

        return test_result

    def test_filecoin_json_upload(self, json_data: dict, name: str) -> dict:
        """Test JSON upload to Filecoin"""
        self.log(f"Testing Filecoin JSON upload: {name}")

        test_result = {
            "method": "filecoin_bridge",
            "type": "json",
            "name": name,
            "size": len(json.dumps(json_data)),
            "success": False,
            "cid": None,
            "error": None,
            "duration": 0,
        }

        start_time = time.time()

        try:
            payload = {"data": json_data, "name": name}

            response = requests.post(
                f"{self.bridge_url}/upload/json", json=payload, timeout=60
            )

            test_result["duration"] = time.time() - start_time

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    test_result["success"] = True
                    test_result["cid"] = result.get("pieceCid")
                    self.log(
                        f"Filecoin JSON upload successful: {test_result['cid']}", "PASS"
                    )
                else:
                    test_result["error"] = result.get("error", "Unknown error")
                    self.log(
                        f"Filecoin JSON upload failed: {test_result['error']}", "FAIL"
                    )
            else:
                test_result["error"] = f"HTTP {response.status_code}: {response.text}"
                self.log(f"Filecoin JSON upload failed: {test_result['error']}", "FAIL")

        except Exception as e:
            test_result["duration"] = time.time() - start_time
            test_result["error"] = str(e)
            self.log(f"Filecoin JSON upload exception: {e}", "FAIL")

        return test_result

    def test_ipfs_direct_upload(
        self, data: bytes, filename: str, data_type: str
    ) -> dict:
        """Test direct IPFS upload"""
        self.log(f"Testing IPFS direct upload: {filename}")

        test_result = {
            "method": "ipfs_direct",
            "type": data_type,
            "filename": filename,
            "size": len(data),
            "success": False,
            "cid": None,
            "error": None,
            "duration": 0,
        }

        start_time = time.time()

        try:
            if data_type == "json":
                json_data = json.loads(data.decode("utf-8"))
                cid = self.ipfs_client.upload_json(
                    json_data, filename.replace(".json", "")
                )
            else:
                cid = self.ipfs_client.upload_file(data, filename)

            test_result["duration"] = time.time() - start_time
            test_result["success"] = True
            test_result["cid"] = cid
            self.log(f"IPFS direct upload successful: {cid}", "PASS")

        except Exception as e:
            test_result["duration"] = time.time() - start_time
            test_result["error"] = str(e)
            self.log(f"IPFS direct upload failed: {e}", "FAIL")

        return test_result

    def test_lighthouse_upload(
        self, data: bytes, filename: str, data_type: str
    ) -> dict:
        """Test Lighthouse Storage upload"""
        if not self.lighthouse_client:
            return {
                "method": "lighthouse",
                "type": data_type,
                "success": False,
                "error": "Lighthouse client not available",
                "duration": 0,
            }

        self.log(f"Testing Lighthouse upload: {filename}")

        test_result = {
            "method": "lighthouse",
            "type": data_type,
            "filename": filename,
            "size": len(data),
            "success": False,
            "cid": None,
            "error": None,
            "duration": 0,
        }

        start_time = time.time()

        try:
            if data_type == "json":
                json_data = json.loads(data.decode("utf-8"))
                cid = self.lighthouse_client.upload_json(
                    json_data, filename.replace(".json", "")
                )
            else:
                cid = self.lighthouse_client.upload_file(data, filename)

            test_result["duration"] = time.time() - start_time
            test_result["success"] = True
            test_result["cid"] = cid
            self.log(f"Lighthouse upload successful: {cid}", "PASS")

        except Exception as e:
            test_result["duration"] = time.time() - start_time
            test_result["error"] = str(e)
            self.log(f"Lighthouse upload failed: {e}", "FAIL")

        return test_result

    def test_filecoin_pin_upload(
        self, data: bytes, filename: str, data_type: str
    ) -> dict:
        """Test Filecoin Pin CLI upload"""
        if not self.filecoin_pin_client:
            return {
                "method": "filecoin_pin",
                "type": data_type,
                "success": False,
                "error": "Filecoin Pin client not available",
                "duration": 0,
            }

        self.log(f"Testing Filecoin Pin CLI upload: {filename}")

        test_result = {
            "method": "filecoin_pin",
            "type": data_type,
            "filename": filename,
            "size": len(data),
            "success": False,
            "cid": None,
            "error": None,
            "duration": 0,
        }

        start_time = time.time()

        try:
            if data_type == "json":
                json_data = json.loads(data.decode("utf-8"))
                cid = self.filecoin_pin_client.upload_json(
                    json_data, filename.replace(".json", "")
                )
            else:
                cid = self.filecoin_pin_client.upload_file(data, filename)

            test_result["duration"] = time.time() - start_time
            test_result["success"] = True
            test_result["cid"] = cid
            self.log(f"Filecoin Pin CLI upload successful: {cid}", "PASS")

        except Exception as e:
            test_result["duration"] = time.time() - start_time
            test_result["error"] = str(e)
            self.log(f"Filecoin Pin CLI upload failed: {e}", "FAIL")

        return test_result

    def test_download_verification(
        self, cid: str, original_data: bytes, method: str
    ) -> dict:
        """Test downloading and verifying uploaded content"""
        self.log(f"Testing download verification for {method}")

        test_result = {
            "method": method,
            "type": "download_verification",
            "cid": cid,
            "success": False,
            "error": None,
            "data_matches": False,
            "duration": 0,
        }

        start_time = time.time()

        try:
            if method == "filecoin_bridge":
                response = requests.post(
                    f"{self.bridge_url}/download", json={"pieceCid": cid}, timeout=60
                )

                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        import base64

                        downloaded_data = base64.b64decode(result.get("content", ""))
                        test_result["data_matches"] = downloaded_data == original_data
                        test_result["success"] = True
                    else:
                        test_result["error"] = result.get("error")
                else:
                    test_result["error"] = f"HTTP {response.status_code}"

            elif method == "ipfs_direct":
                downloaded_data = self.ipfs_client.download_file(cid)
                test_result["data_matches"] = downloaded_data == original_data
                test_result["success"] = True

            elif method == "lighthouse":
                downloaded_data = self.lighthouse_client.download_file(cid)
                test_result["data_matches"] = downloaded_data == original_data
                test_result["success"] = True

            elif method == "filecoin_pin":
                downloaded_data = self.filecoin_pin_client.download_file(cid)
                test_result["data_matches"] = downloaded_data == original_data
                test_result["success"] = True

            test_result["duration"] = time.time() - start_time

            if test_result["success"]:
                if test_result["data_matches"]:
                    self.log(f"Download verification passed for {method}", "PASS")
                else:
                    self.log(
                        f"Download verification failed - data mismatch for {method}",
                        "FAIL",
                    )
            else:
                self.log(
                    f"Download verification failed for {method}: {test_result['error']}",
                    "FAIL",
                )

        except Exception as e:
            test_result["duration"] = time.time() - start_time
            test_result["error"] = str(e)
            self.log(f"Download verification exception for {method}: {e}", "FAIL")

        return test_result

    def run_comprehensive_test(self):
        """Run comprehensive upload tests"""
        self.log("🚀 Starting comprehensive upload tests")
        self.log("=" * 50)

        # Test 1: Bridge Health Check
        bridge_healthy = self.test_bridge_health()

        # Test 2: Bridge Balance Check
        balances = self.test_bridge_balance()
        has_funds = float(balances.get("USDFC", "0")) > 0

        # Test 3: Check all available clients
        ipfs_status = self.ipfs_client.get_status()
        self.log(f"IPFS Direct status: {ipfs_status}")

        if self.lighthouse_client:
            try:
                lighthouse_info = self.lighthouse_client.get_storage_info()
                self.log(
                    f"Lighthouse available: {lighthouse_info.get('success', False)}"
                )
            except:
                self.log("Lighthouse client failed to initialize", "WARN")

        if self.filecoin_pin_client:
            try:
                pin_auth = self.filecoin_pin_client.test_authentication()
                self.log(f"Filecoin Pin CLI available: {pin_auth}")
            except:
                self.log("Filecoin Pin CLI failed to initialize", "WARN")

        # Create test data
        test_image = self.create_test_image(200, 200, (0, 255, 0))  # Green test image
        test_json = self.create_test_json("comprehensive_test")
        test_json_bytes = json.dumps(test_json, indent=2).encode("utf-8")

        # Test 4: Filecoin Image Upload (if bridge is healthy and has funds)
        if bridge_healthy and has_funds:
            filecoin_image_result = self.test_filecoin_image_upload(
                test_image, "test_image.png"
            )
            self.results["tests"].append(filecoin_image_result)

            # Verify download if upload was successful
            if filecoin_image_result["success"]:
                download_result = self.test_download_verification(
                    filecoin_image_result["cid"], test_image, "filecoin_bridge"
                )
                self.results["tests"].append(download_result)
        else:
            self.log("Skipping Filecoin tests - bridge not ready or no funds", "WARN")

        # Test 5: Filecoin JSON Upload (if bridge is healthy and has funds)
        if bridge_healthy and has_funds:
            filecoin_json_result = self.test_filecoin_json_upload(
                test_json, "test_metadata"
            )
            self.results["tests"].append(filecoin_json_result)

        # Test 6: Lighthouse Storage Upload
        if self.lighthouse_client:
            lighthouse_image_result = self.test_lighthouse_upload(
                test_image, "test_image.png", "image"
            )
            self.results["tests"].append(lighthouse_image_result)

            if lighthouse_image_result["success"]:
                download_result = self.test_download_verification(
                    lighthouse_image_result["cid"], test_image, "lighthouse"
                )
                self.results["tests"].append(download_result)

            lighthouse_json_result = self.test_lighthouse_upload(
                test_json_bytes, "test_metadata.json", "json"
            )
            self.results["tests"].append(lighthouse_json_result)

        # Test 7: Filecoin Pin CLI Upload
        if self.filecoin_pin_client:
            pin_image_result = self.test_filecoin_pin_upload(
                test_image, "test_image.png", "image"
            )
            self.results["tests"].append(pin_image_result)

            if pin_image_result["success"]:
                download_result = self.test_download_verification(
                    pin_image_result["cid"], test_image, "filecoin_pin"
                )
                self.results["tests"].append(download_result)

            pin_json_result = self.test_filecoin_pin_upload(
                test_json_bytes, "test_metadata.json", "json"
            )
            self.results["tests"].append(pin_json_result)

        # Test 8: IPFS Direct Upload
        ipfs_image_result = self.test_ipfs_direct_upload(
            test_image, "test_image.png", "image"
        )
        self.results["tests"].append(ipfs_image_result)

        # Verify IPFS direct download if upload was successful
        if ipfs_image_result["success"]:
            download_result = self.test_download_verification(
                ipfs_image_result["cid"], test_image, "ipfs_direct"
            )
            self.results["tests"].append(download_result)

        # Test 9: IPFS Direct JSON Upload
        ipfs_json_result = self.test_ipfs_direct_upload(
            test_json_bytes, "test_metadata.json", "json"
        )
        self.results["tests"].append(ipfs_json_result)

        # Generate summary
        self._generate_summary()

        # Save results
        self._save_results()

        self.log("=" * 50)
        self.log("🏁 Comprehensive tests completed")
        self._print_summary()

    def _generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.results["tests"])
        passed_tests = sum(1 for test in self.results["tests"] if test["success"])
        failed_tests = total_tests - passed_tests

        # Group by method
        filecoin_tests = [
            t for t in self.results["tests"] if t["method"] == "filecoin_bridge"
        ]
        lighthouse_tests = [
            t for t in self.results["tests"] if t["method"] == "lighthouse"
        ]
        filecoin_pin_tests = [
            t for t in self.results["tests"] if t["method"] == "filecoin_pin"
        ]
        ipfs_tests = [t for t in self.results["tests"] if t["method"] == "ipfs_direct"]

        filecoin_success = sum(1 for t in filecoin_tests if t["success"])
        lighthouse_success = sum(1 for t in lighthouse_tests if t["success"])
        filecoin_pin_success = sum(1 for t in filecoin_pin_tests if t["success"])
        ipfs_success = sum(1 for t in ipfs_tests if t["success"])

        self.results["summary"] = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": f"{(passed_tests / total_tests * 100):.1f}%"
            if total_tests > 0
            else "0%",
            "filecoin_bridge": {
                "total": len(filecoin_tests),
                "passed": filecoin_success,
                "success_rate": f"{(filecoin_success / len(filecoin_tests) * 100):.1f}%"
                if filecoin_tests
                else "0%",
            },
            "lighthouse": {
                "total": len(lighthouse_tests),
                "passed": lighthouse_success,
                "success_rate": f"{(lighthouse_success / len(lighthouse_tests) * 100):.1f}%"
                if lighthouse_tests
                else "0%",
            },
            "filecoin_pin": {
                "total": len(filecoin_pin_tests),
                "passed": filecoin_pin_success,
                "success_rate": f"{(filecoin_pin_success / len(filecoin_pin_tests) * 100):.1f}%"
                if filecoin_pin_tests
                else "0%",
            },
            "ipfs_direct": {
                "total": len(ipfs_tests),
                "passed": ipfs_success,
                "success_rate": f"{(ipfs_success / len(ipfs_tests) * 100):.1f}%"
                if ipfs_tests
                else "0%",
            },
        }

    def _save_results(self):
        """Save test results to file"""
        results_file = Path(__file__).parent / "test_results.json"
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2)
        self.log(f"Results saved to: {results_file}")

    def _print_summary(self):
        """Print test summary"""
        summary = self.results["summary"]

        print("\n📊 TEST SUMMARY")
        print("=" * 40)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']} ✅")
        print(f"Failed: {summary['failed']} ❌")
        print(f"Success Rate: {summary['success_rate']}")
        print("")
        print("📈 BY METHOD:")
        if summary["filecoin_bridge"]["total"] > 0:
            print(
                f"Filecoin Bridge: {summary['filecoin_bridge']['passed']}/{summary['filecoin_bridge']['total']} ({summary['filecoin_bridge']['success_rate']})"
            )
        if summary["lighthouse"]["total"] > 0:
            print(
                f"Lighthouse Storage: {summary['lighthouse']['passed']}/{summary['lighthouse']['total']} ({summary['lighthouse']['success_rate']})"
            )
        if summary["filecoin_pin"]["total"] > 0:
            print(
                f"Filecoin Pin CLI: {summary['filecoin_pin']['passed']}/{summary['filecoin_pin']['total']} ({summary['filecoin_pin']['success_rate']})"
            )
        print(
            f"IPFS Direct: {summary['ipfs_direct']['passed']}/{summary['ipfs_direct']['total']} ({summary['ipfs_direct']['success_rate']})"
        )
        print("")

        # Recommendations
        if summary["lighthouse"]["total"] > 0 and summary["lighthouse"]["passed"] > 0:
            print("🏮 RECOMMENDATION: Lighthouse Storage is working!")
            print("   Excellent choice for production use with Filecoin backing.")

        if (
            summary["filecoin_pin"]["total"] > 0
            and summary["filecoin_pin"]["passed"] > 0
        ):
            print("⚡ RECOMMENDATION: Filecoin Pin CLI is working!")
            print("   Direct Filecoin storage with cryptographic proofs.")

        if (
            summary["filecoin_bridge"]["total"] > 0
            and summary["filecoin_bridge"]["passed"] == 0
        ):
            print("💡 NOTE: Filecoin Bridge uploads are failing.")
            print("   This is expected due to authorization issues.")

        if summary["ipfs_direct"]["passed"] > 0:
            print("✅ IPFS Direct is working - suitable for production use.")

        if summary["passed"] == summary["total_tests"]:
            print("🎉 ALL TESTS PASSED! Both methods are working correctly.")


def main():
    """Main test runner"""
    tester = UploadTester()
    tester.run_comprehensive_test()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test runner failed: {e}")
