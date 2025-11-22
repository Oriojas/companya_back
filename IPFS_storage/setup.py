#!/usr/bin/env python3
"""
Setup Script for NFT IPFS Uploader
Automates the installation and configuration process
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_step(step_num, title):
    """Print a formatted step"""
    print(f"\n📋 Step {step_num}: {title}")
    print("-" * 40)


def check_python_version():
    """Check if Python version is compatible"""
    print_step(1, "Checking Python Version")

    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False

    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def install_dependencies():
    """Install required Python packages"""
    print_step(2, "Installing Dependencies")

    try:
        # Check if pip is available
        subprocess.run(
            [sys.executable, "-m", "pip", "--version"], check=True, capture_output=True
        )
        print("✅ pip is available")

        # Install requirements
        print("📦 Installing packages from requirements.txt...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("✅ All dependencies installed successfully")
            return True
        else:
            print("❌ Failed to install dependencies")
            print(f"Error: {result.stderr}")
            return False

    except subprocess.CalledProcessError as e:
        print("❌ pip is not available")
        print("Please install pip and try again")
        return False
    except FileNotFoundError:
        print("❌ requirements.txt not found")
        return False


def setup_environment():
    """Setup environment variables"""
    print_step(3, "Setting up Environment")

    env_file = Path(".env")
    env_example = Path(".env.example")

    # Check if .env already exists
    if env_file.exists():
        print("⚠️  .env file already exists")
        response = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if response != "y":
            print("✅ Keeping existing .env file")
            return True

    # Check if .env.example exists
    if not env_example.exists():
        print("❌ .env.example not found")
        return False

    # Copy .env.example to .env
    try:
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from template")

        print("\n🔑 You need to configure your Pinata API credentials:")
        print("1. Visit: https://app.pinata.cloud/developers/api-keys")
        print("2. Create a new API key")
        print("3. Edit the .env file and add your credentials:")
        print("   - PINATA_API_KEY=your_api_key")
        print("   - PINATA_SECRET_API_KEY=your_secret_key")

        return True

    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False


def create_directories():
    """Create necessary directories"""
    print_step(4, "Creating Directories")

    directories = ["uploads/temp_images", "uploads/metadata_history"]

    try:
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {directory}")

        return True

    except Exception as e:
        print(f"❌ Failed to create directories: {e}")
        return False


def test_installation():
    """Test if installation was successful"""
    print_step(5, "Testing Installation")

    try:
        # Test imports
        print("🔍 Testing module imports...")

        import streamlit

        print("✅ Streamlit imported successfully")

        import requests

        print("✅ Requests imported successfully")

        from dotenv import load_dotenv

        print("✅ python-dotenv imported successfully")

        from PIL import Image

        print("✅ Pillow imported successfully")

        import tenacity

        print("✅ tenacity imported successfully")

        # Test local modules
        sys.path.append("modules")
        from pinata_client import PinataClient

        print("✅ PinataClient imported successfully")

        from metadata_builder import build_nft_metadata

        print("✅ metadata_builder imported successfully")

        print("\n🎉 All imports successful!")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def show_next_steps():
    """Show what to do next"""
    print_header("🚀 Setup Complete!")

    print("Next steps:")
    print("")
    print("1. Configure your Pinata API credentials:")
    print("   Edit the .env file with your API keys")
    print("")
    print("2. Test your connection:")
    print("   python test_connection.py")
    print("")
    print("3. Run the application:")
    print("   python run.py")
    print("   or")
    print("   streamlit run app.py")
    print("")
    print("4. For programmatic usage examples:")
    print("   python example_usage.py")
    print("")
    print("📚 Documentation:")
    print("   See README.md for detailed instructions")
    print("")
    print("🆘 Need help?")
    print("   - Check the troubleshooting section in README.md")
    print("   - Ensure your Pinata account has available quota")
    print("   - Verify your internet connection")


def main():
    """Main setup function"""
    print_header("NFT IPFS Uploader - Setup")
    print("This script will set up the NFT IPFS Uploader application")
    print("Please ensure you have a Pinata account and API keys ready")

    # Confirmation
    response = input("\nDo you want to continue? (Y/n): ").strip().lower()
    if response == "n":
        print("Setup cancelled")
        return

    success = True

    # Run setup steps
    success &= check_python_version()
    success &= install_dependencies()
    success &= setup_environment()
    success &= create_directories()
    success &= test_installation()

    if success:
        show_next_steps()
    else:
        print("\n❌ Setup failed!")
        print("Please check the errors above and try again")
        sys.exit(1)


if __name__ == "__main__":
    main()
