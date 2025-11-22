#!/usr/bin/env python3
"""
Filecoin RPC Configuration Fixer
Automatically updates .env file with working RPC endpoints
"""

import os
import time
from typing import List, Optional, Tuple

import requests

# Working RPC endpoints from official Filecoin docs
FILECOIN_RPC_ENDPOINTS = [
    "https://api.calibration.node.glif.io/rpc/v1",
    "https://rpc.ankr.com/filecoin_testnet",
    "https://filecoin-calibration.chainstacklabs.com/rpc/v1",
    "https://calibration.filfox.info/rpc/v1",
]


def test_rpc_endpoint(
    url: str, timeout: int = 10
) -> Tuple[bool, Optional[str], Optional[float]]:
    """
    Test if RPC endpoint is working
    Returns: (is_working, version, response_time)
    """
    test_payload = {
        "jsonrpc": "2.0",
        "method": "Filecoin.Version",
        "params": [],
        "id": 1,
    }

    try:
        start_time = time.time()
        response = requests.post(
            url,
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=timeout,
        )
        response_time = time.time() - start_time

        if response.status_code == 200:
            result = response.json()
            if "result" in result and "Version" in result["result"]:
                return True, result["result"]["Version"], response_time

        return (
            False,
            f"HTTP {response.status_code}: {response.text[:100]}",
            response_time,
        )

    except requests.exceptions.Timeout:
        return False, "Connection timeout", timeout
    except requests.exceptions.ConnectionError:
        return False, "Connection error", None
    except Exception as e:
        return False, str(e), None


def find_best_rpc() -> Optional[str]:
    """
    Find the fastest working RPC endpoint
    """
    print("🔍 Testing Filecoin RPC endpoints...")
    print("=" * 60)

    working_endpoints = []

    for i, endpoint in enumerate(FILECOIN_RPC_ENDPOINTS, 1):
        print(f"{i}. Testing {endpoint}")
        is_working, info, response_time = test_rpc_endpoint(endpoint)

        if is_working:
            print(f"   ✅ Working - Version: {info}")
            print(f"   ⚡ Response time: {response_time:.2f}s")
            working_endpoints.append((endpoint, response_time))
        else:
            print(f"   ❌ Failed - {info}")
        print()

    if not working_endpoints:
        print("❌ No working RPC endpoints found!")
        return None

    # Sort by response time and return the fastest
    working_endpoints.sort(key=lambda x: x[1])
    best_endpoint = working_endpoints[0][0]

    print(f"🎯 Best endpoint: {best_endpoint}")
    print(f"   Response time: {working_endpoints[0][1]:.2f}s")

    return best_endpoint


def update_env_file(new_rpc_url: str) -> bool:
    """
    Update .env file with new RPC URL
    """
    env_path = ".env"
    env_example_path = ".env.example"

    # Check if .env exists, if not create from .env.example
    if not os.path.exists(env_path):
        if os.path.exists(env_example_path):
            print("📋 Creating .env from .env.example...")
            with open(env_example_path, "r") as f:
                content = f.read()
            with open(env_path, "w") as f:
                f.write(content)
        else:
            print("❌ Neither .env nor .env.example found!")
            return False

    # Read current .env content
    with open(env_path, "r") as f:
        lines = f.readlines()

    # Update FILECOIN_RPC_URL and STORAGE_PROVIDER
    updated_lines = []
    rpc_updated = False
    provider_updated = False

    for line in lines:
        if line.startswith("FILECOIN_RPC_URL="):
            updated_lines.append(f"FILECOIN_RPC_URL={new_rpc_url}\n")
            rpc_updated = True
        elif line.startswith("STORAGE_PROVIDER="):
            updated_lines.append("STORAGE_PROVIDER=filecoin\n")
            provider_updated = True
        else:
            updated_lines.append(line)

    # Add missing variables if they don't exist
    if not rpc_updated:
        updated_lines.append(f"\n# Filecoin Configuration\n")
        updated_lines.append(f"FILECOIN_RPC_URL={new_rpc_url}\n")

    if not provider_updated:
        updated_lines.append("STORAGE_PROVIDER=filecoin\n")

    # Write updated content
    with open(env_path, "w") as f:
        f.writelines(updated_lines)

    print(f"✅ Updated .env file:")
    print(f"   FILECOIN_RPC_URL={new_rpc_url}")
    print(f"   STORAGE_PROVIDER=filecoin")

    return True


def validate_configuration():
    """
    Validate current configuration
    """
    print("\n🔧 Validating configuration...")

    # Check environment variables
    rpc_url = os.getenv("FILECOIN_RPC_URL")
    private_key = os.getenv("FILECOIN_PRIVATE_KEY")
    bridge_url = os.getenv("FILECOIN_BRIDGE_URL", "http://localhost:3001")

    if not rpc_url:
        print("❌ FILECOIN_RPC_URL not set")
        return False

    if not private_key:
        print("❌ FILECOIN_PRIVATE_KEY not set")
        print("💡 You need to add your private key to .env file")
        return False

    # Test RPC connection with new URL
    print(f"🔗 Testing RPC connection: {rpc_url}")
    is_working, info, response_time = test_rpc_endpoint(rpc_url)

    if is_working:
        print(f"✅ RPC connection successful")
        print(f"   Version: {info}")
        return True
    else:
        print(f"❌ RPC connection failed: {info}")
        return False


def main():
    """
    Main function to fix Filecoin RPC configuration
    """
    print("🚀 Filecoin RPC Configuration Fixer")
    print("=" * 50)
    print()

    # Find best working RPC endpoint
    best_rpc = find_best_rpc()

    if not best_rpc:
        print("\n❌ Could not find any working RPC endpoints.")
        print("💡 This might be a temporary network issue. Try again later.")
        return

    print("\n📝 Updating configuration...")
    if update_env_file(best_rpc):
        print("\n✅ Configuration updated successfully!")
    else:
        print("\n❌ Failed to update configuration.")
        return

    print("\n🔄 Reloading environment variables...")
    # Load updated environment variables
    from dotenv import load_dotenv

    load_dotenv(override=True)

    # Validate configuration
    if validate_configuration():
        print("\n🎉 Filecoin RPC configuration fixed successfully!")
        print("\n📋 Next steps:")
        print("1. Make sure your FILECOIN_PRIVATE_KEY is set in .env")
        print("2. Get test tokens from: https://faucet.calibration.fildev.network/")
        print("3. Start the bridge service: cd bridge && npm start")
        print("4. Run the diagnostic: python troubleshoot_filecoin.py")
    else:
        print("\n⚠️  Configuration updated but validation failed.")
        print("   Check your private key and other settings.")


if __name__ == "__main__":
    main()
