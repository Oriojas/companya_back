"""
NFT Metadata Uploader - Streamlit Application
Upload images to Filecoin and generate OpenSea-compatible metadata
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

from filecoin_client import FilecoinCloudClient
from filecoin_direct_client import FilecoinDirectClient
from metadata_builder import (
    build_nft_metadata,
    format_metadata_preview,
    save_metadata_to_file,
    validate_metadata,
)
from pinata_client import PinataClient
from upload_logger import UploadLogger


def init_session_state():
    """Initialize Streamlit session state variables"""
    if "current_metadata" not in st.session_state:
        st.session_state.current_metadata = None
    if "pinata_client" not in st.session_state:
        st.session_state.pinata_client = None
    if "filecoin_client" not in st.session_state:
        st.session_state.filecoin_client = None
    if "filecoin_direct_client" not in st.session_state:
        st.session_state.filecoin_direct_client = None
    if "storage_provider" not in st.session_state:
        st.session_state.storage_provider = "filecoin_direct"


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


def load_filecoin_client() -> Optional[FilecoinCloudClient]:
    """Load and test Filecoin Cloud client"""
    try:
        client = FilecoinCloudClient()
        if client.test_authentication():
            return client
        else:
            st.error("❌ Failed to authenticate with Filecoin Cloud")
            return None
    except Exception as e:
        st.error(f"❌ Error initializing Filecoin client: {str(e)}")
        st.error("Please check your .env file contains FILECOIN_PRIVATE_KEY")
        return None


def load_filecoin_direct_client() -> Optional[FilecoinDirectClient]:
    """Load and test Filecoin Direct client with improved error handling"""
    try:
        client = FilecoinDirectClient()

        # Test connection with retry logic
        with st.spinner("Conectando a la red Filecoin..."):
            if client.test_authentication():
                st.success("✅ Conectado a Filecoin exitosamente")
                return client
            else:
                st.error("❌ No se pudo conectar a la red Filecoin")
                st.error("Verifique su conexión a internet y las credenciales")
                return None

    except TimeoutError as e:
        st.error("❌ Timeout de conexión a Filecoin")
        st.error(
            "La red Filecoin está tardando demasiado en responder. Intente nuevamente."
        )
        st.info("💡 Consejo: Verifique su conexión a internet")
        return None

    except ConnectionError as e:
        st.error("❌ Error de conexión a Filecoin")
        st.error("No se pudo establecer conexión con la red Filecoin")
        st.info("💡 Consejo: Verifique que no hay problemas de firewall")
        return None

    except ValueError as e:
        st.error("❌ Error de configuración")
        st.error("Falta FILECOIN_PRIVATE_KEY en las variables de entorno")
        st.info("💡 Consejo: Verifique su archivo .env")
        return None

    except Exception as e:
        st.error(f"❌ Error inesperado: {str(e)}")
        st.error("Por favor revise la configuración e intente nuevamente")
        return None


def validate_image_file(uploaded_file) -> bool:
    """Validate uploaded image file"""
    if uploaded_file is None:
        return False

    # Check file type
    allowed_types = ["png", "jpg", "jpeg", "gif", "webp"]
    file_extension = uploaded_file.name.split(".")[-1].lower()

    if file_extension not in allowed_types:
        st.error(
            f"❌ Unsupported file type: {file_extension}. "
            f"Supported formats: {', '.join(allowed_types)}"
        )
        return False

    # Check file size (100MB limit)
    file_size = uploaded_file.size
    max_size = 100 * 1024 * 1024  # 100MB in bytes

    if file_size > max_size:
        st.error(f"❌ File too large. Maximum size is {max_size // (1024 * 1024)}MB")
        return False

    if file_size == 0:
        st.error("❌ File is empty")
        return False

    return True


def main():
    """Main application function"""

    # Page configuration
    st.set_page_config(
        page_title="NFT Filecoin Uploader",
        page_icon="🔷",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Initialize session state
    init_session_state()

    # Custom CSS for Filecoin theme
    st.markdown(
        """
    <style>
    /* Filecoin brand colors */
    :root {
        --filecoin-primary: #0EA2DF;
        --filecoin-secondary: #2E86AB;
        --filecoin-accent: #A23B72;
        --filecoin-dark: #1E293B;
        --filecoin-light: #F8FAFB;
        --filecoin-success: #10B981;
        --filecoin-warning: #F59E0B;
        --filecoin-error: #EF4444;
    }

    /* Main title styling */
    .main-title {
        color: var(--filecoin-dark);
        text-align: center;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, var(--filecoin-primary), var(--filecoin-secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .subtitle {
        color: var(--filecoin-dark);
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        opacity: 0.8;
    }

    /* Sidebar styling */
    .css-1d391kg {
        background-color: var(--filecoin-light);
    }

    /* Success messages */
    .stSuccess {
        background-color: rgba(16, 185, 129, 0.1);
        color: var(--filecoin-success);
        border-left: 4px solid var(--filecoin-success);
    }

    /* Error messages */
    .stError {
        background-color: rgba(239, 68, 68, 0.1);
        color: var(--filecoin-error);
        border-left: 4px solid var(--filecoin-error);
    }

    /* Warning messages */
    .stWarning {
        background-color: rgba(245, 158, 11, 0.1);
        color: var(--filecoin-warning);
        border-left: 4px solid var(--filecoin-warning);
    }

    /* Info messages */
    .stInfo {
        background-color: rgba(14, 162, 223, 0.1);
        color: var(--filecoin-primary);
        border-left: 4px solid var(--filecoin-primary);
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, var(--filecoin-primary), var(--filecoin-secondary));
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, var(--filecoin-secondary), var(--filecoin-accent));
        box-shadow: 0 4px 12px rgba(14, 162, 223, 0.3);
        transform: translateY(-2px);
    }

    /* Form submit button */
    .stFormSubmitButton > button {
        background: linear-gradient(135deg, var(--filecoin-primary), var(--filecoin-secondary));
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 1.1rem;
        font-weight: 700;
        padding: 0.75rem 2rem;
        width: 100%;
        transition: all 0.3s ease;
    }

    .stFormSubmitButton > button:hover {
        background: linear-gradient(135deg, var(--filecoin-secondary), var(--filecoin-accent));
        box-shadow: 0 6px 20px rgba(14, 162, 223, 0.4);
        transform: translateY(-2px);
    }

    /* Code blocks */
    .stCode {
        background-color: var(--filecoin-light);
        border: 1px solid var(--filecoin-primary);
        border-radius: 6px;
    }

    /* Metrics */
    .metric-container {
        background-color: var(--filecoin-light);
        border-radius: 8px;
        padding: 1rem;
        border-left: 4px solid var(--filecoin-primary);
    }

    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--filecoin-primary), var(--filecoin-secondary));
    }

    /* Expander */
    .streamlit-expanderHeader {
        background-color: var(--filecoin-light);
        color: var(--filecoin-dark);
        border-radius: 6px;
    }

    /* Radio buttons */
    .stRadio > div {
        background-color: var(--filecoin-light);
        border-radius: 8px;
        padding: 1rem;
    }

    /* File uploader */
    .uploadedFile {
        background-color: var(--filecoin-light);
        border: 2px dashed var(--filecoin-primary);
        border-radius: 8px;
    }

    /* Headers */
    h1, h2, h3 {
        color: var(--filecoin-dark);
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: var(--filecoin-light);
        color: var(--filecoin-dark);
        border-radius: 6px 6px 0 0;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--filecoin-primary), var(--filecoin-secondary));
        color: white;
    }

    /* Spinner */
    .stSpinner > div {
        border-top-color: var(--filecoin-primary);
    }

    /* Container borders */
    .element-container {
        border-radius: 8px;
    }

    /* Custom success box */
    .success-box {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(14, 162, 223, 0.1));
        border: 1px solid var(--filecoin-success);
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
    }

    /* Custom info box */
    .info-box {
        background: linear-gradient(135deg, rgba(14, 162, 223, 0.1), rgba(46, 134, 171, 0.1));
        border: 1px solid var(--filecoin-primary);
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Title and header
    st.markdown(
        '<h1 class="main-title">🔷 NFT Metadata Uploader - Filecoin Direct</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="subtitle">Upload images to Filecoin and generate OpenSea-compatible metadata</p>',
        unsafe_allow_html=True,
    )

    # Sidebar
    with st.sidebar:
        st.header("🔧 Configuration")

        # Storage provider selection
        st.subheader("📡 Storage Provider")
        provider = st.radio(
            "Choose storage provider:",
            ["filecoin_direct", "pinata", "filecoin"],
            format_func=lambda x: "🔷 Filecoin Direct"
            if x == "filecoin_direct"
            else "📌 Pinata IPFS"
            if x == "pinata"
            else "🟠 Filecoin Cloud (Legacy)",
            key="storage_provider_radio",
        )

        if provider != st.session_state.storage_provider:
            st.session_state.storage_provider = provider
            st.rerun()

        # Initialize selected client
        if st.session_state.storage_provider == "filecoin_direct":
            if st.session_state.filecoin_direct_client is None:
                st.session_state.filecoin_direct_client = load_filecoin_direct_client()

            if st.session_state.filecoin_direct_client:
                st.success("✅ Conectado a Filecoin Direct")

                # Connection status info
                with st.expander("🔗 Estado de Conexión"):
                    client = st.session_state.filecoin_direct_client
                    st.info(f"**RPC URL activa:** {client.rpc_url}")
                    st.info(f"**URLs disponibles:** {len(client.rpc_urls)}")
                    st.info(f"**Timeout:** {client.timeout}s")

                    if st.button("🔄 Probar Conexión", key="test_connection"):
                        with st.spinner("Probando conexión..."):
                            try:
                                if client.test_authentication():
                                    st.success("✅ Conexión exitosa")
                                else:
                                    st.error("❌ Fallo en la conexión")
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")

                # Account info
                with st.expander("📊 Información de Cuenta"):
                    try:
                        col1, col2 = st.columns(2)

                        with col1:
                            with st.spinner("Obteniendo balance..."):
                                balance_info = client.get_balance()
                                if balance_info.get("success"):
                                    balances = balance_info.get("balances", {})
                                    st.metric(
                                        "Balance FIL", f"{balances.get('FIL', '0')} FIL"
                                    )
                                else:
                                    st.warning("No se pudo obtener el balance")

                        with col2:
                            with st.spinner("Obteniendo info de red..."):
                                storage_info = client.get_storage_info()
                                if storage_info.get("success"):
                                    info = storage_info.get("info", {})
                                    st.metric("Red", info.get("network", "Desconocida"))
                                    st.metric(
                                        "Proveedores", info.get("totalProviders", "0")
                                    )
                                else:
                                    st.warning(
                                        "No se pudo obtener info de almacenamiento"
                                    )

                    except Exception as e:
                        st.warning(f"⚠️ Error al cargar información: {str(e)}")
                        st.info("💡 Esto puede ser temporal - intente nuevamente")
            else:
                st.error("❌ No se pudo conectar a Filecoin Direct")
                st.info("🔄 Intente cambiar de proveedor o reconectarse")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 Reconectar", key="reconnect_filecoin"):
                        st.session_state.filecoin_direct_client = None
                        st.rerun()
                with col2:
                    if st.button("⚙️ Cambiar Proveedor", key="change_provider"):
                        st.session_state.storage_provider = "pinata"
                        st.rerun()
                st.stop()

        elif st.session_state.storage_provider == "pinata":
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
                                "Pin Size",
                                f"{account_info.get('pin_size_total', 0)} bytes",
                            )
                    except:
                        st.info("Could not load account info")
            else:
                st.error("❌ Not connected to Pinata")
                st.stop()

        else:  # filecoin legacy
            if st.session_state.filecoin_client is None:
                with st.spinner("Testing Filecoin Cloud connection..."):
                    st.session_state.filecoin_client = load_filecoin_client()

            if st.session_state.filecoin_client:
                st.success("✅ Connected to Filecoin Cloud")

                # Account info
                with st.expander("📊 Account Info"):
                    try:
                        balance_info = st.session_state.filecoin_client.get_balance()
                        if "error" not in balance_info:
                            balances = balance_info.get("balances", {})
                            st.metric(
                                "USDFC Balance", f"{balances.get('USDFC', '0')} USDFC"
                            )
                            st.metric("FIL Balance", f"{balances.get('FIL', '0')} FIL")
                    except:
                        st.info("Could not load balance info")

                    try:
                        storage_info = (
                            st.session_state.filecoin_client.get_storage_info()
                        )
                        if "error" not in storage_info:
                            info = storage_info.get("info", {})
                            st.metric(
                                "Active Providers", info.get("activeProviders", "N/A")
                            )
                    except:
                        pass
            else:
                st.error("❌ Not connected to Filecoin Cloud")
                st.info("💡 Recommended: Use Filecoin Direct instead")
                st.stop()

        st.divider()

    # Main content
    st.header("🚀 Upload NFT")
    st.header("🎨 Upload Your NFT")

    # File uploader
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=["png", "jpg", "jpeg", "gif", "webp"],
        help="Maximum file size: 100MB",
    )

    if uploaded_file is not None:
        # Validate file
        if not validate_image_file(uploaded_file):
            st.stop()

        # Show image preview
        col1, col2 = st.columns([1, 2])

        with col1:
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption="Image Preview", width="stretch")

                # Show file info
                st.info(
                    f"**File:** {uploaded_file.name}\n"
                    f"**Size:** {uploaded_file.size:,} bytes\n"
                    f"**Type:** {uploaded_file.type}"
                )
            except Exception as e:
                st.error(f"Error loading image: {e}")
                st.stop()

        with col2:
            st.subheader("📝 NFT Metadata")

            with st.form("nft_metadata_form"):
                # Basic NFT information
                name = st.text_input(
                    "Name *",
                    placeholder="My Awesome NFT",
                    help="Name of your NFT",
                )

                description = st.text_area(
                    "Description *",
                    placeholder="Describe your NFT...",
                    help="Detailed description of your NFT",
                    height=100,
                )

                # Custom attributes
                st.markdown("**Custom Attributes**")

                col_attr1, col_attr2 = st.columns(2)

                with col_attr1:
                    activity = st.text_input(
                        "Activity",
                        placeholder="Swimming",
                        help="Type of activity",
                    )

                    user = st.text_input(
                        "User",
                        placeholder="John Doe",
                        help="User or creator name",
                    )

                with col_attr2:
                    companion = st.text_input(
                        "Companion",
                        placeholder="Team Alpha",
                        help="Companion or team",
                    )

                    time_value = st.number_input(
                        "Time",
                        min_value=0,
                        max_value=10000,
                        value=5,
                        help="Time value",
                    )

                    # Submit button
                    submitted = st.form_submit_button(
                        "🚀 Upload to Filecoin", width="stretch"
                    )

                    if submitted:
                        # Validate required fields
                        if not name or not description:
                            st.error("❌ Name and Description are required fields")
                        else:
                            # Process upload
                            with st.spinner("Uploading to Filecoin..."):
                                try:
                                    process_upload(
                                        uploaded_file,
                                        name,
                                        description,
                                        activity,
                                        user,
                                        companion,
                                        time_value,
                                    )
                                except Exception as e:
                                    st.error(f"❌ Upload failed: {str(e)}")


def process_upload(
    uploaded_file,
    name: str,
    description: str,
    activity: str,
    user: str,
    companion: str,
    time: int,
):
    """Process the complete upload workflow"""

    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        # Step 1: Upload image
        status_text.text("📤 Uploading image to Filecoin...")
        progress_bar.progress(25)

        # Get file bytes - ensure we get the actual bytes
        uploaded_file.seek(0)  # Reset file pointer to beginning
        file_bytes = uploaded_file.getvalue()  # Use getvalue() for UploadedFile

        # Validate file size
        if len(file_bytes) == 0:
            st.error("❌ File is empty (0 bytes). Please select a valid image.")
            return

        # Upload image to selected provider
        if st.session_state.storage_provider == "pinata":
            image_cid = st.session_state.pinata_client.upload_file(
                file_bytes=file_bytes,
                filename=uploaded_file.name,
                metadata={"name": f"{name}_image"},
            )
            client = st.session_state.pinata_client
        elif st.session_state.storage_provider == "filecoin_direct":
            image_cid = st.session_state.filecoin_direct_client.upload_file(
                file_bytes=file_bytes,
                filename=uploaded_file.name,
                metadata={"name": f"{name}_image"},
            )
            client = st.session_state.filecoin_direct_client
        else:  # filecoin (legacy)
            image_cid = st.session_state.filecoin_client.upload_file(
                file_bytes=file_bytes,
                filename=uploaded_file.name,
                metadata={"name": f"{name}_image"},
            )
            client = st.session_state.filecoin_client

        image_uri = client.get_ipfs_uri(image_cid)
        image_gateway = client.get_gateway_url(image_cid)

        progress_bar.progress(50)
        status_text.text("🔨 Generating metadata...")

        # Step 2: Create metadata
        metadata = build_nft_metadata(
            name=name,
            description=description,
            image_uri=image_uri,
            actividad=activity,
            usuario=user,
            acompanante=companion,
            tiempo=time,
        )

        progress_bar.progress(75)
        status_text.text("📝 Uploading metadata to Filecoin...")

        # Step 3: Upload metadata
        metadata_cid = client.upload_json(json_data=metadata, name=f"{name}_metadata")

        metadata_uri = client.get_ipfs_uri(metadata_cid)
        metadata_gateway = client.get_gateway_url(metadata_cid)

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

        # Save metadata file locally
        metadata_filename = (
            f"{name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        metadata_filepath = os.path.join(
            "uploads", "metadata_history", metadata_filename
        )
        save_metadata_to_file(metadata, metadata_filepath)

        # Display success message with custom styling
        st.markdown(
            """
        <div class="success-box">
            <h3 style="color: var(--filecoin-success); margin: 0 0 1rem 0;">
                🎉 Upload completed successfully!
            </h3>
            <p style="color: var(--filecoin-dark); margin: 0;">
                Your NFT has been successfully uploaded to the Filecoin network with verifiable storage deals.
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Display results
        st.markdown("### 📋 Upload Results")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                """
            <div class="info-box">
                <h4 style="color: var(--filecoin-primary); margin: 0 0 1rem 0;">🖼️ Image</h4>
                <p style="color: var(--filecoin-success); font-weight: 600; margin-bottom: 1rem;">
                    ✅ Image uploaded to Filecoin
                </p>
            """,
                unsafe_allow_html=True,
            )
            st.code(f"CID: {image_cid}")
            st.code(f"URI: {image_uri}")
            if image_gateway:
                st.markdown(f"[🌐 View Image]({image_gateway})")
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown(
                """
            <div class="info-box">
                <h4 style="color: var(--filecoin-primary); margin: 0 0 1rem 0;">📝 NFT Metadata</h4>
                <p style="color: var(--filecoin-success); font-weight: 600; margin-bottom: 1rem;">
                    ✅ Metadata uploaded to Filecoin
                </p>
            """,
                unsafe_allow_html=True,
            )
            st.code(f"CID: {metadata_cid}")
            st.code(f"🎯 Token URI: {metadata_uri}")
            if metadata_gateway:
                st.markdown(f"[🌐 View Metadata]({metadata_gateway})")
            st.markdown("</div>", unsafe_allow_html=True)

        # Display final Token URI prominently
        st.markdown("---")
        st.markdown("### 🎯 Final Token URI for Smart Contract")

        st.markdown(
            """
        <div class="success-box" style="text-align: center;">
            <h4 style="color: var(--filecoin-primary); margin: 0 0 1rem 0;">
                Ready for Smart Contract Integration
            </h4>
        """,
            unsafe_allow_html=True,
        )

        st.code(metadata_uri, language=None)

        st.markdown(
            """
            <p style="color: var(--filecoin-dark); margin: 1rem 0 0 0;">
                💡 Use this Token URI in your ERC-721 smart contract's tokenURI() function
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Show metadata preview
        st.subheader("📄 Generated Metadata Preview")
        st.json(metadata)

        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()

    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"❌ Upload failed: {str(e)}")

        # Log failed upload
        # Error occurred during upload
        pass

        raise e


if __name__ == "__main__":
    main()
