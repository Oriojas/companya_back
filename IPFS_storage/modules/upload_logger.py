"""
Upload Logger for IPFS Storage
Comprehensive logging system for tracking all Pinata uploads in JSON format
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class UploadLogger:
    """Logger for tracking IPFS uploads with detailed metadata"""

    def __init__(self, log_file: str = "uploads/logs/upload_log.json"):
        """
        Initialize the upload logger

        Args:
            log_file: Path to the log file
        """
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        # Initialize log file if it doesn't exist
        if not self.log_file.exists():
            self._initialize_log_file()

    def _initialize_log_file(self):
        """Initialize empty log file structure"""
        initial_data = {
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "total_uploads": 0,
            "total_size_bytes": 0,
            "uploads": [],
        }

        with open(self.log_file, "w", encoding="utf-8") as f:
            json.dump(initial_data, f, indent=2, ensure_ascii=False)

    def _load_log_data(self) -> Dict[str, Any]:
        """Load existing log data"""
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._initialize_log_file()
            return self._load_log_data()

    def _save_log_data(self, data: Dict[str, Any]):
        """Save log data to file"""
        # Update totals
        data["total_uploads"] = len(data["uploads"])
        data["total_size_bytes"] = sum(
            upload.get("file_size_bytes", 0) for upload in data["uploads"]
        )
        data["last_updated"] = datetime.now().isoformat()

        with open(self.log_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def log_upload(
        self,
        upload_type: str,  # "image" or "metadata"
        filename: str,
        cid: str,
        file_size_bytes: int,
        ipfs_uri: str,
        gateway_url: str,
        metadata: Optional[Dict[str, Any]] = None,
        nft_metadata: Optional[Dict[str, Any]] = None,
        related_cid: Optional[str] = None,
        upload_duration_seconds: Optional[float] = None,
        user_agent: str = "NFT-IPFS-Uploader",
        status: str = "success",
    ) -> str:
        """
        Log a successful upload

        Args:
            upload_type: Type of upload ("image", "metadata", "json")
            filename: Original filename
            cid: IPFS Content Identifier
            file_size_bytes: Size of uploaded file in bytes
            ipfs_uri: Full IPFS URI (ipfs://...)
            gateway_url: HTTP gateway URL for access
            metadata: Additional metadata about the upload
            nft_metadata: NFT metadata (if applicable)
            related_cid: Related CID (e.g., image CID for metadata)
            upload_duration_seconds: Time taken to upload
            user_agent: Client identification
            status: Upload status (success, failed, partial)

        Returns:
            str: Upload ID for reference
        """
        data = self._load_log_data()

        upload_id = (
            f"upload_{len(data['uploads']) + 1}_{int(datetime.now().timestamp())}"
        )

        upload_entry = {
            "upload_id": upload_id,
            "timestamp": datetime.now().isoformat(),
            "upload_type": upload_type,
            "status": status,
            "file_info": {
                "original_filename": filename,
                "file_size_bytes": file_size_bytes,
                "file_type": self._get_file_type(filename),
            },
            "ipfs_info": {
                "cid": cid,
                "ipfs_uri": ipfs_uri,
                "gateway_url": gateway_url,
                "related_cid": related_cid,
            },
            "metadata": metadata or {},
            "nft_metadata": nft_metadata,
            "performance": {
                "upload_duration_seconds": upload_duration_seconds,
                "user_agent": user_agent,
            },
        }

        data["uploads"].append(upload_entry)
        self._save_log_data(data)

        return upload_id

    def log_failed_upload(
        self,
        upload_type: str,
        filename: str,
        file_size_bytes: int,
        error_message: str,
        error_code: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Log a failed upload

        Args:
            upload_type: Type of upload attempted
            filename: Original filename
            file_size_bytes: Size of file attempted to upload
            error_message: Error message
            error_code: Error code if available
            metadata: Additional metadata

        Returns:
            str: Upload ID for reference
        """
        data = self._load_log_data()

        upload_id = (
            f"failed_{len(data['uploads']) + 1}_{int(datetime.now().timestamp())}"
        )

        upload_entry = {
            "upload_id": upload_id,
            "timestamp": datetime.now().isoformat(),
            "upload_type": upload_type,
            "status": "failed",
            "file_info": {
                "original_filename": filename,
                "file_size_bytes": file_size_bytes,
                "file_type": self._get_file_type(filename),
            },
            "error_info": {"error_message": error_message, "error_code": error_code},
            "metadata": metadata or {},
        }

        data["uploads"].append(upload_entry)
        self._save_log_data(data)

        return upload_id

    def get_upload_stats(self) -> Dict[str, Any]:
        """
        Get upload statistics

        Returns:
            dict: Upload statistics
        """
        data = self._load_log_data()

        successful_uploads = [u for u in data["uploads"] if u["status"] == "success"]
        failed_uploads = [u for u in data["uploads"] if u["status"] == "failed"]

        image_uploads = [u for u in successful_uploads if u["upload_type"] == "image"]
        metadata_uploads = [
            u for u in successful_uploads if u["upload_type"] == "metadata"
        ]

        stats = {
            "total_uploads": len(data["uploads"]),
            "successful_uploads": len(successful_uploads),
            "failed_uploads": len(failed_uploads),
            "success_rate": len(successful_uploads) / len(data["uploads"])
            if data["uploads"]
            else 0,
            "uploads_by_type": {
                "image": len(image_uploads),
                "metadata": len(metadata_uploads),
            },
            "total_size_bytes": sum(
                u["file_info"]["file_size_bytes"] for u in successful_uploads
            ),
            "total_size_mb": sum(
                u["file_info"]["file_size_bytes"] for u in successful_uploads
            )
            / (1024 * 1024),
            "average_file_size_bytes": sum(
                u["file_info"]["file_size_bytes"] for u in successful_uploads
            )
            / len(successful_uploads)
            if successful_uploads
            else 0,
            "first_upload": data["uploads"][0]["timestamp"]
            if data["uploads"]
            else None,
            "last_upload": data["uploads"][-1]["timestamp"]
            if data["uploads"]
            else None,
        }

        return stats

    def get_recent_uploads(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent uploads

        Args:
            limit: Maximum number of uploads to return

        Returns:
            list: Recent uploads
        """
        data = self._load_log_data()
        return data["uploads"][-limit:]

    def search_uploads(
        self,
        upload_type: Optional[str] = None,
        status: Optional[str] = None,
        filename_contains: Optional[str] = None,
        cid: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search uploads by various criteria

        Args:
            upload_type: Filter by upload type
            status: Filter by status
            filename_contains: Filter by filename containing text
            cid: Filter by specific CID
            start_date: Filter by start date (ISO format)
            end_date: Filter by end date (ISO format)

        Returns:
            list: Matching uploads
        """
        data = self._load_log_data()
        results = data["uploads"]

        if upload_type:
            results = [u for u in results if u["upload_type"] == upload_type]

        if status:
            results = [u for u in results if u["status"] == status]

        if filename_contains:
            results = [
                u
                for u in results
                if filename_contains.lower()
                in u["file_info"]["original_filename"].lower()
            ]

        if cid:
            results = [u for u in results if u.get("ipfs_info", {}).get("cid") == cid]

        if start_date:
            results = [u for u in results if u["timestamp"] >= start_date]

        if end_date:
            results = [u for u in results if u["timestamp"] <= end_date]

        return results

    def get_nft_pairs(self) -> List[Dict[str, Any]]:
        """
        Get NFT pairs (image + metadata combinations)

        Returns:
            list: NFT pairs with both image and metadata
        """
        data = self._load_log_data()

        # Group by related_cid to find pairs
        pairs = []
        image_uploads = {
            u["ipfs_info"]["cid"]: u
            for u in data["uploads"]
            if u["upload_type"] == "image" and u["status"] == "success"
        }

        metadata_uploads = [
            u
            for u in data["uploads"]
            if u["upload_type"] == "metadata" and u["status"] == "success"
        ]

        for metadata_upload in metadata_uploads:
            related_cid = metadata_upload["ipfs_info"].get("related_cid")
            if related_cid and related_cid in image_uploads:
                pairs.append(
                    {
                        "nft_name": metadata_upload.get("nft_metadata", {}).get(
                            "name", "Unknown"
                        ),
                        "image_upload": image_uploads[related_cid],
                        "metadata_upload": metadata_upload,
                        "created_at": metadata_upload["timestamp"],
                        "image_uri": image_uploads[related_cid]["ipfs_info"][
                            "ipfs_uri"
                        ],
                        "metadata_uri": metadata_upload["ipfs_info"]["ipfs_uri"],
                        "nft_token_uri": metadata_upload["ipfs_info"][
                            "ipfs_uri"
                        ],  # This is the main URI
                    }
                )

        return sorted(pairs, key=lambda x: x["created_at"], reverse=True)

    def export_logs(
        self, output_file: Optional[str] = None, format_type: str = "json"
    ) -> str:
        """
        Export logs to file

        Args:
            output_file: Output file path (optional)
            format_type: Export format ("json", "csv")

        Returns:
            str: Path to exported file
        """
        data = self._load_log_data()

        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"uploads/logs/export_{timestamp}.{format_type}"

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format_type == "json":
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        elif format_type == "csv":
            import csv

            with open(output_path, "w", newline="", encoding="utf-8") as f:
                if data["uploads"]:
                    # Flatten the upload data for CSV
                    fieldnames = [
                        "upload_id",
                        "timestamp",
                        "upload_type",
                        "status",
                        "filename",
                        "file_size_bytes",
                        "cid",
                        "ipfs_uri",
                    ]

                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()

                    for upload in data["uploads"]:
                        row = {
                            "upload_id": upload["upload_id"],
                            "timestamp": upload["timestamp"],
                            "upload_type": upload["upload_type"],
                            "status": upload["status"],
                            "filename": upload["file_info"]["original_filename"],
                            "file_size_bytes": upload["file_info"]["file_size_bytes"],
                            "cid": upload.get("ipfs_info", {}).get("cid", ""),
                            "ipfs_uri": upload.get("ipfs_info", {}).get("ipfs_uri", ""),
                        }
                        writer.writerow(row)

        return str(output_path)

    def cleanup_old_logs(self, days_to_keep: int = 30):
        """
        Remove old log entries

        Args:
            days_to_keep: Number of days to keep logs
        """
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        cutoff_iso = cutoff_date.isoformat()

        data = self._load_log_data()
        data["uploads"] = [u for u in data["uploads"] if u["timestamp"] >= cutoff_iso]

        self._save_log_data(data)

    def _get_file_type(self, filename: str) -> str:
        """Get file type from filename"""
        extension = Path(filename).suffix.lower()

        type_mapping = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".svg": "image/svg+xml",
            ".webp": "image/webp",
            ".json": "application/json",
            ".txt": "text/plain",
        }

        return type_mapping.get(extension, "application/octet-stream")

    def filter_ignored_cids(self, ignored_cids: set) -> int:
        """
        Filter out uploads with ignored CIDs from the log

        Args:
            ignored_cids: Set of CIDs to remove from logs

        Returns:
            int: Number of entries removed
        """
        if not ignored_cids:
            return 0

        data = self._load_log_data()
        original_count = len(data["uploads"])

        # Filter out uploads with ignored CIDs
        data["uploads"] = [
            upload
            for upload in data["uploads"]
            if upload.get("ipfs_info", {}).get("cid", "") not in ignored_cids
            and upload.get("cid", "") not in ignored_cids
        ]

        filtered_count = len(data["uploads"])
        removed_count = original_count - filtered_count

        if removed_count > 0:
            self._save_log_data(data)

        return removed_count

    def get_recent_uploads_filtered(
        self, limit: int = 10, ignored_cids: set = None
    ) -> List[Dict[str, Any]]:
        """
        Get recent uploads filtered by ignored CIDs

        Args:
            limit: Maximum number of uploads to return
            ignored_cids: Set of CIDs to ignore

        Returns:
            list: Recent uploads (filtered)
        """
        data = self._load_log_data()
        uploads = data["uploads"]

        # Filter out ignored CIDs if provided
        if ignored_cids:
            uploads = [
                upload
                for upload in uploads
                if upload.get("ipfs_info", {}).get("cid", "") not in ignored_cids
                and upload.get("cid", "") not in ignored_cids
            ]

        return uploads[-limit:]

    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get data formatted for dashboard display

        Returns:
            dict: Dashboard data
        """
        stats = self.get_upload_stats()
        recent_uploads = self.get_recent_uploads(5)
        nft_pairs = self.get_nft_pairs()[:5]  # Last 5 NFTs

        return {
            "statistics": stats,
            "recent_uploads": recent_uploads,
            "recent_nfts": nft_pairs,
            "log_file_path": str(self.log_file),
            "log_file_size_bytes": self.log_file.stat().st_size
            if self.log_file.exists()
            else 0,
        }
