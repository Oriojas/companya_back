#!/usr/bin/env python3
"""
Filecoin Cloud Troubleshooting Script
Diagnoses and helps fix common connection issues with Filecoin Cloud
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class FilecoinTroubleshooter:
    """Comprehensive troubleshooting for Filecoin Cloud issues"""

    def __init__(self):
        self.bridge_url = os.getenv("FILECOIN_BRIDGE_URL", "http://localhost:3001")
        self.private_key = os.getenv("FILECOIN_PRIVATE_KEY")
        self.rpc_url = os.getenv(
            "FILECOIN_RPC_URL", "https://filecoin-calibration.chainup.net/rpc/v1"
        )
        self.issues_found = []
        self.solutions = []

    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "=" * 60)
        print(f"  {title}")
        print("=" * 60)

    def print_step(self, step: str):
        """Print formatted step"""
        print(f"\n🔍 {step}")
        print("-" * 40)

    def check_environment_variables(self) -> bool:
        """Check if required environment variables are set"""
        self.print_step("Checking Environment Variables")

        issues = []

        if not self.private_key:
            issues.append("FILECOIN_PRIVATE_KEY is not set")
            self.solutions.append(
                "Add FILECOIN_PRIVATE_KEY=your_private_key_without_0x to your .env file"
            )
        elif self.private_key.startswith("0x"):
            issues.append("FILECOIN_PRIVATE_KEY should not include '0x' prefix")
            self.solutions.append(
                "Remove '0x' prefix from FILECOIN_PRIVATE_KEY in .env file"
            )
        elif len(self.private_key) != 64:
            issues.append("FILECOIN_PRIVATE_KEY appears to be invalid length")
            self.solutions.append(
                "Ensure FILECOIN_PRIVATE_KEY is a valid 64-character hex string"
            )
        else:
            print(
                f"✅ FILECOIN_PRIVATE_KEY: {self.private_key[:10]}...{self.private_key[-6:]}"
            )

        if not self.rpc_url:
            issues.append("FILECOIN_RPC_URL is not set")
            self.solutions.append(
                "Add FILECOIN_RPC_URL=https://filecoin-calibration.chainup.net/rpc/v1 to .env"
            )
        else:
            print(f"✅ FILECOIN_RPC_URL: {self.rpc_url}")

        print(f"✅ FILECOIN_BRIDGE_URL: {self.bridge_url}")

        if issues:
            for issue in issues:
                print(f"❌ {issue}")
                self.issues_found.extend(issues)
            return False

        return True

    def check_node_js(self) -> bool:
        """Check if Node.js is installed and correct version"""
        self.print_step("Checking Node.js Installation")

        try:
            result = subprocess.run(
                ["node", "--version"], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                version = result.stdout.strip()
                major_version = int(version.replace("v", "").split(".")[0])

                if major_version >= 18:
                    print(f"✅ Node.js {version} found (>= 18 required)")
                    return True
                else:
                    print(f"❌ Node.js {version} found, but version 18+ required")
                    self.issues_found.append("Node.js version too old")
                    self.solutions.append(
                        "Install Node.js 18+ from https://nodejs.org/"
                    )
                    return False
            else:
                print(f"❌ Node.js command failed: {result.stderr}")

        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError) as e:
            print(f"❌ Node.js not found or error: {e}")

        self.issues_found.append("Node.js not found or invalid")
        self.solutions.append("Install Node.js 18+ from https://nodejs.org/")
        return False

    def check_bridge_directory(self) -> bool:
        """Check if bridge directory exists and is properly configured"""
        self.print_step("Checking Bridge Service Directory")

        bridge_dir = Path("bridge")

        if not bridge_dir.exists():
            print("❌ Bridge directory not found")
            self.issues_found.append("Bridge directory missing")
            self.solutions.append(
                "Ensure you're running from IPFS_storage directory with bridge/ folder"
            )
            return False

        print("✅ Bridge directory found")

        # Check required files
        required_files = ["server.js", "package.json"]
        missing_files = []

        for file in required_files:
            file_path = bridge_dir / file
            if file_path.exists():
                print(f"✅ {file} found")
            else:
                print(f"❌ {file} missing")
                missing_files.append(file)

        if missing_files:
            self.issues_found.append(
                f"Missing bridge files: {', '.join(missing_files)}"
            )
            self.solutions.append(
                "Re-run the setup or check bridge directory integrity"
            )
            return False

        return True

    def check_bridge_dependencies(self) -> bool:
        """Check if Node.js dependencies are installed"""
        self.print_step("Checking Bridge Dependencies")

        bridge_dir = Path("bridge")
        node_modules = bridge_dir / "node_modules"

        if not node_modules.exists():
            print("❌ node_modules directory not found")
            self.issues_found.append("Bridge dependencies not installed")
            self.solutions.append("Run: cd bridge && npm install")
            return False

        print("✅ node_modules directory found")

        # Check for key dependencies
        key_deps = ["@filoz/synapse-sdk", "ethers", "express"]
        missing_deps = []

        for dep in key_deps:
            dep_path = node_modules / dep
            if dep_path.exists():
                print(f"✅ {dep} installed")
            else:
                print(f"❌ {dep} missing")
                missing_deps.append(dep)

        if missing_deps:
            self.issues_found.append(f"Missing dependencies: {', '.join(missing_deps)}")
            self.solutions.append("Run: cd bridge && npm install")
            return False

        return True

    def test_rpc_connection(self) -> bool:
        """Test direct connection to Filecoin RPC"""
        self.print_step("Testing Filecoin RPC Connection")

        try:
            # Test basic RPC call
            payload = {
                "jsonrpc": "2.0",
                "method": "Filecoin.Version",
                "params": [],
                "id": 1,
            }

            response = requests.post(
                self.rpc_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )

            if response.status_code == 200:
                result = response.json()
                if "result" in result:
                    version_info = result["result"]
                    print(f"✅ RPC connection successful")
                    print(f"   Version: {version_info.get('Version', 'N/A')}")
                    print(f"   Commit: {version_info.get('Commit', 'N/A')[:8]}...")
                    return True
                else:
                    print(f"❌ Invalid RPC response: {result}")
            else:
                print(f"❌ RPC request failed: HTTP {response.status_code}")
                print(f"   Response: {response.text[:200]}...")

        except requests.RequestException as e:
            print(f"❌ RPC connection failed: {e}")

        self.issues_found.append("Cannot connect to Filecoin RPC")
        self.solutions.append("Check internet connection and RPC URL")
        return False

    def check_bridge_service(self) -> bool:
        """Check if bridge service is running"""
        self.print_step("Checking Bridge Service Status")

        try:
            response = requests.get(f"{self.bridge_url}/health", timeout=5)

            if response.status_code == 200:
                health_data = response.json()
                print("✅ Bridge service is running")
                print(f"   Status: {health_data.get('status', 'unknown')}")
                print(f"   Service: {health_data.get('service', 'unknown')}")
                return True
            else:
                print(f"❌ Bridge service responded with HTTP {response.status_code}")

        except requests.RequestException as e:
            print(f"❌ Bridge service not responding: {e}")

        self.issues_found.append("Bridge service not running")
        self.solutions.append("Start bridge service: cd bridge && npm start")
        return False

    def start_bridge_service(self) -> bool:
        """Attempt to start the bridge service"""
        self.print_step("Attempting to Start Bridge Service")

        bridge_dir = Path("bridge")

        if not bridge_dir.exists():
            print("❌ Bridge directory not found")
            return False

        try:
            # Change to bridge directory
            original_dir = os.getcwd()
            os.chdir(bridge_dir)

            print("🚀 Starting bridge service...")

            # Set up environment
            env = os.environ.copy()
            env["FILECOIN_PRIVATE_KEY"] = self.private_key
            env["FILECOIN_RPC_URL"] = self.rpc_url

            # Start the service
            process = subprocess.Popen(
                ["node", "server.js"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # Wait for service to start
            print("⏳ Waiting for service to initialize...")

            for i in range(20):  # Wait up to 20 seconds
                try:
                    response = requests.get(f"{self.bridge_url}/health", timeout=1)
                    if response.status_code == 200:
                        print("✅ Bridge service started successfully")
                        return process
                except requests.RequestException:
                    pass

                time.sleep(1)
                print(f"   ... waiting ({i + 1}/20)")

            print("❌ Bridge service failed to start in time")

            # Try to get error output
            try:
                stdout, stderr = process.communicate(timeout=1)
                if stderr:
                    print(f"   Error output: {stderr.decode()[:300]}...")
            except subprocess.TimeoutExpired:
                pass

            process.terminate()
            return False

        except Exception as e:
            print(f"❌ Failed to start bridge service: {e}")
            return False
        finally:
            os.chdir(original_dir)

    def test_bridge_authentication(self) -> bool:
        """Test authentication with the bridge service"""
        self.print_step("Testing Bridge Authentication")

        try:
            response = requests.post(
                f"{self.bridge_url}/test", json={"action": "test_auth"}, timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print("✅ Bridge authentication successful")
                    print(f"   Providers: {result.get('providers', 'N/A')}")
                    return True
                else:
                    print(
                        f"❌ Bridge authentication failed: {result.get('error', 'Unknown error')}"
                    )
            else:
                print(f"❌ Bridge test failed: HTTP {response.status_code}")
                print(f"   Response: {response.text[:200]}...")

        except requests.RequestException as e:
            print(f"❌ Bridge authentication test failed: {e}")

        self.issues_found.append("Bridge authentication failed")
        self.solutions.append("Check private key and bridge service logs")
        return False

    def check_wallet_balance(self) -> bool:
        """Check if wallet has sufficient balance"""
        self.print_step("Checking Wallet Balance")

        try:
            response = requests.get(f"{self.bridge_url}/balance", timeout=10)

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    balances = result.get("balances", {})
                    usdfc_balance = float(balances.get("USDFC", "0"))
                    fil_balance = float(balances.get("FIL", "0"))

                    print("💰 Current balances:")
                    print(f"   USDFC: {usdfc_balance:.6f}")
                    print(f"   FIL: {fil_balance:.6f}")

                    low_balance = False

                    if usdfc_balance < 0.1:
                        print("⚠️  Low USDFC balance detected")
                        self.issues_found.append("Low USDFC balance")
                        self.solutions.append(
                            "Get USDFC tokens from https://faucet.calibration.fildev.network/"
                        )
                        low_balance = True

                    if fil_balance < 0.001:
                        print("⚠️  Low FIL balance detected")
                        self.issues_found.append("Low FIL balance")
                        self.solutions.append(
                            "Get tFIL tokens from https://faucet.calibration.fildev.network/"
                        )
                        low_balance = True

                    if not low_balance:
                        print("✅ Sufficient balance for operations")

                    return True
                else:
                    print(
                        f"❌ Balance check failed: {result.get('error', 'Unknown error')}"
                    )
            else:
                print(f"❌ Balance check failed: HTTP {response.status_code}")

        except requests.RequestException as e:
            print(f"❌ Balance check failed: {e}")

        self.issues_found.append("Cannot check wallet balance")
        self.solutions.append(
            "Ensure bridge service is running and private key is correct"
        )
        return False

    def run_full_diagnosis(self) -> Dict[str, bool]:
        """Run complete diagnostic sequence"""
        self.print_header("Filecoin Cloud Diagnostic")
        print("Checking all components for common issues...")

        results = {}

        # Environment check
        results["environment"] = self.check_environment_variables()

        # Node.js check
        results["nodejs"] = self.check_node_js()

        if results["nodejs"]:
            # Bridge directory check
            results["bridge_dir"] = self.check_bridge_directory()

            if results["bridge_dir"]:
                # Dependencies check
                results["dependencies"] = self.check_bridge_dependencies()
            else:
                results["dependencies"] = False
        else:
            results["bridge_dir"] = False
            results["dependencies"] = False

        # RPC connection check
        results["rpc_connection"] = self.test_rpc_connection()

        # Bridge service check
        results["bridge_service"] = self.check_bridge_service()

        # If bridge is not running, try to start it
        if (
            not results["bridge_service"]
            and results["nodejs"]
            and results["bridge_dir"]
            and results["dependencies"]
        ):
            print("\n🔧 Attempting to start bridge service...")
            bridge_process = self.start_bridge_service()
            if bridge_process:
                results["bridge_service"] = True
                time.sleep(2)  # Give it a moment to fully initialize

        # Authentication test (if bridge is running)
        if results["bridge_service"]:
            results["authentication"] = self.test_bridge_authentication()

            # Balance check (if authentication works)
            if results["authentication"]:
                results["balance"] = self.check_wallet_balance()
            else:
                results["balance"] = False
        else:
            results["authentication"] = False
            results["balance"] = False

        return results

    def show_summary(self, results: Dict[str, bool]):
        """Show diagnostic summary and solutions"""
        self.print_header("Diagnostic Summary")

        # Show results
        print("📊 Component Status:")
        for component, status in results.items():
            icon = "✅" if status else "❌"
            print(
                f"   {icon} {component.replace('_', ' ').title()}: {'PASS' if status else 'FAIL'}"
            )

        # Overall status
        all_passed = all(results.values())
        if all_passed:
            print("\n🎉 All checks passed! Filecoin Cloud should be working.")
        else:
            print(f"\n❌ {sum(1 for v in results.values() if not v)} issues found.")

        # Show solutions
        if self.issues_found:
            self.print_header("Recommended Solutions")
            for i, solution in enumerate(self.solutions, 1):
                print(f"{i:2d}. {solution}")

        # Quick fix commands
        if not all_passed:
            self.print_header("Quick Fix Commands")

            if not results.get("dependencies"):
                print("📦 Install bridge dependencies:")
                print("   cd bridge && npm install")

            if not results.get("bridge_service"):
                print("🚀 Start bridge service:")
                print("   cd bridge && npm start")

            if "Low" in " ".join(self.issues_found):
                print("🪙 Get test tokens:")
                print("   Visit: https://faucet.calibration.fildev.network/")

        # Next steps
        self.print_header("Next Steps")
        if all_passed:
            print("1. Your Filecoin Cloud setup is ready!")
            print("2. Run the Streamlit app: streamlit run app.py")
            print("3. Select 'Filecoin Cloud' as your storage provider")
        else:
            print("1. Fix the issues listed above")
            print("2. Re-run this diagnostic: python troubleshoot_filecoin.py")
            print("3. If problems persist, check the full setup guide in README.md")


def main():
    """Main troubleshooting function"""
    troubleshooter = FilecoinTroubleshooter()

    # Run full diagnosis
    results = troubleshooter.run_full_diagnosis()

    # Show summary and recommendations
    troubleshooter.show_summary(results)

    # Return success if all checks passed
    return all(results.values())


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
