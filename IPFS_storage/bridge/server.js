import express from 'express';
import cors from 'cors';
import multer from 'multer';
import dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { readFileSync } from 'fs';
import { Synapse, RPC_URLS, TOKENS, TIME_CONSTANTS } from '@filoz/synapse-sdk';
import { ethers } from 'ethers';

// Load environment variables
dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const port = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json({ limit: '100mb' }));
app.use(express.urlencoded({ extended: true, limit: '100mb' }));

// Configure multer for file uploads
const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 100 * 1024 * 1024, // 100MB limit
  },
});

// Global Synapse instance
let synapse = null;
let isInitialized = false;

// Initialize Synapse SDK
async function initializeSynapse() {
  try {
    const privateKey = process.env.FILECOIN_PRIVATE_KEY;
    const rpcURL = process.env.FILECOIN_RPC_URL || RPC_URLS.calibration.http;

    if (!privateKey) {
      throw new Error('FILECOIN_PRIVATE_KEY not found in environment variables');
    }

    console.log('🔧 Initializing Synapse SDK...');
    synapse = await Synapse.create({
      privateKey: privateKey,
      rpcURL: rpcURL,
    });

    console.log('✅ Synapse SDK initialized successfully');

    // Test connection and get initial balance
    try {
      const walletBalance = await synapse.payments.walletBalance(TOKENS.USDFC);
      const formattedBalance = ethers.formatUnits(walletBalance, 18);
      console.log(`💰 USDFC Balance: ${formattedBalance} USDFC`);

      // Check if we have sufficient balance for operations
      if (walletBalance < ethers.parseUnits("0.1", 18)) {
        console.warn('⚠️  Low USDFC balance. Consider adding more funds for storage operations.');
      }
    } catch (balanceError) {
      console.warn('⚠️  Could not check wallet balance:', balanceError.message);
    }

    isInitialized = true;
    return true;
  } catch (error) {
    console.error('❌ Failed to initialize Synapse SDK:', error.message);
    isInitialized = false;
    return false;
  }
}

// Ensure Synapse is initialized before handling requests
async function ensureInitialized(req, res, next) {
  if (!isInitialized) {
    const initialized = await initializeSynapse();
    if (!initialized) {
      return res.status(500).json({
        success: false,
        error: 'Failed to initialize Filecoin connection'
      });
    }
  }
  next();
}

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    success: true,
    service: 'Filecoin Bridge Service',
    status: isInitialized ? 'ready' : 'initializing',
    timestamp: new Date().toISOString()
  });
});

// Test authentication endpoint
app.post('/test', ensureInitialized, async (req, res) => {
  try {
    // Test basic SDK functionality
    const storageInfo = await synapse.storage.getStorageInfo();

    res.json({
      success: true,
      message: 'Filecoin connection successful',
      providers: storageInfo.providers.length,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('❌ Test failed:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Upload file endpoint
app.post('/upload/file', upload.single('file'), ensureInitialized, async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({
        success: false,
        error: 'No file provided'
      });
    }

    const { filename, metadata } = req.body;
    const fileBuffer = req.file.buffer;

    console.log(`📤 Uploading file: ${filename || req.file.originalname} (${fileBuffer.length} bytes)`);

    // Ensure minimum size requirement (127 bytes)
    let uploadBuffer = fileBuffer;
    if (fileBuffer.length < 127) {
      const padding = Buffer.alloc(127 - fileBuffer.length);
      uploadBuffer = Buffer.concat([fileBuffer, padding]);
      console.log(`📏 Padded file to meet 127 byte minimum: ${uploadBuffer.length} bytes`);
    }

    // Upload to Filecoin
    const result = await synapse.storage.upload(uploadBuffer, {
      withCDN: true, // Enable CDN for faster retrieval
      metadata: metadata ? JSON.parse(metadata) : {}
    });

    console.log(`✅ File uploaded successfully. Piece CID: ${result.pieceCid}`);

    res.json({
      success: true,
      pieceCid: result.pieceCid,
      size: result.size,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('❌ File upload failed:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Upload JSON endpoint
app.post('/upload/json', ensureInitialized, async (req, res) => {
  try {
    const { data, name } = req.body;

    if (!data) {
      return res.status(400).json({
        success: false,
        error: 'No JSON data provided'
      });
    }

    console.log(`📝 Uploading JSON: ${name || 'unnamed'}`);

    // Convert JSON to buffer
    const jsonString = JSON.stringify(data, null, 2);
    let jsonBuffer = Buffer.from(jsonString, 'utf8');

    // Ensure minimum size requirement
    if (jsonBuffer.length < 127) {
      // Add padding to the JSON data
      const paddingSize = 127 - jsonBuffer.length;
      data._padding = 'x'.repeat(paddingSize);
      const paddedJsonString = JSON.stringify(data, null, 2);
      jsonBuffer = Buffer.from(paddedJsonString, 'utf8');
      console.log(`📏 Padded JSON to meet 127 byte minimum: ${jsonBuffer.length} bytes`);
    }

    // Upload to Filecoin
    const result = await synapse.storage.upload(jsonBuffer, {
      withCDN: true,
      metadata: {
        type: 'json',
        name: name || 'metadata',
        contentType: 'application/json'
      }
    });

    console.log(`✅ JSON uploaded successfully. Piece CID: ${result.pieceCid}`);

    res.json({
      success: true,
      pieceCid: result.pieceCid,
      size: result.size,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('❌ JSON upload failed:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Download file endpoint
app.post('/download', ensureInitialized, async (req, res) => {
  try {
    const { pieceCid } = req.body;

    if (!pieceCid) {
      return res.status(400).json({
        success: false,
        error: 'No piece CID provided'
      });
    }

    console.log(`📥 Downloading file with Piece CID: ${pieceCid}`);

    // Download from Filecoin
    const data = await synapse.storage.download(pieceCid);

    // Convert to base64 for JSON response
    const base64Content = Buffer.from(data).toString('base64');

    console.log(`✅ File downloaded successfully: ${data.length} bytes`);

    res.json({
      success: true,
      content: base64Content,
      size: data.length,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('❌ Download failed:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get storage info endpoint
app.get('/info', ensureInitialized, async (req, res) => {
  try {
    const storageInfo = await synapse.storage.getStorageInfo();

    res.json({
      success: true,
      info: {
        providers: storageInfo.providers.map(p => ({
          id: p.id,
          name: p.name,
          description: p.description,
          active: p.active
        })),
        totalProviders: storageInfo.providers.length,
        activeProviders: storageInfo.providers.filter(p => p.active).length
      },
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('❌ Failed to get storage info:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get balance endpoint
app.get('/balance', ensureInitialized, async (req, res) => {
  try {
    const usdfc_balance = await synapse.payments.walletBalance(TOKENS.USDFC);
    const fil_balance = await synapse.payments.walletBalance(TOKENS.FIL);

    res.json({
      success: true,
      balances: {
        USDFC: ethers.formatUnits(usdfc_balance, 18),
        FIL: ethers.formatUnits(fil_balance, 18)
      },
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('❌ Failed to get balance:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Estimate cost endpoint
app.post('/estimate', ensureInitialized, async (req, res) => {
  try {
    const { fileSizeBytes, durationDays = 30 } = req.body;

    if (!fileSizeBytes || fileSizeBytes <= 0) {
      return res.status(400).json({
        success: false,
        error: 'Invalid file size'
      });
    }

    // Simple cost estimation based on Filecoin storage pricing
    const bytesToTiB = fileSizeBytes / (1024 ** 4);
    const costPerTiBMonth = 2.5; // Approximate USDFC cost for 1TiB for 30 days
    const monthsNeeded = durationDays / 30;

    const estimatedCost = bytesToTiB * costPerTiBMonth * monthsNeeded;

    res.json({
      success: true,
      estimation: {
        fileSizeBytes: fileSizeBytes,
        durationDays: durationDays,
        estimatedCostUSDFC: estimatedCost.toFixed(6),
        breakdown: {
          sizeInTiB: bytesToTiB.toExponential(2),
          costPerTiBMonth: costPerTiBMonth,
          monthsNeeded: monthsNeeded
        }
      },
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('❌ Failed to estimate cost:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Fund account endpoint (for initial setup)
app.post('/fund', ensureInitialized, async (req, res) => {
  try {
    const { amount = "2.5" } = req.body; // Default 2.5 USDFC

    const depositAmount = ethers.parseUnits(amount, 18);

    console.log(`💰 Funding account with ${amount} USDFC...`);

    // Check current balance
    const currentBalance = await synapse.payments.walletBalance(TOKENS.USDFC);

    if (currentBalance < depositAmount) {
      return res.status(400).json({
        success: false,
        error: `Insufficient wallet balance. Need ${amount} USDFC, have ${ethers.formatUnits(currentBalance, 18)}`
      });
    }

    // Deposit and approve storage service
    const tx = await synapse.payments.depositWithPermitAndApproveOperator(
      depositAmount,
      synapse.getWarmStorageAddress(),
      ethers.MaxUint256,
      ethers.MaxUint256,
      TIME_CONSTANTS.EPOCHS_PER_MONTH
    );

    await tx.wait();

    console.log(`✅ Account funded successfully. Transaction: ${tx.hash}`);

    res.json({
      success: true,
      message: `Successfully funded account with ${amount} USDFC`,
      transactionHash: tx.hash,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('❌ Failed to fund account:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Error handling middleware
app.use((error, req, res, next) => {
  console.error('❌ Server error:', error);
  res.status(500).json({
    success: false,
    error: 'Internal server error'
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    success: false,
    error: 'Endpoint not found'
  });
});

// Start server
async function startServer() {
  try {
    // Initialize Synapse SDK
    const initialized = await initializeSynapse();

    if (!initialized) {
      console.warn('⚠️  Starting server without Synapse initialization. Check your configuration.');
    }

    app.listen(port, () => {
      console.log(`🚀 Filecoin Bridge Service running on port ${port}`);
      console.log(`📋 Endpoints available:`);
      console.log(`   GET  /health - Health check`);
      console.log(`   POST /test - Test connection`);
      console.log(`   POST /upload/file - Upload file`);
      console.log(`   POST /upload/json - Upload JSON`);
      console.log(`   POST /download - Download file`);
      console.log(`   GET  /info - Storage info`);
      console.log(`   GET  /balance - Wallet balance`);
      console.log(`   POST /estimate - Cost estimation`);
      console.log(`   POST /fund - Fund account`);
    });
  } catch (error) {
    console.error('❌ Failed to start server:', error);
    process.exit(1);
  }
}

// Handle process termination
process.on('SIGINT', () => {
  console.log('\n👋 Shutting down Filecoin Bridge Service...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\n👋 Shutting down Filecoin Bridge Service...');
  process.exit(0);
});

// Start the server
startServer();
