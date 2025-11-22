#!/usr/bin/env python3
"""
Upload Logs Viewer
Standalone script to view and analyze IPFS upload logs
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add modules directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "modules"))


def load_logs(log_file: str = "uploads/logs/upload_log.json") -> Dict[str, Any]:
    """Load upload logs from file"""
    log_path = Path(log_file)

    if not log_path.exists():
        return {"uploads": []}

    try:
        with open(log_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"uploads": []}


def print_header(title: str):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_stats(uploads: List[Dict[str, Any]]):
    """Print upload statistics"""
    if not uploads:
        print("📊 No uploads found")
        return

    successful = [u for u in uploads if u.get("status") == "success"]
    failed = [u for u in uploads if u.get("status") == "failed"]

    image_uploads = [u for u in successful if u.get("upload_type") == "image"]
    metadata_uploads = [u for u in successful if u.get("upload_type") == "metadata"]

    total_size_bytes = sum(u.get("file_size_bytes", 0) for u in successful)
    total_size_mb = total_size_bytes / (1024 * 1024)

    print(f"📊 Upload Statistics:")
    print(f"   Total uploads: {len(uploads)}")
    print(f"   ✅ Successful: {len(successful)}")
    print(f"   ❌ Failed: {len(failed)}")
    print(f"   📸 Images: {len(image_uploads)}")
    print(f"   📝 Metadata: {len(metadata_uploads)}")
    print(f"   💾 Total size: {total_size_mb:.2f} MB ({total_size_bytes:,} bytes)")

    if successful:
        avg_size = total_size_bytes / len(successful)
        print(f"   📏 Average file size: {avg_size / 1024:.1f} KB")

    if uploads:
        success_rate = len(successful) / len(uploads) * 100
        print(f"   📈 Success rate: {success_rate:.1f}%")

        first_upload = min(u.get("timestamp", "") for u in uploads)
        last_upload = max(u.get("timestamp", "") for u in uploads)

        print(f"   ⏰ First upload: {first_upload[:19].replace('T', ' ')}")
        print(f"   ⏰ Last upload: {last_upload[:19].replace('T', ' ')}")


def print_recent_uploads(uploads: List[Dict[str, Any]], limit: int = 10):
    """Print recent uploads"""
    if not uploads:
        return

    recent = uploads[-limit:]
    recent.reverse()  # Most recent first

    print(f"\n📄 Recent Uploads (last {len(recent)}):")
    print("-" * 60)

    for i, upload in enumerate(recent, 1):
        status_icon = "✅" if upload.get("status") == "success" else "❌"
        type_icon = "🖼️" if upload.get("upload_type") == "image" else "📝"

        timestamp = upload.get("timestamp", "Unknown")[:19].replace("T", " ")
        filename = upload.get("filename", "Unknown")
        file_size = upload.get("file_size_bytes", 0)
        upload_type = upload.get("upload_type", "unknown")

        print(f"{i:2d}. {status_icon} {type_icon} [{upload_type.upper()}] {filename}")
        print(f"     📅 {timestamp} | 💾 {file_size:,} bytes")

        if upload.get("status") == "success":
            cid = upload.get("cid", "N/A")
            print(f"     🔗 {cid}")

            nft_name = upload.get("nft_name")
            if nft_name:
                print(f"     🎨 NFT: {nft_name}")

        if upload.get("error"):
            print(f"     ❌ Error: {upload['error']}")

        print()


def print_nft_pairs(uploads: List[Dict[str, Any]]):
    """Print NFT pairs (image + metadata combinations)"""
    # Group by NFT name or related uploads
    nft_pairs = {}

    for upload in uploads:
        if upload.get("status") != "success":
            continue

        nft_name = upload.get("nft_name", "Unknown")
        upload_type = upload.get("upload_type")

        if nft_name not in nft_pairs:
            nft_pairs[nft_name] = {"image": None, "metadata": None}

        nft_pairs[nft_name][upload_type] = upload

    # Filter complete pairs
    complete_pairs = {
        name: pair
        for name, pair in nft_pairs.items()
        if pair["image"] and pair["metadata"]
    }

    if not complete_pairs:
        print("\n🎨 No complete NFT pairs found")
        return

    print(f"\n🎨 Complete NFT Pairs ({len(complete_pairs)}):")
    print("-" * 60)

    for i, (nft_name, pair) in enumerate(complete_pairs.items(), 1):
        image_upload = pair["image"]
        metadata_upload = pair["metadata"]

        print(f"{i}. 🎨 {nft_name}")

        # Image info
        image_size = image_upload.get("file_size_bytes", 0)
        image_cid = image_upload.get("cid", "N/A")
        print(f"   🖼️  Image: {image_size:,} bytes | CID: {image_cid}")

        # Metadata info
        metadata_size = metadata_upload.get("file_size_bytes", 0)
        metadata_cid = metadata_upload.get("cid", "N/A")
        print(f"   📝  Metadata: {metadata_size:,} bytes | CID: {metadata_cid}")

        # NFT Token URI (this is what goes in smart contract)
        metadata_uri = metadata_upload.get("ipfs_uri", "N/A")
        print(f"   🎯  NFT Token URI: {metadata_uri}")

        # Creation date
        created_at = metadata_upload.get("timestamp", "")[:19].replace("T", " ")
        print(f"   📅  Created: {created_at}")
        print()


def print_failed_uploads(uploads: List[Dict[str, Any]]):
    """Print failed uploads for debugging"""
    failed = [u for u in uploads if u.get("status") == "failed"]

    if not failed:
        print("\n✅ No failed uploads found")
        return

    print(f"\n❌ Failed Uploads ({len(failed)}):")
    print("-" * 60)

    for i, upload in enumerate(failed, 1):
        timestamp = upload.get("timestamp", "Unknown")[:19].replace("T", " ")
        filename = upload.get("filename", "Unknown")
        upload_type = upload.get("upload_type", "unknown")
        error = upload.get("error", "Unknown error")

        print(f"{i}. [{upload_type.upper()}] {filename}")
        print(f"   📅 {timestamp}")
        print(f"   ❌ {error}")
        print()


def search_uploads(uploads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Interactive search for uploads"""
    print("\n🔍 Search Uploads")
    print("Enter search criteria (press Enter to skip):")

    # Get search criteria
    filename_search = input("🔤 Filename contains: ").strip()
    cid_search = input("🔗 CID equals: ").strip()
    type_search = input("📁 Type (image/metadata): ").strip()
    status_search = input("📊 Status (success/failed): ").strip()

    results = uploads.copy()

    if filename_search:
        results = [
            u
            for u in results
            if filename_search.lower() in u.get("filename", "").lower()
        ]

    if cid_search:
        results = [u for u in results if u.get("cid") == cid_search]

    if type_search:
        results = [u for u in results if u.get("upload_type") == type_search.lower()]

    if status_search:
        results = [u for u in results if u.get("status") == status_search.lower()]

    print(f"\n🎯 Found {len(results)} matching uploads:")

    if results:
        print_recent_uploads(results, len(results))

    return results


def export_logs(uploads: List[Dict[str, Any]], format_type: str = "json"):
    """Export logs to file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if format_type == "json":
        output_file = f"uploads/logs/export_{timestamp}.json"

        export_data = {
            "exported_at": datetime.now().isoformat(),
            "total_uploads": len(uploads),
            "uploads": uploads,
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

    elif format_type == "csv":
        import csv

        output_file = f"uploads/logs/export_{timestamp}.csv"

        with open(output_file, "w", newline="", encoding="utf-8") as f:
            if uploads:
                fieldnames = [
                    "timestamp",
                    "upload_type",
                    "status",
                    "filename",
                    "file_size_bytes",
                    "cid",
                    "ipfs_uri",
                    "error",
                    "nft_name",
                ]

                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for upload in uploads:
                    row = {
                        "timestamp": upload.get("timestamp", ""),
                        "upload_type": upload.get("upload_type", ""),
                        "status": upload.get("status", ""),
                        "filename": upload.get("filename", ""),
                        "file_size_bytes": upload.get("file_size_bytes", 0),
                        "cid": upload.get("cid", ""),
                        "ipfs_uri": upload.get("ipfs_uri", ""),
                        "error": upload.get("error", ""),
                        "nft_name": upload.get("nft_name", ""),
                    }
                    writer.writerow(row)

    print(f"✅ Exported logs to: {output_file}")
    return output_file


def interactive_menu():
    """Interactive menu for log viewing"""
    log_data = load_logs()
    uploads = log_data.get("uploads", [])

    while True:
        print_header("Upload Logs Viewer - Interactive Menu")

        print("📋 Options:")
        print("1. 📊 View Statistics")
        print("2. 📄 View Recent Uploads")
        print("3. 🎨 View NFT Pairs")
        print("4. ❌ View Failed Uploads")
        print("5. 🔍 Search Uploads")
        print("6. 📥 Export Logs")
        print("7. 🔄 Reload Logs")
        print("0. 🚪 Exit")

        choice = input("\nSelect option (0-7): ").strip()

        if choice == "0":
            print("👋 Goodbye!")
            break
        elif choice == "1":
            print_stats(uploads)
        elif choice == "2":
            limit = input("Number of recent uploads to show (default: 10): ").strip()
            limit = int(limit) if limit.isdigit() else 10
            print_recent_uploads(uploads, limit)
        elif choice == "3":
            print_nft_pairs(uploads)
        elif choice == "4":
            print_failed_uploads(uploads)
        elif choice == "5":
            search_uploads(uploads)
        elif choice == "6":
            format_choice = input("Export format (json/csv) [json]: ").strip().lower()
            if not format_choice:
                format_choice = "json"
            export_logs(uploads, format_choice)
        elif choice == "7":
            log_data = load_logs()
            uploads = log_data.get("uploads", [])
            print("🔄 Logs reloaded")
        else:
            print("❌ Invalid option")

        input("\nPress Enter to continue...")


def main():
    """Main function"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        log_data = load_logs()
        uploads = log_data.get("uploads", [])

        if command == "stats":
            print_header("Upload Statistics")
            print_stats(uploads)

        elif command == "recent":
            limit = (
                int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 10
            )
            print_header(f"Recent Uploads (last {limit})")
            print_recent_uploads(uploads, limit)

        elif command == "nfts":
            print_header("NFT Pairs")
            print_nft_pairs(uploads)

        elif command == "failed":
            print_header("Failed Uploads")
            print_failed_uploads(uploads)

        elif command == "export":
            format_type = sys.argv[2] if len(sys.argv) > 2 else "json"
            export_logs(uploads, format_type)

        elif command == "help":
            print_header("Upload Logs Viewer - Help")
            print("Usage:")
            print("  python view_logs.py [command] [options]")
            print("")
            print("Commands:")
            print("  stats          Show upload statistics")
            print("  recent [N]     Show last N uploads (default: 10)")
            print("  nfts           Show complete NFT pairs")
            print("  failed         Show failed uploads")
            print("  export [format] Export logs (json/csv)")
            print("  help           Show this help")
            print("")
            print("Interactive mode:")
            print("  python view_logs.py")

        else:
            print(f"❌ Unknown command: {command}")
            print("Use 'python view_logs.py help' for usage information")

    else:
        # Interactive mode
        interactive_menu()


if __name__ == "__main__":
    main()
