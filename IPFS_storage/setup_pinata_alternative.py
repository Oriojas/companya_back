#!/usr/bin/env python3
"""
Pinata IPFS Setup Script - Alternative to Filecoin Cloud
Easy setup for NFT metadata storage using Pinata's reliable IPFS service
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv


# Colors for terminal output
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    END = "\033[0m"


def print_header():
    """Print setup header"""
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("=" * 60)
    print("🍍 PINATA IPFS SETUP - NFT METADATA STORAGE")
    print("=" * 60)
    print(f"{Colors.END}")
    print(
        f"{Colors.WHITE}Alternative to Filecoin Cloud - Reliable and Easy to Use{Colors.END}\n"
    )


def print_step(step: int, title: str):
    """Print step header"""
    print(f"{Colors.MAGENTA}{Colors.BOLD}Step {step}: {title}{Colors.END}")
    print("-" * 40)


def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")


def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}❌ {message}{Colors.END}")


def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")


def print_info(message: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")


def get_pinata_credentials() -> Dict[str, str]:
    """Get Pinata credentials from user input"""
    print(f"{Colors.CYAN}📋 Pinata API Credentials Setup{Colors.END}")
    print()

    print("🔗 To get your Pinata API credentials:")
    print("   1. Go to: https://app.pinata.cloud/developers/api-keys")
    print("   2. Sign up for free (1GB storage included)")
    print("   3. Create a new API key with full permissions")
    print("   4. Copy the API Key and Secret API Key")
    print()

    api_key = input("🔑 Enter your Pinata API Key: ").strip()
    if not api_key:
        print_error("API Key cannot be empty!")
        return {}

    secret_key = input("🔐 Enter your Pinata Secret API Key: ").strip()
    if not secret_key:
        print_error("Secret API Key cannot be empty!")
        return {}

    return {"api_key": api_key, "secret_key": secret_key}


def test_pinata_connection(api_key: str, secret_key: str) -> bool:
    """Test Pinata API connection"""
    try:
        headers = {
            "pinata_api_key": api_key,
            "pinata_secret_api_key": secret_key,
            "Content-Type": "application/json",
        }

        response = requests.get(
            "https://api.pinata.cloud/data/testAuthentication",
            headers=headers,
            timeout=10,
        )

        if response.status_code == 200:
            result = response.json()
            return (
                result.get("message")
                == "Congratulations! You are communicating with the Pinata API!"
            )
        else:
            print_error(f"Authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except requests.RequestException as e:
        print_error(f"Connection error: {e}")
        return False


def get_account_info(api_key: str, secret_key: str) -> Optional[Dict[str, Any]]:
    """Get Pinata account information"""
    try:
        headers = {"pinata_api_key": api_key, "pinata_secret_api_key": secret_key}

        response = requests.get(
            "https://api.pinata.cloud/data/userPinnedDataTotal",
            headers=headers,
            timeout=10,
        )

        if response.status_code == 200:
            return response.json()
        else:
            return None

    except requests.RequestException:
        return None


def update_env_file(credentials: Dict[str, str]) -> bool:
    """Update .env file with Pinata credentials"""
    env_path = Path(".env")
    env_example_path = Path(".env.example")

    # Create .env from example if it doesn't exist
    if not env_path.exists() and env_example_path.exists():
        print_info("Creating .env from .env.example...")
        env_content = env_example_path.read_text()
    elif env_path.exists():
        env_content = env_path.read_text()
    else:
        # Create minimal .env
        env_content = """# Storage Provider Configuration
STORAGE_PROVIDER=pinata

# Pinata IPFS Configuration
PINATA_API_KEY=your_api_key_here
PINATA_SECRET_API_KEY=your_secret_key_here
"""

    # Update the content
    lines = env_content.split("\n")
    updated_lines = []

    # Track which variables we've updated
    updated_vars = set()

    for line in lines:
        if line.startswith("STORAGE_PROVIDER="):
            updated_lines.append("STORAGE_PROVIDER=pinata")
            updated_vars.add("STORAGE_PROVIDER")
        elif line.startswith("PINATA_API_KEY="):
            updated_lines.append(f"PINATA_API_KEY={credentials['api_key']}")
            updated_vars.add("PINATA_API_KEY")
        elif line.startswith("PINATA_SECRET_API_KEY="):
            updated_lines.append(f"PINATA_SECRET_API_KEY={credentials['secret_key']}")
            updated_vars.add("PINATA_SECRET_API_KEY")
        else:
            updated_lines.append(line)

    # Add missing variables
    if "STORAGE_PROVIDER" not in updated_vars:
        updated_lines.append("\n# Storage Provider Configuration")
        updated_lines.append("STORAGE_PROVIDER=pinata")

    if "PINATA_API_KEY" not in updated_vars:
        updated_lines.append("\n# Pinata IPFS Configuration")
        updated_lines.append(f"PINATA_API_KEY={credentials['api_key']}")

    if "PINATA_SECRET_API_KEY" not in updated_vars:
        updated_lines.append(f"PINATA_SECRET_API_KEY={credentials['secret_key']}")

    # Write updated content
    try:
        with open(env_path, "w") as f:
            f.write("\n".join(updated_lines))
        return True
    except Exception as e:
        print_error(f"Failed to update .env file: {e}")
        return False


def test_upload_functionality() -> bool:
    """Test basic upload functionality with Pinata"""
    try:
        # Load environment variables
        load_dotenv(override=True)

        # Import the Pinata client
        sys.path.append(str(Path(__file__).parent / "modules"))
        from pinata_client import PinataClient

        print_info("Testing upload functionality...")

        # Initialize client
        client = PinataClient()

        # Test with a small text file
        test_content = b"Hello Pinata! This is a test upload from the setup script."
        test_filename = f"pinata_test_{int(time.time())}.txt"

        # Upload test file
        cid = client.upload_file(test_content, test_filename)
        print_success(f"Test file uploaded successfully!")
        print_info(f"   CID: {cid}")
        print_info(f"   IPFS URI: {client.get_ipfs_uri(cid)}")
        print_info(f"   Gateway URL: {client.get_gateway_url(cid)}")

        # Test JSON upload
        test_metadata = {
            "name": "Pinata Setup Test NFT",
            "description": "Test metadata created during Pinata setup",
            "attributes": [
                {"trait_type": "Setup", "value": "Complete"},
                {"trait_type": "Provider", "value": "Pinata IPFS"},
            ],
        }

        metadata_cid = client.upload_json(test_metadata, "setup_test_metadata")
        print_success("Test metadata uploaded successfully!")
        print_info(f"   CID: {metadata_cid}")
        print_info(f"   IPFS URI: {client.get_ipfs_uri(metadata_cid)}")

        return True

    except Exception as e:
        print_error(f"Upload test failed: {e}")
        return False


def create_sample_nft():
    """Create a sample NFT to demonstrate the system"""
    try:
        print_info("Creating sample NFT demonstration...")

        # Load modules
        sys.path.append(str(Path(__file__).parent / "modules"))
        from metadata_builder import build_nft_metadata
        from pinata_client import PinataClient

        client = PinataClient()

        # Create a simple SVG image
        svg_content = """<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
  <rect width="200" height="200" fill="#4A90E2"/>
  <circle cx="100" cy="100" r="50" fill="#FFD700"/>
  <text x="100" y="180" text-anchor="middle" fill="white" font-family="Arial" font-size="16">
    Sample NFT
  </text>
</svg>"""

        # Upload image
        svg_bytes = svg_content.encode("utf-8")
        image_cid = client.upload_file(svg_bytes, "sample_nft.svg")
        image_uri = client.get_ipfs_uri(image_cid)

        # Create metadata
        metadata = build_nft_metadata(
            name="Pinata Setup Demo NFT",
            description="This is a demo NFT created during Pinata IPFS setup to test the system functionality.",
            image_uri=image_uri,
            actividad="Setup Demo",
            usuario="System Setup",
            acompanante="Pinata IPFS",
            tiempo=1,
        )

        # Upload metadata
        metadata_cid = client.upload_json(metadata, "sample_nft_metadata")
        token_uri = client.get_ipfs_uri(metadata_cid)

        print_success("Sample NFT created successfully!")
        print()
        print(f"{Colors.CYAN}🎨 Your Sample NFT:{Colors.END}")
        print(f"   Name: {metadata['name']}")
        print(f"   Image URI: {image_uri}")
        print(f"   Token URI: {token_uri}")
        print(f"   Gateway URL: {client.get_gateway_url(metadata_cid)}")
        print()
        print_info("You can use the Token URI in your smart contracts!")

        return True

    except Exception as e:
        print_error(f"Sample NFT creation failed: {e}")
        return False


def show_final_instructions():
    """Show final usage instructions"""
    print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 PINATA SETUP COMPLETE!{Colors.END}")
    print("=" * 50)

    print(f"{Colors.CYAN}📋 Next Steps:{Colors.END}")
    print("1. Run your Streamlit app:")
    print("   streamlit run app.py")
    print()
    print("2. In the app, select 'Pinata IPFS' as your storage provider")
    print()
    print("3. Upload your NFT images and generate metadata")
    print()

    print(f"{Colors.CYAN}🔗 Useful Links:{Colors.END}")
    print("• Pinata Dashboard: https://app.pinata.cloud/")
    print("• Pinata Docs: https://docs.pinata.cloud/")
    print("• IPFS Gateway: https://gateway.pinata.cloud/ipfs/[CID]")
    print()

    print(f"{Colors.CYAN}💡 Tips:{Colors.END}")
    print("• Free account includes 1GB storage and 1GB bandwidth/month")
    print("• Optimize images before upload to save space")
    print("• Keep backup of important CIDs")
    print("• Monitor usage in Pinata dashboard")
    print()

    print(f"{Colors.YELLOW}📊 Account Limits (Free Plan):{Colors.END}")
    print("• Storage: 1GB")
    print("• Bandwidth: 1GB/month")
    print("• Max file size: 100MB")
    print("• Requests: 1000/month")


def main():
    """Main setup function"""
    print_header()

    # Step 1: Get credentials
    print_step(1, "Getting Pinata API Credentials")
    credentials = get_pinata_credentials()

    if not credentials:
        print_error("Setup cancelled. No credentials provided.")
        return

    print()

    # Step 2: Test connection
    print_step(2, "Testing Pinata Connection")
    print_info("Verifying your API credentials...")

    if not test_pinata_connection(credentials["api_key"], credentials["secret_key"]):
        print_error("Failed to connect to Pinata. Please check your credentials.")
        return

    print_success("Connection successful!")

    # Get account info
    account_info = get_account_info(credentials["api_key"], credentials["secret_key"])
    if account_info:
        pin_count = account_info.get("pin_count", "N/A")
        pin_size = account_info.get("pin_size_total", 0)
        pin_size_mb = round(pin_size / (1024 * 1024), 2) if pin_size else 0

        print_info(f"Account Info: {pin_count} files, {pin_size_mb} MB used")

    print()

    # Step 3: Update configuration
    print_step(3, "Updating Configuration")
    print_info("Saving credentials to .env file...")

    if not update_env_file(credentials):
        print_error("Failed to update configuration.")
        return

    print_success("Configuration saved successfully!")
    print()

    # Step 4: Test functionality
    print_step(4, "Testing Upload Functionality")

    if not test_upload_functionality():
        print_warning("Upload test failed, but basic setup is complete.")
        print_info("You can still try using the Streamlit app.")
    else:
        print_success("Upload functionality working perfectly!")

    print()

    # Step 5: Create sample NFT
    print_step(5, "Creating Sample NFT (Optional)")

    try_sample = (
        input(
            f"{Colors.CYAN}Create a sample NFT to test the system? (y/N): {Colors.END}"
        )
        .strip()
        .lower()
    )

    if try_sample in ["y", "yes"]:
        create_sample_nft()
    else:
        print_info("Skipping sample NFT creation.")

    print()

    # Final instructions
    show_final_instructions()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Setup cancelled by user.{Colors.END}")
    except Exception as e:
        print_error(f"Setup failed with error: {e}")
        print_info("Please try running the setup again or check the documentation.")
