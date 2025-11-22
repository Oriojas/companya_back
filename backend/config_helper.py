"""
Configuration Helper for NFT Backend

Simple utility to load deployment information and contract configuration
automatically from the project structure.
"""

import json
import os
from pathlib import Path


class ConfigHelper:
    """Helper class to load backend configuration automatically"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backend_dir = self.project_root / "backend"
        self.deployments_dir = self.project_root / "deployments"
        self.artifacts_dir = self.project_root / "artifacts"

    def load_deployment_info(self):
        """Load the latest deployment information"""
        latest_deployment = self.deployments_dir / "latest-deployment.json"

        if not latest_deployment.exists():
            raise FileNotFoundError(
                "No deployment information found. Run 'npm run deploy' first."
            )

        with open(latest_deployment, 'r') as f:
            return json.load(f)

    def load_contract_abi(self):
        """Load the contract ABI from compiled artifacts"""
        artifact_path = (
            self.artifacts_dir
            / "contracts"
            / "ColeccionServiciosNFT.sol"
            / "ColeccionServiciosNFT.json"
        )

        if not artifact_path.exists():
            raise FileNotFoundError(
                "Contract ABI not found. Run 'npm run compile' first."
            )

        with open(artifact_path, 'r') as f:
            artifact = json.load(f)
            return artifact["abi"]

    def get_contract_address(self):
        """Get the deployed contract address"""
        deployment_info = self.load_deployment_info()
        return deployment_info["contractAddress"]

    def create_env_template(self):
        """Create a .env template with current deployment info"""
        deployment_info = self.load_deployment_info()

        env_content = f"""# Backend Configuration for NFT Services
# Generated from deployment: {deployment_info['deploymentDate']}

# Network Configuration
RPC_URL=https://sepolia-rollup.arbitrum.io/rpc
CHAIN_ID=421614

# Contract Information (auto-detected)
CONTRACT_ADDRESS={deployment_info['contractAddress']}
CONTRACT_NAME={deployment_info['contractName']}

# Private Key (REQUIRED - replace with your actual private key)
PRIVATE_KEY=your_private_key_here_without_0x_prefix

# Optional: Arbiscan API Key for verification
ARBISCAN_API_KEY=your_arbiscan_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
"""
        return env_content


# Global instance for easy access
config_helper = ConfigHelper()
```Ahora voy a actualizar el main.py del backend para usar esta configuración simple:
