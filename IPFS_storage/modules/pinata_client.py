"""
Pinata Client for IPFS uploads
Handles image and JSON uploads to Pinata IPFS service
"""

import json
import os
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

# Load environment variables
load_dotenv()

# Debug flag - set to False in production
DEBUG = False


class UploadLogger:
    """Simple logger for upload tracking"""

    def __init__(self, log_file: str = "uploads/logs/upload_log.json"):
        import json
        from datetime import datetime
        from pathlib import Path

        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        if not self.log_file.exists():
            with open(self.log_file, "w", encoding="utf-8") as f:
                json.dump(
                    {"created_at": datetime.now().isoformat(), "uploads": []},
                    f,
                    indent=2,
                )

    def log_upload(
        self,
        upload_type,
        filename,
        cid,
        file_size_bytes,
        ipfs_uri,
        gateway_url,
        **kwargs,
    ):
        import json
        from datetime import datetime

        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            data = {"uploads": []}

        upload_entry = {
            "timestamp": datetime.now().isoformat(),
            "upload_type": upload_type,
            "filename": filename,
            "cid": cid,
            "file_size_bytes": file_size_bytes,
            "ipfs_uri": ipfs_uri,
            "gateway_url": gateway_url,
            **kwargs,
        }

        data["uploads"].append(upload_entry)

        with open(self.log_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


class PinataClient:
    """Client for interacting with Pinata IPFS API"""

    def __init__(self, api_key: str = None, secret_key: str = None):
        """
        Initialize Pinata client

        Args:
            api_key: Pinata API key (if None, loads from env)
            secret_key: Pinata secret key (if None, loads from env)
        """
        self.api_key = api_key or os.getenv("PINATA_API_KEY")
        self.secret_key = secret_key or os.getenv("PINATA_SECRET_API_KEY")

        if not self.api_key or not self.secret_key:
            raise ValueError("Pinata API credentials not found. Check .env file.")

        self.base_url = "https://api.pinata.cloud"
        self.headers = {
            "pinata_api_key": self.api_key,
            "pinata_secret_api_key": self.secret_key,
        }

        # Initialize logger
        self.logger = UploadLogger()

    def test_authentication(self) -> bool:
        """
        Test Pinata API authentication

        Returns:
            bool: True if authentication successful
        """
        try:
            response = requests.get(
                f"{self.base_url}/data/testAuthentication",
                headers=self.headers,
                timeout=10,
            )
            return response.status_code == 200
        except requests.RequestException:
            return False

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def upload_file(
        self, file_bytes: bytes, filename: str, metadata: Optional[Dict] = None
    ) -> str:
        """
        Upload file to Pinata IPFS

        Args:
            file_bytes: File content as bytes
            filename: Name of the file
            metadata: Optional metadata for the pin

        Returns:
            str: IPFS CID of uploaded file

        Raises:
            Exception: If upload fails
        """
        if DEBUG:
            print(f"DEBUG: Uploading file '{filename}' with {len(file_bytes)} bytes")

        if len(file_bytes) == 0:
            # Log failed upload
            self.logger.log_upload(
                upload_type="image",
                filename=filename,
                cid="",
                file_size_bytes=0,
                ipfs_uri="",
                gateway_url="",
                status="failed",
                error="File is empty (0 bytes)",
            )
            raise Exception("File is empty (0 bytes)")

        url = f"{self.base_url}/pinning/pinFileToIPFS"

        # Prepare files and data for multipart upload
        files = {"file": (filename, file_bytes, "application/octet-stream")}

        pin_metadata = metadata or {"name": filename}
        data = {
            "pinataMetadata": json.dumps(pin_metadata),
            "pinataOptions": json.dumps({"cidVersion": 1}),
        }

        if DEBUG:
            print(f"DEBUG: Uploading to {url}")
            print(f"DEBUG: Metadata: {pin_metadata}")

        try:
            response = requests.post(
                url, headers=self.headers, files=files, data=data, timeout=120
            )

            if DEBUG:
                print(f"DEBUG: Response status: {response.status_code}")
                print(f"DEBUG: Response text: {response.text}")

            if response.status_code != 200:
                # Log failed upload
                self.logger.log_upload(
                    upload_type="image",
                    filename=filename,
                    cid="",
                    file_size_bytes=len(file_bytes),
                    ipfs_uri="",
                    gateway_url="",
                    status="failed",
                    error=f"HTTP {response.status_code}: {response.text}",
                )
                raise Exception(
                    f"Failed to upload file: {response.status_code} - {response.text}"
                )

            result = response.json()
            cid = result["IpfsHash"]

            # Log successful upload
            ipfs_uri = self.get_ipfs_uri(cid)
            gateway_url = self.get_gateway_url(cid)

            self.logger.log_upload(
                upload_type="image",
                filename=filename,
                cid=cid,
                file_size_bytes=len(file_bytes),
                ipfs_uri=ipfs_uri,
                gateway_url=gateway_url,
                status="success",
                metadata=pin_metadata,
            )

            if DEBUG:
                print(f"DEBUG: Upload successful, CID: {cid}")
            return cid

        except requests.RequestException as e:
            # Log network error
            self.logger.log_upload(
                upload_type="image",
                filename=filename,
                cid="",
                file_size_bytes=len(file_bytes),
                ipfs_uri="",
                gateway_url="",
                status="failed",
                error=f"Network error: {str(e)}",
            )
            raise Exception(f"Network error during upload: {str(e)}")

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def upload_json(self, json_data: Dict[str, Any], name: str) -> str:
        """
        Upload JSON data to Pinata IPFS

        Args:
            json_data: JSON object to upload
            name: Name for the pin

        Returns:
            str: IPFS CID of uploaded JSON

        Raises:
            Exception: If upload fails
        """
        url = f"{self.base_url}/pinning/pinJSONToIPFS"

        payload = {
            "pinataContent": json_data,
            "pinataMetadata": {"name": name},
            "pinataOptions": {"cidVersion": 1},
        }

        try:
            response = requests.post(
                url,
                headers={**self.headers, "Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=60,
            )

            if response.status_code != 200:
                # Log failed upload
                self.logger.log_upload(
                    upload_type="metadata",
                    filename=f"{name}.json",
                    cid="",
                    file_size_bytes=len(json.dumps(json_data).encode("utf-8")),
                    ipfs_uri="",
                    gateway_url="",
                    status="failed",
                    error=f"HTTP {response.status_code}: {response.text}",
                    json_data=json_data,
                )
                raise Exception(
                    f"Failed to upload JSON: {response.status_code} - {response.text}"
                )

            result = response.json()
            cid = result["IpfsHash"]

            # Log successful upload
            ipfs_uri = self.get_ipfs_uri(cid)
            gateway_url = self.get_gateway_url(cid)
            file_size = len(json.dumps(json_data).encode("utf-8"))

            self.logger.log_upload(
                upload_type="metadata",
                filename=f"{name}.json",
                cid=cid,
                file_size_bytes=file_size,
                ipfs_uri=ipfs_uri,
                gateway_url=gateway_url,
                status="success",
                json_data=json_data,
                nft_name=json_data.get("name", "Unknown"),
            )

            return cid

        except requests.RequestException as e:
            # Log network error
            self.logger.log_upload(
                upload_type="metadata",
                filename=f"{name}.json",
                cid="",
                file_size_bytes=len(json.dumps(json_data).encode("utf-8")),
                ipfs_uri="",
                gateway_url="",
                status="failed",
                error=f"Network error: {str(e)}",
                json_data=json_data,
            )
            raise Exception(f"Network error during JSON upload: {str(e)}")

    def get_ipfs_uri(self, cid: str) -> str:
        """
        Get IPFS URI from CID

        Args:
            cid: IPFS Content Identifier

        Returns:
            str: IPFS URI in format ipfs://cid
        """
        return f"ipfs://{cid}"

    def get_gateway_url(
        self, cid: str, gateway: str = "https://gateway.pinata.cloud"
    ) -> str:
        """
        Get HTTP gateway URL for IPFS content

        Args:
            cid: IPFS Content Identifier
            gateway: Gateway URL (default: Pinata gateway)

        Returns:
            str: HTTP URL for accessing content
        """
        return f"{gateway}/ipfs/{cid}"

    def get_pin_list(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get list of pinned content

        Args:
            limit: Maximum number of items to return

        Returns:
            dict: Response with pinned content list
        """
        try:
            params = {"pageLimit": limit, "pageOffset": 0}

            response = requests.get(
                f"{self.base_url}/data/pinList",
                headers=self.headers,
                params=params,
                timeout=10,
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to get pin list: {response.status_code}"}

        except requests.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}

    def unpin_content(self, cid: str) -> bool:
        """
        Unpin content from Pinata

        Args:
            cid: IPFS CID to unpin

        Returns:
            bool: True if successful
        """
        try:
            response = requests.delete(
                f"{self.base_url}/pinning/unpin/{cid}", headers=self.headers, timeout=10
            )
            return response.status_code == 200
        except requests.RequestException:
            return False

    def validate_file_size(self, file_size: int, max_size_mb: int = 100) -> bool:
        """
        Validate file size against Pinata limits

        Args:
            file_size: Size in bytes
            max_size_mb: Maximum size in MB

        Returns:
            bool: True if file size is acceptable
        """
        max_size_bytes = max_size_mb * 1024 * 1024
        return file_size <= max_size_bytes

    def get_account_info(self) -> Dict[str, Any]:
        """
        Get Pinata account information

        Returns:
            dict: Account information
        """
        try:
            response = requests.get(
                f"{self.base_url}/data/userPinnedDataTotal",
                headers=self.headers,
                timeout=10,
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to get account info: {response.status_code}"}

        except requests.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
