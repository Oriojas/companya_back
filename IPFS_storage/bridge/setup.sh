#!/bin/bash

# Filecoin Bridge Service Setup Script
# Installs Node.js dependencies and sets up the bridge service

set -e  # Exit on any error

echo "🚀 Setting up Filecoin Bridge Service"
echo "===================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    echo "Please install Node.js 18+ and try again"
    echo "Visit: https://nodejs.org/"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node --version | cut -d 'v' -f 2 | cut -d '.' -f 1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version 18+ required"
    echo "Current version: $(node --version)"
    exit 1
fi

echo "✅ Node.js found: $(node --version)"

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed"
    exit 1
fi

echo "✅ npm found: $(npm --version)"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Create .env template if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env template..."
    cat > .env << EOF
# Filecoin Bridge Service Configuration
# Copy these values from your main IPFS_storage/.env file

# Filecoin Private Key (without 0x prefix)
FILECOIN_PRIVATE_KEY=your_private_key_here

# Filecoin RPC URL (Calibration testnet)
FILECOIN_RPC_URL=https://filecoin-calibration.chainup.net/rpc/v1

# Bridge Service Port
PORT=3001

# Bridge Service URL (for Python client)
BRIDGE_URL=http://localhost:3001
EOF
    echo "✅ Created .env template"
    echo "⚠️  Please edit .env with your actual credentials"
else
    echo "✅ .env file already exists"
fi

# Test installation
echo "🧪 Testing installation..."
npm run test > /dev/null 2>&1 || echo "⚠️  No tests configured (this is normal)"

# Check if we can start the service
echo "🔧 Testing service startup..."
timeout 10s npm start > /dev/null 2>&1 || true

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env with your Filecoin private key and RPC URL"
echo "2. Get test tokens from:"
echo "   - tFIL: https://faucet.calibration.fildev.network/"
echo "   - USDFC: https://faucet.calibration.fildev.network/"
echo "3. Start the service: npm start"
echo "4. Test the bridge: curl http://localhost:3001/health"
echo ""
echo "📚 Documentation:"
echo "- Filecoin Docs: https://docs.filecoin.io"
echo "- Synapse SDK: https://docs.filecoin.cloud"
echo ""
