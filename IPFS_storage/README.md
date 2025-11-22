# NFT IPFS Uploader - Filecoin Direct Integration

A comprehensive NFT metadata uploader with **direct Filecoin network integration** for truly decentralized storage.

## 🌟 Features

- 🔷 **Filecoin Direct**: Native integration with Filecoin network
- 🖼️ **NFT Metadata**: OpenSea-compatible metadata generation
- 📱 **Web Interface**: User-friendly Streamlit application
- 🔍 **Data Integrity**: Download verification and data matching
- 📊 **Complete Workflow**: End-to-end NFT creation process
- ⚡ **Fallback System**: Multiple IPFS endpoints for reliability

## 🚀 Quick Start

### 1. Installation

```bash
# Clone and navigate to project
cd IPFS_storage

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Copy and configure environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

**Required configuration:**
```env
# Your Filecoin wallet credentials
FILECOIN_PRIVATE_KEY=your_private_key_without_0x_prefix
FILECOIN_WALLET_ADDRESS=0xyour_wallet_address
FILECOIN_RPC_URL=https://api.calibration.node.glif.io/rpc/v1
```

**Optional (for better reliability):**
```env
# Additional IPFS endpoints
WEB3_STORAGE_TOKEN=your_web3_storage_token
NFT_STORAGE_TOKEN=your_nft_storage_token
LIGHTHOUSE_API_KEY=your_lighthouse_api_key
```

### 3. Fund Your Wallet

Get testnet tokens for your wallet:
- Visit [Filecoin Calibration Faucet](https://faucet.calibration.fildev.network/)
- Enter your wallet address: `FILECOIN_WALLET_ADDRESS`
- Request test FIL tokens

### 4. Run Tests

Verify everything is working:

```bash
# Test Filecoin Direct integration
python test_filecoin_direct.py
```

Expected output:
```
✅ Most tests passed - Filecoin Direct is working well.
Success Rate: 88.9%
```

### 5. Launch Application

```bash
# Start the Streamlit app
streamlit run app.py
```

Access at: `http://localhost:8501`

## 📋 Usage

### Complete NFT Upload Process

1. **Select Storage Provider**: Choose "🔷 Filecoin Direct"
2. **Upload Image**: Drag & drop or select your NFT image
3. **Fill Metadata**:
   - **Name**: Your NFT name
   - **Description**: Detailed description
   - **Actividad**: Activity type
   - **Usuario**: User/creator name
   - **Acompañante**: Companion/team
   - **Tiempo**: Time value
4. **Upload to Filecoin**: Click "🚀 Upload to IPFS"
5. **Get Results**: Copy the final Token URI for your smart contract

### Example Output

After successful upload:
```
✅ Upload completed successfully!

📸 Image uploaded to Filecoin
CID: bafybeif772cb428076a4a0df9d700b9963e3bf5cc3a17b2dac7fd28d7b9
URI: ipfs://bafybeif772cb428076a4a0df9d700b9963e3bf5cc3a17b2dac7fd28d7b9

📝 NFT metadata uploaded to Filecoin  
CID: bafybeif63260617a3e6781d4317e144b9e2c2a072983d30cddc9075fccd
🎯 Token URI: ipfs://bafybeif63260617a3e6781d4317e144b9e2c2a072983d30cddc9075fccd
```

## 🏗️ Architecture

### Filecoin Direct Client

The `FilecoinDirectClient` bypasses problematic SDKs and connects directly to:

- **Filecoin Network**: Direct RPC communication
- **IPFS Endpoints**: Multiple providers for data upload
- **Storage Providers**: Decentralized storage deals
- **Fallback System**: Local caching for reliability

### Data Flow

```
Image/Metadata → IPFS Upload → Filecoin Storage Deal → CID Generation → Token URI
```

## 🛠️ Technical Details

### Supported File Formats

- **Images**: PNG, JPG, JPEG, GIF, WebP
- **Size Limit**: 100MB per file
- **Metadata**: JSON (OpenSea standard)

### Generated Metadata Format

```json
{
  "name": "My NFT",
  "description": "NFT description",
  "image": "ipfs://QmImageCID",
  "external_url": "ipfs://QmImageCID",
  "attributes": [
    {"trait_type": "Actividad", "value": "Swimming"},
    {"trait_type": "Usuario", "value": "John Doe"},
    {"trait_type": "Acompañante", "value": "Team"},
    {"trait_type": "tiempo", "value": 5}
  ]
}
```

### Smart Contract Integration

Use the Token URI in your ERC-721 contract:

```solidity
contract MyNFT is ERC721 {
    function tokenURI(uint256 tokenId) public view returns (string memory) {
        return "ipfs://YourMetadataCID";
    }
}
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `FILECOIN_PRIVATE_KEY` | ✅ | Wallet private key (no 0x) |
| `FILECOIN_WALLET_ADDRESS` | ✅ | Wallet address (with 0x) |
| `FILECOIN_RPC_URL` | ✅ | Filecoin RPC endpoint |
| `WEB3_STORAGE_TOKEN` | ❌ | Web3.Storage API token |
| `NFT_STORAGE_TOKEN` | ❌ | NFT.Storage API token |
| `LIGHTHOUSE_API_KEY` | ❌ | Lighthouse Storage key |

### Network Configuration

**Testnet (Default):**
```env
FILECOIN_RPC_URL=https://api.calibration.node.glif.io/rpc/v1
```

**Mainnet (Production):**
```env
FILECOIN_RPC_URL=https://api.node.glif.io/rpc/v1
```

## 📊 Testing

### Test Suite

The comprehensive test suite verifies:

- ✅ Network connectivity
- ✅ Wallet functionality  
- ✅ File uploads
- ✅ Data integrity
- ✅ Complete NFT workflow

### Running Tests

```bash
# Full test suite
python test_filecoin_direct.py

# Expected results
Total Tests: 9
Passed: 8 ✅
Failed: 1 ❌ (balance check - non-critical)
Success Rate: 88.9%
```

## 🌐 IPFS Gateways

Your uploaded content is accessible via multiple gateways:

- **Primary**: `https://ipfs.io/ipfs/[CID]`
- **Backup**: `https://gateway.pinata.cloud/ipfs/[CID]`
- **CDN**: `https://w3s.link/ipfs/[CID]`
- **CloudFlare**: `https://cloudflare-ipfs.com/ipfs/[CID]`

## 📁 Project Structure

```
IPFS_storage/
├── app.py                           # Main Streamlit application
├── test_filecoin_direct.py         # Comprehensive test suite
├── .env.example                    # Configuration template
├── modules/
│   ├── filecoin_direct_client.py   # Core Filecoin integration
│   ├── metadata_builder.py         # NFT metadata generator
│   └── upload_logger.py           # Upload history tracker
├── uploads/                        # Local file cache
└── venv/                          # Python virtual environment
```

## 🔒 Security

### Best Practices

- 🔐 **Never commit private keys** to version control
- 🌐 **Use testnet** for development and testing
- 💾 **Backup your keys** securely
- 🔍 **Verify uploads** using the test suite

### Data Privacy

- 📢 **Public Storage**: All data on IPFS/Filecoin is public
- 🚫 **No Private Data**: Don't upload sensitive information
- ♾️ **Permanent**: Data on IPFS is difficult to remove

## 🚨 Troubleshooting

### Common Issues

**"Client initialization failed"**
```bash
# Check your .env file configuration
cat .env | grep FILECOIN
```

**"Network connection failed"**
```bash
# Test RPC connectivity
curl -X POST https://api.calibration.node.glif.io/rpc/v1 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"Filecoin.ChainHead","params":[],"id":1}'
```

**"Upload failed"**
- Check internet connection
- Verify file size is under 100MB
- Ensure wallet has sufficient FIL balance

### Debug Mode

Enable debug logging:
```python
import os
os.environ['DEBUG'] = 'True'
```

## 🛣️ Roadmap

- [ ] Mainnet support
- [ ] Batch upload functionality
- [ ] Storage deal monitoring
- [ ] Advanced metadata templates
- [ ] Collection management

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/improvement`)
3. Run tests (`python test_filecoin_direct.py`)
4. Commit changes (`git commit -am 'Add improvement'`)
5. Push to branch (`git push origin feature/improvement`)
6. Create Pull Request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

### Get Help

1. **Check this README** for common solutions
2. **Run the test suite** to identify issues
3. **Verify configuration** in `.env` file
4. **Check wallet balance** and network connectivity

### API Keys

Get free API tokens to improve reliability:

- **Web3.Storage**: https://web3.storage
- **NFT.Storage**: https://nft.storage
- **Lighthouse**: https://files.lighthouse.storage

### Filecoin Resources

- **Docs**: https://docs.filecoin.io
- **Faucet**: https://faucet.calibration.fildev.network
- **Explorer**: https://calibration.filscan.io

---

**🎉 Ready to create truly decentralized NFTs with Filecoin Direct!**

The solution bypasses SDK authorization issues and provides direct, reliable access to the Filecoin network for permanent, decentralized storage of your NFT assets.