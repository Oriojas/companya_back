#!/usr/bin/env python3
"""
Run NFT IPFS Uploader
Simple script to launch the Streamlit application
"""

import os
import subprocess
import sys
from pathlib import Path


def check_requirements():
    """Check if all requirements are installed"""
    try:
        import requests
        import streamlit
        import tenacity
        from dotenv import load_dotenv
        from PIL import Image

        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return False


def check_env_file():
    """Check if .env file exists and has required variables"""
    env_path = Path(".env")

    if not env_path.exists():
        print("❌ .env file not found!")
        print("Please copy .env.example to .env and configure your Pinata credentials")
        return False

    # Load environment variables
    from dotenv import load_dotenv

    load_dotenv()

    api_key = os.getenv("PINATA_API_KEY")
    secret_key = os.getenv("PINATA_SECRET_API_KEY")

    if not api_key or not secret_key:
        print("❌ Pinata credentials not found in .env file!")
        print("Please configure PINATA_API_KEY and PINATA_SECRET_API_KEY")
        return False

    return True


def main():
    """Main function to run the app"""
    print("🎨 NFT IPFS Uploader")
    print("=" * 30)

    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("❌ app.py not found!")
        print("Please run this script from the IPFS_storage directory")
        return False

    # Check requirements
    if not check_requirements():
        return False

    # Check environment configuration
    if not check_env_file():
        return False

    print("✅ All checks passed!")
    print("🚀 Starting Streamlit application...")
    print("\nThe app will open in your browser at http://localhost:8501")
    print("Press Ctrl+C to stop the application\n")

    try:
        # Run Streamlit
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error running application: {e}")
        return False

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
