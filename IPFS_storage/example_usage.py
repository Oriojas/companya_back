#!/usr/bin/env python3
"""
Example Usage of IPFS Storage Modules
Demonstrates how to use the modules programmatically without Streamlit
"""

import os
import sys
from pathlib import Path

# Add modules directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "modules"))

from dotenv import load_dotenv
from modules.metadata_builder import (
    build_nft_metadata,
    format_metadata_preview,
    save_metadata_to_file,
    validate_metadata,
)
from modules.pinata_client import PinataClient

# Load environment variables
load_dotenv()


def example_upload_image():
    """Example: Upload an image file to IPFS"""
    print("📸 Example 1: Upload Image to IPFS")
    print("-" * 40)

    try:
        # Initialize client
        client = PinataClient()

        # For this example, we'll create a simple text file to upload
        # In real usage, you'd read an actual image file
        sample_content = b"This is a sample file for testing IPFS upload"
        filename = "sample_image.txt"

        # Upload file
        print(f"Uploading {filename}...")
        cid = client.upload_file(
            file_bytes=sample_content,
            filename=filename,
            metadata={"name": "Sample Upload", "type": "example"},
        )

        # Get URIs
        ipfs_uri = client.get_ipfs_uri(cid)
        gateway_url = client.get_gateway_url(cid)

        print(f"✅ Upload successful!")
        print(f"   CID: {cid}")
        print(f"   IPFS URI: {ipfs_uri}")
        print(f"   Gateway URL: {gateway_url}")

        return cid, ipfs_uri

    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return None, None


def example_create_metadata(image_uri):
    """Example: Create NFT metadata"""
    print("\n📝 Example 2: Create NFT Metadata")
    print("-" * 40)

    try:
        # Create metadata
        metadata = build_nft_metadata(
            name="My First NFT",
            description="This is an example NFT created with our IPFS uploader",
            image_uri=image_uri or "ipfs://QmExampleImageCID",
            actividad="Programming",
            usuario="Developer",
            acompanante="AI Assistant",
            tiempo=60,
        )

        print("✅ Metadata created!")
        print("Preview:")
        print(format_metadata_preview(metadata))

        # Validate metadata
        errors = validate_metadata(metadata)
        if errors:
            print("\n⚠️  Validation warnings:")
            for error in errors:
                print(f"   • {error}")
        else:
            print("\n✅ Metadata is valid!")

        return metadata

    except Exception as e:
        print(f"❌ Metadata creation failed: {e}")
        return None


def example_upload_metadata(metadata):
    """Example: Upload metadata JSON to IPFS"""
    print("\n📤 Example 3: Upload Metadata to IPFS")
    print("-" * 40)

    try:
        # Initialize client
        client = PinataClient()

        # Upload metadata
        print("Uploading metadata JSON...")
        cid = client.upload_json(json_data=metadata, name="example_nft_metadata")

        # Get URIs
        ipfs_uri = client.get_ipfs_uri(cid)
        gateway_url = client.get_gateway_url(cid)

        print(f"✅ Metadata upload successful!")
        print(f"   CID: {cid}")
        print(f"   NFT Token URI: {ipfs_uri}")
        print(f"   Gateway URL: {gateway_url}")

        return cid, ipfs_uri

    except Exception as e:
        print(f"❌ Metadata upload failed: {e}")
        return None, None


def example_save_local_metadata(metadata):
    """Example: Save metadata to local file"""
    print("\n💾 Example 4: Save Metadata Locally")
    print("-" * 40)

    try:
        # Create output directory
        output_dir = Path("uploads/metadata_history")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save metadata
        filepath = output_dir / "example_metadata.json"
        success = save_metadata_to_file(metadata, str(filepath))

        if success:
            print(f"✅ Metadata saved to: {filepath}")
        else:
            print("❌ Failed to save metadata")

    except Exception as e:
        print(f"❌ Save failed: {e}")


def example_batch_operations():
    """Example: Batch operations for multiple NFTs"""
    print("\n📦 Example 5: Batch Operations")
    print("-" * 40)

    try:
        client = PinataClient()

        # Example data for multiple NFTs
        nft_data = [
            {
                "name": "NFT #001",
                "description": "First NFT in collection",
                "actividad": "Swimming",
                "usuario": "Alice",
                "acompanante": "Bob",
                "tiempo": 30,
            },
            {
                "name": "NFT #002",
                "description": "Second NFT in collection",
                "actividad": "Running",
                "usuario": "Charlie",
                "acompanante": "Dana",
                "tiempo": 45,
            },
        ]

        print(f"Processing {len(nft_data)} NFTs...")

        for i, nft in enumerate(nft_data, 1):
            print(f"\nProcessing NFT #{i}...")

            # Create metadata (using placeholder image URI)
            metadata = build_nft_metadata(
                name=nft["name"],
                description=nft["description"],
                image_uri=f"ipfs://QmExampleImage{i:03d}",
                actividad=nft["actividad"],
                usuario=nft["usuario"],
                acompanante=nft["acompanante"],
                tiempo=nft["tiempo"],
            )

            # Upload metadata
            cid = client.upload_json(metadata, f"{nft['name']}_metadata")
            uri = client.get_ipfs_uri(cid)

            print(f"   ✅ {nft['name']}: {uri}")

        print(f"\n🎉 Batch processing complete!")

    except Exception as e:
        print(f"❌ Batch processing failed: {e}")


def example_account_management():
    """Example: Account management operations"""
    print("\n👤 Example 6: Account Management")
    print("-" * 40)

    try:
        client = PinataClient()

        # Test connection
        if client.test_authentication():
            print("✅ Connected to Pinata")
        else:
            print("❌ Connection failed")
            return

        # Get account info
        print("\n📊 Account Information:")
        account_info = client.get_account_info()

        if "error" not in account_info:
            print(f"   Pin Count: {account_info.get('pin_count', 'N/A')}")
            print(f"   Total Size: {account_info.get('pin_size_total', 'N/A')} bytes")

        # Get recent pins
        print("\n📌 Recent Pins:")
        pin_list = client.get_pin_list(limit=5)

        if "error" not in pin_list and "rows" in pin_list:
            for pin in pin_list["rows"][:3]:  # Show first 3
                print(
                    f"   • {pin.get('metadata', {}).get('name', 'Unnamed')}: {pin.get('ipfs_pin_hash', 'No CID')}"
                )

    except Exception as e:
        print(f"❌ Account management failed: {e}")


def main():
    """Main example function"""
    print("🎨 NFT IPFS Storage - Example Usage")
    print("=" * 50)

    # Check if .env exists
    if not Path(".env").exists():
        print("❌ .env file not found!")
        print("Please copy .env.example to .env and configure your Pinata credentials")
        return

    # Check environment variables
    if not os.getenv("PINATA_API_KEY") or not os.getenv("PINATA_SECRET_API_KEY"):
        print("❌ Pinata credentials not found in .env file!")
        return

    try:
        # Run examples

        # Example 1: Upload image
        image_cid, image_uri = example_upload_image()

        # Example 2: Create metadata
        metadata = example_create_metadata(image_uri)

        if metadata:
            # Example 3: Upload metadata
            metadata_cid, nft_uri = example_upload_metadata(metadata)

            # Example 4: Save locally
            example_save_local_metadata(metadata)

        # Example 5: Batch operations
        example_batch_operations()

        # Example 6: Account management
        example_account_management()

        print("\n🎉 All examples completed!")
        print("\nNote: This example uses placeholder data.")
        print("In real usage, you would:")
        print("1. Read actual image files")
        print("2. Process real NFT data")
        print("3. Handle errors appropriately")
        print("4. Implement proper logging")

    except KeyboardInterrupt:
        print("\n👋 Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
