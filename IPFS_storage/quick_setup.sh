#!/bin/bash

# Quick Setup Script for NFT IPFS Uploader
# Automatically sets up virtual environment and installs dependencies

set -e  # Exit on any error

echo "🎨 NFT IPFS Uploader - Quick Setup"
echo "=================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Please install Python 3 and try again"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found"
    echo "Please run this script from the IPFS_storage directory"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo "✅ Dependencies installed successfully!"

# Setup .env file if it doesn't exist
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "📝 Creating .env file from template..."
        cp .env.example .env
        echo "✅ .env file created"
        echo ""
        echo "🔑 IMPORTANT: You need to edit the .env file with your Pinata credentials:"
        echo "   1. Visit: https://app.pinata.cloud/developers/api-keys"
        echo "   2. Create a new API key"
        echo "   3. Edit .env file with your credentials"
        echo ""
    else
        echo "⚠️  .env.example not found, skipping .env creation"
    fi
else
    echo "✅ .env file already exists"
fi

# Create necessary directories
echo "📁 Creating upload directories..."
mkdir -p uploads/temp_images
mkdir -p uploads/metadata_history
echo "✅ Directories created"

# Test installation
echo "🧪 Testing installation..."
python -c "
try:
    import streamlit
    import requests
    from dotenv import load_dotenv
    from PIL import Image
    import tenacity
    print('✅ All packages imported successfully!')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Configure your Pinata API credentials in the .env file"
echo "2. Test your connection: python test_connection.py"
echo "3. Run the application: python run.py"
echo ""
echo "💡 Remember to activate the virtual environment before running:"
echo "   source venv/bin/activate"
echo ""
echo "📚 For more information, see README.md"
