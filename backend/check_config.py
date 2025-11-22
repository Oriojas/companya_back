#!/usr/bin/env python3
"""
Simple Configuration Check for NFT Backend

This script verifies that the backend is properly configured and can connect
to the contract on Arbitrum Sepolia.

Usage:
    python check_config.py
"""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from web3 import Web3


def check_configuration():
    """Check the backend configuration"""
    print("🔍 Checking backend configuration...")

    # Load environment variables
    load_dotenv()

    # Check required environment variables
    required_vars = ["PRIVATE_KEY", "RPC_URL"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("   Please check your .env file")
        return False

    print("✅ All required environment variables are set")

    # Check RPC connection
    try:
        web3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL")))
        if not web3.is_connected():
            print("❌ Cannot connect to RPC URL")
            return False

        block_number = web3.eth.block_number
        print(f"✅ Connected to Arbitrum Sepolia - Block: {block_number}")

    except Exception as e:
        print(f"❌ RPC connection error: {e}")
        return False

    # Check contract ABI
    try:
        project_root = Path(__file__).parent.parent
        artifact_path = (
            project_root
            / "artifacts"
            / "contracts"
            / "ColeccionServiciosNFT.sol"
            / "ColeccionServiciosNFT.json"
        )

        if not artifact_path.exists():
            print("❌ Contract ABI not found")
            print("   Run 'npm run compile' in the project root")
            return False

        with open(artifact_path, "r") as f:
            artifact = json.load(f)
            contract_abi = artifact["abi"]

        print(f"✅ Contract ABI loaded ({len(contract_abi)} functions)")

    except Exception as e:
        print(f"❌ Error loading contract ABI: {e}")
        return False

    # Check contract connection
    try:
        # Load contract address from deployment info
        deployment_file = project_root / "deployments" / "latest-deployment.json"
        if not deployment_file.exists():
            print("❌ Deployment information not found")
            print("   Run 'npm run deploy' in the project root")
            return False

        with open(deployment_file, "r") as f:
            deployment_info = json.load(f)

        contract_address = deployment_info["contractAddress"]
        contract = web3.eth.contract(
            address=Web3.to_checksum_address(contract_address), abi=contract_abi
        )

        # Test contract functions
        contract_name = contract.functions.name().call()
        contract_symbol = contract.functions.symbol().call()
        next_token_id = contract.functions.obtenerProximoTokenId().call()

        print(f"✅ Contract connected: {contract_name} ({contract_symbol})")
        print(f"✅ Contract address: {contract_address}")
        print(f"✅ Next Token ID: {next_token_id}")

    except Exception as e:
        print(f"❌ Error connecting to contract: {e}")
        return False

    # Check account
    try:
        private_key = os.getenv("PRIVATE_KEY")
        if private_key == "your_private_key_here_without_0x_prefix":
            print("⚠️  Using placeholder private key - replace with actual key")
        else:
            account = web3.eth.account.from_key(private_key)
            balance = web3.eth.get_balance(account.address)
            balance_eth = web3.from_wei(balance, "ether")
            print(f"✅ Account configured: {account.address}")
            print(f"✅ Account balance: {balance_eth} ETH")

            if balance_eth < 0.001:
                print("⚠️  Low balance - you may need test ETH from faucet")

    except Exception as e:
        print(f"❌ Error with account: {e}")
        return False

    return True


def main():
    """Main function"""
    print("🧪 NFT Backend Configuration Check")
    print("=" * 50)

    success = check_configuration()

    print("\n" + "=" * 50)
    if success:
        print("🎉 Configuration check passed! Backend is ready to use.")
        print("\nNext steps:")
        print("  1. Start the backend: python main.py")
        print("  2. Run tests: python tests/test_backend_completo.py")
    else:
        print("❌ Configuration check failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
