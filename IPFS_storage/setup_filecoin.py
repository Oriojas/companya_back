#!/usr/bin/env python3
"""
Filecoin Cloud Setup and Funding Script
Helps setup and fund a Filecoin account for IPFS storage
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_step(step_num, title):
    """Print a formatted step"""
    print(f"\n📋 Step {step_num}: {title}")
    print("-" * 40)


def check_node_js():
    """Check if Node.js is installed"""
    try:
        result = subprocess.run(
            ["node", "--version"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            major_version = int(version.replace("v", "").split(".")[0])
            if major_version >= 18:
                print(f"✅ Node.js {version} found")
                return True
            else:
                print(f"❌ Node.js {version} found, but version 18+ required")
                return False
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
        pass

    print("❌ Node.js not found or version check failed")
    print("Please install Node.js 18+ from: https://nodejs.org/")
    return False


def setup_bridge_service():
    """Setup the Node.js bridge service"""
    print_step(1, "Setting up Node.js Bridge Service")

    bridge_dir = Path("bridge")
    if not bridge_dir.exists():
        print("❌ Bridge directory not found")
        return False

    # Change to bridge directory
    original_dir = os.getcwd()
    try:
        os.chdir(bridge_dir)

        # Run setup script
        if Path("setup.sh").exists():
            print("🔧 Running bridge setup script...")
            result = subprocess.run(
                ["bash", "setup.sh"], capture_output=True, text=True
            )
            if result.returncode == 0:
                print("✅ Bridge service setup completed")
            else:
                print(f"❌ Bridge setup failed: {result.stderr}")
                return False
        else:
            # Manual npm install
            print("📦 Installing Node.js dependencies...")
            result = subprocess.run(["npm", "install"], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Dependencies installed successfully")
            else:
                print(f"❌ npm install failed: {result.stderr}")
                return False

        return True

    finally:
        os.chdir(original_dir)


def check_environment_variables():
    """Check if required environment variables are set"""
    print_step(2, "Checking Environment Configuration")

    private_key = os.getenv("FILECOIN_PRIVATE_KEY")
    rpc_url = os.getenv("FILECOIN_RPC_URL")

    if not private_key:
        print("❌ FILECOIN_PRIVATE_KEY not found in .env")
        print("Please add your Filecoin private key to .env file")
        print("Example: FILECOIN_PRIVATE_KEY=your_private_key_without_0x")
        return False

    if not rpc_url:
        print("⚠️  FILECOIN_RPC_URL not set, using default Calibration testnet")
        rpc_url = "https://filecoin-calibration.chainup.net/rpc/v1"

    print("✅ Environment variables configured")
    print(f"   Private key: {private_key[:10]}...{private_key[-10:]}")
    print(f"   RPC URL: {rpc_url}")
    return True


def start_bridge_service():
    """Start the bridge service"""
    print_step(3, "Starting Bridge Service")

    bridge_dir = Path("bridge")
    if not bridge_dir.exists():
        print("❌ Bridge directory not found")
        return None

    # Check if service is already running
    try:
        response = requests.get("http://localhost:3001/health", timeout=3)
        if response.status_code == 200:
            print("✅ Bridge service is already running")
            return True
    except requests.exceptions.RequestException:
        pass

    # Start the service
    print("🚀 Starting bridge service...")

    original_dir = os.getcwd()
    try:
        os.chdir(bridge_dir)

        # Start service in background
        env = os.environ.copy()
        env["FILECOIN_PRIVATE_KEY"] = os.getenv("FILECOIN_PRIVATE_KEY")
        env["FILECOIN_RPC_URL"] = os.getenv(
            "FILECOIN_RPC_URL", "https://filecoin-calibration.chainup.net/rpc/v1"
        )

        process = subprocess.Popen(
            ["node", "server.js"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Wait for service to start
        print("⏳ Waiting for service to initialize...")
        for i in range(15):  # Wait up to 15 seconds
            try:
                response = requests.get("http://localhost:3001/health", timeout=1)
                if response.status_code == 200:
                    print("✅ Bridge service started successfully")
                    return process
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
            print(f"   ... waiting ({i + 1}/15)")

        print("❌ Bridge service failed to start in time")
        process.terminate()
        return None

    except Exception as e:
        print(f"❌ Failed to start bridge service: {e}")
        return None
    finally:
        os.chdir(original_dir)


def test_connection():
    """Test connection to Filecoin Cloud"""
    print_step(4, "Testing Filecoin Connection")

    try:
        # Test authentication
        response = requests.post(
            "http://localhost:3001/test", json={"action": "test_auth"}, timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Connection to Filecoin Cloud successful")
                print(f"   Providers available: {result.get('providers', 'N/A')}")
                return True
            else:
                print("❌ Connection test failed")
                return False
        else:
            print(f"❌ Connection test failed: HTTP {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Connection test failed: {e}")
        return False


def check_wallet_balance():
    """Check wallet balance"""
    print_step(5, "Checking Wallet Balance")

    try:
        response = requests.get("http://localhost:3001/balance", timeout=10)

        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                balances = result.get("balances", {})
                usdfc_balance = float(balances.get("USDFC", "0"))
                fil_balance = float(balances.get("FIL", "0"))

                print("💰 Current wallet balances:")
                print(f"   USDFC: {usdfc_balance:.6f}")
                print(f"   FIL: {fil_balance:.6f}")

                if usdfc_balance < 0.1:
                    print("⚠️  Low USDFC balance detected")
                    print("   You may need more USDFC for storage operations")

                if fil_balance < 0.001:
                    print("⚠️  Low FIL balance detected")
                    print("   You may need more FIL for gas fees")

                return True
            else:
                print("❌ Failed to get balance information")
                return False
        else:
            print(f"❌ Balance check failed: HTTP {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Balance check failed: {e}")
        return False


def get_test_tokens():
    """Provide instructions for getting test tokens"""
    print_step(6, "Getting Test Tokens")

    print("🪙 To use Filecoin Cloud, you need test tokens:")
    print("")
    print("1. 💧 Get tFIL (for gas fees):")
    print("   Visit: https://faucet.calibration.fildev.network/")
    print("   Request tFIL tokens for your wallet address")
    print("")
    print("2. 💵 Get USDFC (for storage payments):")
    print("   Visit: https://faucet.calibration.fildev.network/")
    print("   Request USDFC tokens for your wallet address")
    print("")
    print("3. ⏰ Wait for tokens to arrive (may take a few minutes)")
    print("")

    # Try to get wallet address from the service
    try:
        response = requests.get("http://localhost:3001/info", timeout=5)
        if response.status_code == 200:
            result = response.json()
            # The wallet address would be in the SDK info if available
            print("💡 Your wallet address can be found in your Filecoin wallet")
    except:
        pass


def fund_account():
    """Help user fund their account for storage"""
    print_step(7, "Funding Storage Account")

    print("💳 Funding your account for storage operations...")

    # Ask user if they want to fund the account
    response = (
        input("\nDo you want to fund your account with 2.5 USDFC? (y/N): ")
        .strip()
        .lower()
    )

    if response != "y":
        print("⏭️  Skipping account funding")
        print("   You can fund your account later using the bridge service")
        return True

    try:
        print("💰 Attempting to fund account with 2.5 USDFC...")
        response = requests.post(
            "http://localhost:3001/fund", json={"amount": "2.5"}, timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Account funded successfully!")
                print(f"   Transaction: {result.get('transactionHash', 'N/A')}")
                return True
            else:
                print(
                    f"❌ Account funding failed: {result.get('error', 'Unknown error')}"
                )
                return False
        else:
            print(f"❌ Account funding failed: HTTP {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Account funding failed: {e}")
        return False


def test_upload():
    """Test upload functionality"""
    print_step(8, "Testing Upload Functionality")

    print("🧪 Testing file upload...")

    # Create test data
    test_data = (
        b"Hello from Filecoin Cloud! This is a test upload to verify everything is working correctly. "
        + b"x" * 50
    )  # Ensure > 127 bytes

    try:
        # Test file upload
        files = {"file": ("test_file.txt", test_data, "text/plain")}
        data = {"filename": "test_file.txt", "metadata": json.dumps({"test": True})}

        response = requests.post(
            "http://localhost:3001/upload/file", files=files, data=data, timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                piece_cid = result.get("pieceCid")
                print(f"✅ Test upload successful!")
                print(f"   Piece CID: {piece_cid}")
                print(f"   Size: {result.get('size', 'N/A')} bytes")

                # Test download
                print("📥 Testing download...")
                download_response = requests.post(
                    "http://localhost:3001/download",
                    json={"pieceCid": piece_cid},
                    timeout=30,
                )

                if download_response.status_code == 200:
                    download_result = download_response.json()
                    if download_result.get("success"):
                        print("✅ Test download successful!")
                        return True
                    else:
                        print(f"❌ Download failed: {download_result.get('error')}")
                else:
                    print(f"❌ Download failed: HTTP {download_response.status_code}")

            else:
                print(f"❌ Upload failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ Upload failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Upload test failed: {e}")

    return False


def main():
    """Main setup function"""
    print_header("Filecoin Cloud Setup & Configuration")
    print(
        "This script will help you set up and configure Filecoin Cloud for IPFS storage"
    )

    # Check prerequisites
    if not check_node_js():
        print("\n❌ Setup failed: Node.js 18+ is required")
        return False

    # Setup steps
    success = True
    bridge_process = None

    try:
        success &= setup_bridge_service()
        success &= check_environment_variables()

        if success:
            bridge_process = start_bridge_service()
            success = bridge_process is not None

        if success:
            success &= test_connection()
            success &= check_wallet_balance()

        if success:
            get_test_tokens()
            # Give user time to get tokens if needed
            input("\nPress Enter after you've obtained test tokens to continue...")

            # Re-check balance
            check_wallet_balance()

            success &= fund_account()
            success &= test_upload()

        if success:
            print_header("🎉 Setup Completed Successfully!")
            print("")
            print("✅ Filecoin Cloud is ready to use!")
            print("✅ Bridge service is running on http://localhost:3001")
            print("✅ Your Python application can now use FilecoinCloudClient")
            print("")
            print("📋 Next steps:")
            print("1. Keep the bridge service running")
            print("2. Use the Streamlit app with Filecoin Cloud provider")
            print("3. Monitor your wallet balance for storage costs")
            print("")
            print("🔗 Useful links:")
            print("- Filecoin Docs: https://docs.filecoin.io")
            print("- Synapse SDK: https://docs.filecoin.cloud")
            print("- Test Faucet: https://faucet.calibration.fildev.network/")
        else:
            print_header("❌ Setup Failed")
            print("Please check the errors above and try again")
            print("For help, see the README.md or contact support")

    except KeyboardInterrupt:
        print("\n👋 Setup interrupted by user")
        success = False

    finally:
        # Keep bridge service running if setup was successful
        if success and bridge_process:
            print("\n🔄 Bridge service will continue running...")
            print("Press Ctrl+C to stop the bridge service when done")
            try:
                bridge_process.wait()
            except KeyboardInterrupt:
                print("\n👋 Stopping bridge service...")
                bridge_process.terminate()
                try:
                    bridge_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    bridge_process.kill()
        elif bridge_process:
            # Clean up if setup failed
            bridge_process.terminate()

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
