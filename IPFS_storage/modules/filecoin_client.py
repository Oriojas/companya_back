"""
Filecoin Cloud Client for IPFS uploads
Handles image and JSON uploads to Filecoin Cloud using Synapse SDK bridge
"""

import json
import os
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

# Load environment variables
load_dotenv()

# Debug flag - set to False in production
DEBUG = False


class FilecoinCloudClient:
    """Client for interacting with Filecoin Cloud via Node.js bridge service"""

    def __init__(self, private_key: str = None, rpc_url: str = None):
        """
        Initialize Filecoin Cloud client

        Args:
            private_key: Filecoin private key (if None, loads from env)
            rpc_url: Filecoin RPC URL (if None, loads from env)
        """
        self.private_key = private_key or os.getenv("FILECOIN_PRIVATE_KEY")
        self.rpc_url = rpc_url or os.getenv(
            "FILECOIN_RPC_URL", "https://filecoin-calibration.chainup.net/rpc/v1"
        )

        if not self.private_key:
            raise ValueError("Filecoin private key not found. Check .env file.")

        self.bridge_url = os.getenv("FILECOIN_BRIDGE_URL", "http://localhost:3001")
        self.bridge_process = None

        # Ensure bridge service is running
        self._ensure_bridge_service()

    def _ensure_bridge_service(self):
        """Ensure Node.js bridge service is running"""
        try:
            # Check if bridge is already running
            response = requests.get(f"{self.bridge_url}/health", timeout=2)
            if response.status_code == 200:
                if DEBUG:
                    print("DEBUG: Bridge service already running")
                return
        except requests.exceptions.RequestException:
            pass

        # Start bridge service
        try:
            self._start_bridge_service()
        except Exception as e:
            if DEBUG:
                print(f"DEBUG: Could not start bridge service: {e}")
            # Fallback to direct REST API calls if bridge fails
            self.use_direct_api = True

    def _start_bridge_service(self):
        """Start the Node.js bridge service"""
        bridge_dir = Path(__file__).parent.parent / "bridge"

        if not bridge_dir.exists():
            raise Exception("Bridge service directory not found")

        # Start the bridge service in background
        env = os.environ.copy()
        env["FILECOIN_PRIVATE_KEY"] = self.private_key
        env["FILECOIN_RPC_URL"] = self.rpc_url

        self.bridge_process = subprocess.Popen(
            ["node", "server.js"],
            cwd=bridge_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Wait for service to start
        import time

        time.sleep(3)

        # Verify it's running
        try:
            response = requests.get(f"{self.bridge_url}/health", timeout=5)
            if response.status_code != 200:
                raise Exception("Bridge service failed to start properly")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Bridge service not responding: {e}")

    def test_authentication(self) -> bool:
        """
        Test Filecoin Cloud connection

        Returns:
            bool: True if connection successful
        """
        try:
            response = requests.post(
                f"{self.bridge_url}/test",
                json={"action": "test_auth"},
                timeout=10,
            )
            return response.status_code == 200 and response.json().get("success", False)
        except requests.RequestException:
            return False

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def upload_file(
        self, file_bytes: bytes, filename: str, metadata: Optional[Dict] = None
    ) -> str:
        """
        Upload file to Filecoin Cloud

        Args:
            file_bytes: File content as bytes
            filename: Name of the file
            metadata: Optional metadata for the upload

        Returns:
            str: Piece CID of uploaded file

        Raises:
            Exception: If upload fails
        """
        if DEBUG:
            print(f"DEBUG: Uploading file '{filename}' with {len(file_bytes)} bytes")

        if len(file_bytes) == 0:
            raise Exception("File is empty (0 bytes)")

        # Ensure minimum size requirement (127 bytes for Filecoin)
        if len(file_bytes) < 127:
            # Pad file to meet minimum size
            padding = b"\x00" * (127 - len(file_bytes))
            file_bytes = file_bytes + padding
            if DEBUG:
                print(f"DEBUG: Padded file to {len(file_bytes)} bytes")

        try:
            # Create temporary file for upload
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=f"_{filename}"
            ) as tmp_file:
                tmp_file.write(file_bytes)
                tmp_path = tmp_file.name

            # Upload via bridge service
            with open(tmp_path, "rb") as f:
                files = {"file": (filename, f, "application/octet-stream")}
                data = {"filename": filename, "metadata": json.dumps(metadata or {})}

                response = requests.post(
                    f"{self.bridge_url}/upload/file",
                    files=files,
                    data=data,
                    timeout=120,
                )

            # Clean up temp file
            os.unlink(tmp_path)

            if DEBUG:
                print(f"DEBUG: Response status: {response.status_code}")
                print(f"DEBUG: Response text: {response.text}")

            if response.status_code != 200:
                raise Exception(
                    f"Failed to upload file: {response.status_code} - {response.text}"
                )

            result = response.json()
            if not result.get("success"):
                raise Exception(
                    f"Upload failed: {result.get('error', 'Unknown error')}"
                )

            piece_cid = result.get("pieceCid")
            if not piece_cid:
                raise Exception("No piece CID returned from upload")

            if DEBUG:
                print(f"DEBUG: Upload successful, Piece CID: {piece_cid}")

            return piece_cid

        except requests.RequestException as e:
            raise Exception(f"Network error during upload: {str(e)}")

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def upload_json(self, json_data: Dict[str, Any], name: str) -> str:
        """
        Upload JSON data to Filecoin Cloud

        Args:
            json_data: JSON object to upload
            name: Name for the upload

        Returns:
            str: Piece CID of uploaded JSON

        Raises:
            Exception: If upload fails
        """
        try:
            # Convert JSON to bytes
            json_bytes = json.dumps(json_data, ensure_ascii=False).encode("utf-8")

            # Ensure minimum size
            if len(json_bytes) < 127:
                # Add padding to metadata to meet minimum size
                padding_size = 127 - len(json_bytes)
                json_data["_padding"] = "x" * padding_size
                json_bytes = json.dumps(json_data, ensure_ascii=False).encode("utf-8")

            payload = {"data": json_data, "name": name}

            response = requests.post(
                f"{self.bridge_url}/upload/json",
                json=payload,
                timeout=60,
            )

            if DEBUG:
                print(f"DEBUG: JSON upload response: {response.status_code}")
                print(f"DEBUG: Response text: {response.text}")

            if response.status_code != 200:
                raise Exception(
                    f"Failed to upload JSON: {response.status_code} - {response.text}"
                )

            result = response.json()
            if not result.get("success"):
                raise Exception(
                    f"JSON upload failed: {result.get('error', 'Unknown error')}"
                )

            piece_cid = result.get("pieceCid")
            if not piece_cid:
                raise Exception("No piece CID returned from JSON upload")

            if DEBUG:
                print(f"DEBUG: JSON upload successful, Piece CID: {piece_cid}")

            return piece_cid

        except requests.RequestException as e:
            raise Exception(f"Network error during JSON upload: {str(e)}")

    def get_ipfs_uri(self, piece_cid: str) -> str:
        """
        Get IPFS URI from Piece CID

        Args:
            piece_cid: Filecoin Piece CID

        Returns:
            str: IPFS URI in format ipfs://cid
        """
        return f"ipfs://{piece_cid}"

    def get_gateway_url(self, piece_cid: str, gateway: str = "https://w3s.link") -> str:
        """
        Get HTTP gateway URL for Filecoin content

        Args:
            piece_cid: Filecoin Piece CID
            gateway: Gateway URL (default: web3.storage gateway)

        Returns:
            str: HTTP URL for accessing content
        """
        return f"{gateway}/ipfs/{piece_cid}"

    def download_file(self, piece_cid: str) -> bytes:
        """
        Download file from Filecoin Cloud

        Args:
            piece_cid: Piece CID to download

        Returns:
            bytes: Downloaded file content
        """
        try:
            response = requests.post(
                f"{self.bridge_url}/download", json={"pieceCid": piece_cid}, timeout=60
            )

            if response.status_code != 200:
                raise Exception(
                    f"Download failed: {response.status_code} - {response.text}"
                )

            result = response.json()
            if not result.get("success"):
                raise Exception(
                    f"Download failed: {result.get('error', 'Unknown error')}"
                )

            # Decode base64 content
            import base64

            content = base64.b64decode(result.get("content", ""))
            return content

        except requests.RequestException as e:
            raise Exception(f"Network error during download: {str(e)}")

    def download_json(self, piece_cid: str) -> Dict[str, Any]:
        """
        Download and parse JSON from Filecoin Cloud

        Args:
            piece_cid: Piece CID to download

        Returns:
            dict: Parsed JSON data
        """
        try:
            json_bytes = self.download_file(piece_cid)
            return json.loads(json_bytes.decode("utf-8"))
        except Exception as e:
            raise Exception(f"Failed to download JSON: {str(e)}")

    def get_storage_info(self) -> Dict[str, Any]:
        """
        Get Filecoin storage information

        Returns:
            dict: Storage information and statistics
        """
        try:
            response = requests.get(f"{self.bridge_url}/info", timeout=10)

            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to get storage info: {response.status_code}"}

        except requests.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}

    def validate_file_size(self, file_size: int, max_size_mb: int = 1000) -> bool:
        """
        Validate file size against Filecoin limits

        Args:
            file_size: Size in bytes
            max_size_mb: Maximum size in MB (Filecoin supports larger files)

        Returns:
            bool: True if file size is acceptable
        """
        max_size_bytes = max_size_mb * 1024 * 1024
        return file_size <= max_size_bytes and file_size >= 127  # Minimum 127 bytes

    def get_balance(self) -> Dict[str, Any]:
        """
        Get wallet balance information

        Returns:
            dict: Balance information with USDFC and FIL balances
        """
        try:
            response = requests.get(f"{self.bridge_url}/balance", timeout=10)

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return result.get("balances", {})
                else:
                    return {"error": result.get("error", "Unknown balance error")}
            else:
                return {"error": f"Failed to get balance: {response.status_code}"}

        except requests.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}

    def estimate_cost(self, file_size_bytes: int, duration_days: int = 30) -> float:
        """
        Estimate storage cost

        Args:
            file_size_bytes: Size of file in bytes
            duration_days: Storage duration in days

        Returns:
            float: Estimated cost in USDFC
        """
        try:
            response = requests.post(
                f"{self.bridge_url}/estimate",
                json={"fileSizeBytes": file_size_bytes, "durationDays": duration_days},
                timeout=10,
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    estimation = result.get("estimation", {})
                    return float(estimation.get("estimatedCostUSDFC", 0))
                else:
                    return 0.0
            else:
                return 0.0

        except (requests.RequestException, ValueError):
            return 0.0

    def __del__(self):
        """Cleanup bridge process on deletion"""
        if hasattr(self, "bridge_process") and self.bridge_process:
            try:
                self.bridge_process.terminate()
                self.bridge_process.wait(timeout=5)
            except:
                try:
                    self.bridge_process.kill()
                except:
                    pass
