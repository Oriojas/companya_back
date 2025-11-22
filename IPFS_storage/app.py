"""
NFT Metadata Uploader - Streamlit Application
Upload images to IPFS and generate OpenSea-compatible metadata
"""

import json
import os
import sys
from datetime import datetime
from io import BytesIO
from typing import Any, Dict, Optional

import streamlit as st
from PIL import Image

# Add modules directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "modules"))

from metadata_builder import (
    build_nft_metadata,
    create_metadata_history_entry,
    format_metadata_preview,
    save_metadata_to_file,
    validate_metadata,
)
from pinata_client import PinataClient


def init_session_state():
    """Initialize Streamlit session state variables"""
    if "upload_history" not in st.session_state:
        st.session_state.upload_history = []
    if "current_metadata" not in st.session_state:
        st.session_state.current_metadata = None
    if "pinata_client" not in st.session_state:
        st.session_state.pinata_client = None


def load_pinata_client() -> Optional[PinataClient]:
    """Load and test Pinata client"""
    try:
        client = PinataClient()
        if client.test_authentication():
            return client
        else:
            st.error("❌ Failed to authenticate with Pinata API")
            return None
    except Exception as e:
        st.error(f"❌ Error initializing Pinata client: {str(e)}")
        st.error(
            "Please check your .env file contains PINATA_API_KEY and PINATA_SECRET_API_KEY"
        )
        return None


def validate_image_file(uploaded_file) -> bool:
    """Validate uploaded image file"""
    if uploaded_file is None:
        return False

    # Check file type
    allowed_types = [
        "image/png",
        "image/jpeg",
        "image/jpg",
        "image/gif",
        "image/svg+xml",
        "image/webp",
    ]
    if uploaded_file.type not in allowed_types:
        st.error(f"❌ Unsupported file type: {uploaded_file.type}")
        st.info("Supported formats: PNG, JPG, GIF, SVG, WEBP")
        return False

    # Check file size (100MB limit for Pinata)
    if uploaded_file.size > 100 * 1024 * 1024:
        st.error("❌ File too large. Maximum size is 100MB")
        return False

    return True


def save_history_entry(entry: Dict[str, Any]):
    """Save upload history entry to file"""
    history_file = os.path.join("uploads", "metadata_history", "upload_history.json")

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(history_file), exist_ok=True)

    # Load existing history
    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                history = data.get("uploads", [])
        except:
            pass

    # Add new entry
    history.append(entry)

    # Save updated history
    try:
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump({"uploads": history}, f, indent=2, ensure_ascii=False)
    except Exception as e:
        st.warning(f"⚠️ Could not save history: {str(e)}")


def load_upload_history() -> list:
    """Load upload history from file"""
    history_file = os.path.join("uploads", "metadata_history", "upload_history.json")

    if not os.path.exists(history_file):
        return []

    try:
        with open(history_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("uploads", [])
    except:
        return []


def main():
    """Main application function"""

    # Page configuration
    st.set_page_config(
        page_title="NFT IPFS Uploader",
        page_icon="🎨",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Initialize session state
    init_session_state()

    # Title and header
    st.title("🎨 NFT Metadata Uploader - IPFS Storage")
    st.markdown("Upload images to IPFS and generate OpenSea-compatible metadata")

    # Sidebar
    with st.sidebar:
        st.header("🔧 Configuration")

        # Initialize Pinata client
        if st.session_state.pinata_client is None:
            with st.spinner("Testing Pinata connection..."):
                st.session_state.pinata_client = load_pinata_client()

        if st.session_state.pinata_client:
            st.success("✅ Connected to Pinata")

            # Account info
            with st.expander("📊 Account Info"):
                try:
                    account_info = st.session_state.pinata_client.get_account_info()
                    if "error" not in account_info:
                        st.metric("Pin Count", account_info.get("pin_count", "N/A"))
                        st.metric(
                            "Pin Size", f"{account_info.get('pin_size_total', 0)} bytes"
                        )
                except:
                    st.info("Could not load account info")
        else:
            st.error("❌ Not connected to Pinata")
            st.stop()

        st.divider()

        # Upload history
        st.header("📜 Recent Uploads")
        history = load_upload_history()

        if history:
            # Show last 5 uploads
            for entry in history[-5:]:
                with st.expander(f"📄 {entry.get('name', 'Unknown')}"):
                    st.code(entry.get("nft_uri", ""), language=None)
                    st.caption(f"Uploaded: {entry.get('timestamp', '')[:19]}")
        else:
            st.info("No uploads yet")

    # Main content area
    tab1, tab2 = st.tabs(["🚀 Upload NFT", "📜 History"])

    with tab1:
        col1, col2 = st.columns([1, 1])

        # Left column - Upload and form
        with col1:
            st.header("📤 Upload Image")

            uploaded_file = st.file_uploader(
                "Choose an image file",
                type=["png", "jpg", "jpeg", "gif", "svg", "webp"],
                help="Supported formats: PNG, JPG, GIF, SVG, WEBP (Max: 100MB)",
            )

            if uploaded_file and validate_image_file(uploaded_file):
                # Display image preview
                try:
                    image = Image.open(uploaded_file)
                    st.image(
                        image,
                        caption=f"Preview: {uploaded_file.name}",
                        use_column_width=True,
                    )
                    st.success(
                        f"✅ File loaded: {uploaded_file.name} ({uploaded_file.size:,} bytes)"
                    )
                except Exception as e:
                    st.error(f"❌ Error loading image: {str(e)}")
                    uploaded_file = None

            st.divider()

            # Metadata form
            st.header("📝 NFT Metadata")

            with st.form("metadata_form"):
                # Basic information
                st.subheader("Basic Information")
                name = st.text_input(
                    "NFT Name *",
                    placeholder="Enter the name of your NFT",
                    help="This will be the title of your NFT",
                )

                description = st.text_area(
                    "Description *",
                    placeholder="Describe your NFT...",
                    help="Detailed description of your NFT. Supports markdown.",
                    height=100,
                )

                # Specific attributes
                st.subheader("Attributes")
                actividad = st.text_input(
                    "Actividad *",
                    placeholder="e.g., Swimming, Running, Reading",
                    help="Activity associated with this NFT",
                )

                usuario = st.text_input(
                    "Usuario *",
                    placeholder="e.g., John Doe",
                    help="User associated with this NFT",
                )

                acompanante = st.text_input(
                    "Acompañante *",
                    placeholder="e.g., Maria, Solo, Team Alpha",
                    help="Companion or team associated with this NFT",
                )

                tiempo = st.number_input(
                    "Tiempo *",
                    min_value=0,
                    max_value=10000,
                    value=1,
                    step=1,
                    help="Time value associated with this NFT",
                )

                # Form submission
                submit_button = st.form_submit_button(
                    "🚀 Upload to IPFS", type="primary"
                )

                # Validate required fields
                all_fields_filled = all(
                    [name, description, actividad, usuario, acompanante, uploaded_file]
                )

                if submit_button:
                    if not all_fields_filled:
                        st.error(
                            "❌ Please fill all required fields and upload an image"
                        )
                    else:
                        # Process upload
                        process_upload(
                            uploaded_file,
                            name,
                            description,
                            actividad,
                            usuario,
                            acompanante,
                            tiempo,
                        )

        # Right column - Preview and results
        with col2:
            st.header("👁️ Preview")

            # Generate preview metadata in real-time
            if uploaded_file and all(
                [name, description, actividad, usuario, acompanante]
            ):
                try:
                    preview_metadata = build_nft_metadata(
                        name=name,
                        description=description,
                        image_uri="ipfs://[IMAGE_WILL_BE_UPLOADED]",
                        actividad=actividad,
                        usuario=usuario,
                        acompanante=acompanante,
                        tiempo=tiempo,
                    )

                    st.subheader("📄 Metadata Preview")
                    st.code(format_metadata_preview(preview_metadata), language="json")

                    # Validate metadata
                    errors = validate_metadata(preview_metadata)
                    if errors:
                        st.warning("⚠️ Validation warnings:")
                        for error in errors:
                            st.text(f"• {error}")
                    else:
                        st.success("✅ Metadata structure is valid")

                except Exception as e:
                    st.error(f"❌ Error generating preview: {str(e)}")
            else:
                st.info("Fill the form to see metadata preview")

            # Results area
            if "last_upload_result" in st.session_state:
                st.divider()
                st.header("🎉 Upload Results")

                result = st.session_state.last_upload_result

                st.success("✅ Upload completed successfully!")

                # Display URIs
                st.subheader("📋 Generated URIs")

                # Image URI
                st.text("🖼️ Image URI:")
                st.code(result["image_uri"], language=None)

                # NFT Metadata URI (this is the main URI for the smart contract)
                st.text("🎯 NFT Token URI (use this in your smart contract):")
                st.code(result["metadata_uri"], language=None)

                # Gateway URLs for testing
                st.subheader("🌐 Gateway URLs (for testing)")
                st.text("Image Gateway:")
                st.markdown(f"[View Image]({result['image_gateway']})")

                st.text("Metadata Gateway:")
                st.markdown(f"[View Metadata]({result['metadata_gateway']})")

                # Clear result after showing
                if st.button("🗑️ Clear Results"):
                    del st.session_state.last_upload_result
                    st.rerun()

    with tab2:
        st.header("📜 Upload History")

        history = load_upload_history()

        if not history:
            st.info("No uploads yet. Upload your first NFT in the Upload tab!")
        else:
            st.success(f"Found {len(history)} uploads")

            # Display history in reverse chronological order
            for i, entry in enumerate(reversed(history)):
                with st.expander(
                    f"📄 {entry.get('name', f'Upload {len(history) - i}')} - {entry.get('timestamp', '')[:19]}"
                ):
                    col1, col2 = st.columns([1, 1])

                    with col1:
                        st.text("NFT Information:")
                        st.write(f"**Name:** {entry.get('name', 'N/A')}")
                        st.write(f"**Timestamp:** {entry.get('timestamp', 'N/A')}")

                        st.text("IPFS URIs:")
                        st.code(
                            f"Image: {entry.get('image_uri', 'N/A')}", language=None
                        )
                        st.code(
                            f"NFT URI: {entry.get('nft_uri', 'N/A')}", language=None
                        )

                    with col2:
                        if entry.get("gateway_url"):
                            st.text("Gateway Links:")
                            st.markdown(
                                f"[View Metadata]({entry.get('gateway_url', '')})"
                            )

                        # Show metadata
                        if entry.get("metadata"):
                            with st.expander("View Metadata JSON"):
                                st.code(
                                    json.dumps(entry["metadata"], indent=2),
                                    language="json",
                                )


def process_upload(
    uploaded_file,
    name: str,
    description: str,
    actividad: str,
    usuario: str,
    acompanante: str,
    tiempo: int,
):
    """Process the complete upload workflow"""

    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        # Step 1: Upload image
        status_text.text("📤 Uploading image to IPFS...")
        progress_bar.progress(25)

        # Get file bytes
        file_bytes = uploaded_file.read()
        uploaded_file.seek(0)  # Reset file pointer

        # Upload image to Pinata
        image_cid = st.session_state.pinata_client.upload_file(
            file_bytes=file_bytes,
            filename=uploaded_file.name,
            metadata={"name": f"{name}_image"},
        )

        image_uri = st.session_state.pinata_client.get_ipfs_uri(image_cid)
        image_gateway = st.session_state.pinata_client.get_gateway_url(image_cid)

        progress_bar.progress(50)
        status_text.text("🔨 Generating metadata...")

        # Step 2: Create metadata
        metadata = build_nft_metadata(
            name=name,
            description=description,
            image_uri=image_uri,
            actividad=actividad,
            usuario=usuario,
            acompanante=acompanante,
            tiempo=tiempo,
        )

        progress_bar.progress(75)
        status_text.text("📝 Uploading metadata to IPFS...")

        # Step 3: Upload metadata
        metadata_cid = st.session_state.pinata_client.upload_json(
            json_data=metadata, name=f"{name}_metadata"
        )

        metadata_uri = st.session_state.pinata_client.get_ipfs_uri(metadata_cid)
        metadata_gateway = st.session_state.pinata_client.get_gateway_url(metadata_cid)

        progress_bar.progress(100)
        status_text.text("✅ Upload completed!")

        # Step 4: Save results
        result = {
            "image_cid": image_cid,
            "metadata_cid": metadata_cid,
            "image_uri": image_uri,
            "metadata_uri": metadata_uri,
            "image_gateway": image_gateway,
            "metadata_gateway": metadata_gateway,
        }

        # Save to session state for display
        st.session_state.last_upload_result = result

        # Save to history
        history_entry = create_metadata_history_entry(
            metadata=metadata,
            image_cid=image_cid,
            metadata_cid=metadata_cid,
            image_uri=image_uri,
            metadata_uri=metadata_uri,
            gateway_url=metadata_gateway,
        )

        save_history_entry(history_entry)

        # Save metadata file locally
        metadata_filename = (
            f"{name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        metadata_filepath = os.path.join(
            "uploads", "metadata_history", metadata_filename
        )
        save_metadata_to_file(metadata, metadata_filepath)

        progress_bar.empty()
        status_text.empty()

        st.rerun()

    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"❌ Upload failed: {str(e)}")


if __name__ == "__main__":
    main()
