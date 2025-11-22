"""
Metadata Builder for OpenSea-compatible NFT metadata
Generates JSON metadata according to OpenSea standards
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union


def build_nft_metadata(
    name: str,
    description: str,
    image_uri: str,
    actividad: str,
    usuario: str,
    acompanante: str,
    tiempo: int,
    external_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build NFT metadata compatible with OpenSea standards

    Args:
        name: Name of the NFT
        description: Description of the NFT
        image_uri: IPFS URI of the image (ipfs://...)
        actividad: Activity attribute value
        usuario: User attribute value
        acompanante: Companion attribute value
        tiempo: Time attribute value (numeric)
        external_url: External URL (defaults to image_uri if None)

    Returns:
        dict: OpenSea-compatible metadata
    """
    # Use image_uri as external_url if not provided
    if external_url is None:
        external_url = image_uri

    metadata = {
        "name": name,
        "description": description,
        "image": image_uri,
        "external_url": external_url,
        "attributes": [
            {"trait_type": "Actividad", "value": actividad},
            {"trait_type": "Usuario", "value": usuario},
            {"trait_type": "Acompanante", "value": acompanante},
            {"trait_type": "tiempo", "value": tiempo},
        ],
    }

    return metadata


def add_attribute(
    metadata: Dict[str, Any],
    trait_type: str,
    value: Union[str, int, float],
    display_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Add an attribute to existing metadata

    Args:
        metadata: Existing metadata dictionary
        trait_type: Type of the trait
        value: Value of the trait
        display_type: Display type (number, boost_percentage, etc.)

    Returns:
        dict: Updated metadata with new attribute
    """
    attribute = {"trait_type": trait_type, "value": value}

    if display_type:
        attribute["display_type"] = display_type

    if "attributes" not in metadata:
        metadata["attributes"] = []

    metadata["attributes"].append(attribute)
    return metadata


def validate_metadata(metadata: Dict[str, Any]) -> List[str]:
    """
    Validate metadata against OpenSea standards

    Args:
        metadata: Metadata dictionary to validate

    Returns:
        list: List of validation errors (empty if valid)
    """
    errors = []

    # Check required fields
    required_fields = ["name", "description", "image"]
    for field in required_fields:
        if field not in metadata:
            errors.append(f"Missing required field: {field}")
        elif not metadata[field]:
            errors.append(f"Empty required field: {field}")

    # Validate image URI format
    if "image" in metadata:
        image_uri = metadata["image"]
        if not (image_uri.startswith("ipfs://") or image_uri.startswith("http")):
            errors.append("Image URI should start with 'ipfs://' or 'http'")

    # Validate attributes structure
    if "attributes" in metadata:
        attributes = metadata["attributes"]
        if not isinstance(attributes, list):
            errors.append("Attributes must be a list")
        else:
            for i, attr in enumerate(attributes):
                if not isinstance(attr, dict):
                    errors.append(f"Attribute {i} must be a dictionary")
                    continue

                if "trait_type" not in attr:
                    errors.append(f"Attribute {i} missing 'trait_type'")
                if "value" not in attr:
                    errors.append(f"Attribute {i} missing 'value'")

    return errors


def save_metadata_to_file(
    metadata: Dict[str, Any], filepath: str, pretty: bool = True
) -> bool:
    """
    Save metadata to JSON file

    Args:
        metadata: Metadata dictionary
        filepath: Path to save the file
        pretty: Whether to format JSON with indentation

    Returns:
        bool: True if successful
    """
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            if pretty:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            else:
                json.dump(metadata, f, ensure_ascii=False)
        return True
    except Exception:
        return False


def load_metadata_from_file(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Load metadata from JSON file

    Args:
        filepath: Path to the JSON file

    Returns:
        dict or None: Loaded metadata or None if failed
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def create_metadata_history_entry(
    metadata: Dict[str, Any],
    image_cid: str,
    metadata_cid: str,
    image_uri: str,
    metadata_uri: str,
    gateway_url: str,
) -> Dict[str, Any]:
    """
    Create a history entry for uploaded metadata

    Args:
        metadata: The uploaded metadata
        image_cid: CID of the image
        metadata_cid: CID of the metadata
        image_uri: IPFS URI of the image
        metadata_uri: IPFS URI of the metadata
        gateway_url: HTTP gateway URL

    Returns:
        dict: History entry
    """
    return {
        "timestamp": datetime.now().isoformat(),
        "name": metadata.get("name", "Unknown"),
        "image_cid": image_cid,
        "metadata_cid": metadata_cid,
        "image_uri": image_uri,
        "metadata_uri": metadata_uri,
        "nft_uri": metadata_uri,  # NFT URI is the metadata URI
        "gateway_url": gateway_url,
        "metadata": metadata,
    }


def get_supported_attribute_types() -> Dict[str, str]:
    """
    Get supported OpenSea attribute types

    Returns:
        dict: Mapping of attribute types to descriptions
    """
    return {
        "text": "Simple text attribute",
        "number": "Numeric attribute that can be filtered",
        "boost_percentage": "Percentage boost (0-100)",
        "boost_number": "Numeric boost",
        "date": "Date value (Unix timestamp)",
    }


def format_metadata_preview(metadata: Dict[str, Any]) -> str:
    """
    Format metadata for preview display

    Args:
        metadata: Metadata dictionary

    Returns:
        str: Formatted JSON string
    """
    return json.dumps(metadata, indent=2, ensure_ascii=False)


def estimate_metadata_size(metadata: Dict[str, Any]) -> int:
    """
    Estimate the size of metadata in bytes

    Args:
        metadata: Metadata dictionary

    Returns:
        int: Estimated size in bytes
    """
    json_string = json.dumps(metadata, ensure_ascii=False)
    return len(json_string.encode("utf-8"))
