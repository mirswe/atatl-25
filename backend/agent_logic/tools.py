"""Tools for Customer Info and Finances agents."""

from typing import Dict, Any, Optional
from datetime import datetime
import json
import os
import logging
import uuid
from google.cloud import storage

# Set up logging
logger = logging.getLogger(__name__)

# --- Google Cloud Storage (GCS) Configuration ---
try:
    storage_client = storage.Client()
    BUCKET_NAME = "aiatl2025" 
    bucket = storage_client.bucket(BUCKET_NAME)
except Exception as e:
    logger.error(f"Failed to initialize GCS client or bucket. Is 'google-cloud-storage' installed? {e}")
    storage_client = None
    bucket = None

def _upload_json_to_gcs(data_dict: Dict, folder: str, file_id: str) -> Optional[str]:
    """Helper function to upload a dictionary as a JSON file to GCS.

    Features:
    - Retries uploads with exponential backoff for transient errors
    - Falls back to local file storage under `./storage_fallback/` when GCS
      is unavailable or all retries fail

    Returns a GCS path (gs://...) on success or a local file path (file://...)
    on fallback. Returns None only for unexpected failures.
    """
    # Prepare file path and JSON payload
    file_name = f"{folder}/{file_id}.json"
    payload = json.dumps(data_dict, indent=2)

    # If bucket is not initialized, write to local fallback immediately
    if not bucket:
        logger.warning("GCS bucket not initialized. Writing to local fallback.")
        try:
            fallback_dir = os.path.join(os.getcwd(), "storage_fallback", folder)
            os.makedirs(fallback_dir, exist_ok=True)
            local_path = os.path.join(fallback_dir, f"{file_id}.json")
            with open(local_path, "w", encoding="utf-8") as f:
                f.write(payload)
            local_uri = f"file://{local_path}"
            logger.info(f"Wrote fallback file to {local_uri}")
            return local_uri
        except Exception as e:
            logger.error(f"Failed to write fallback file to disk: {e}")
            return None

    # Try upload with retries
    max_retries = 3
    backoff_base = 0.5  # seconds
    attempt = 0
    while attempt < max_retries:
        try:
            blob = bucket.blob(file_name)
            blob.upload_from_string(payload, content_type="application/json")
            gcs_path = f"gs://{BUCKET_NAME}/{file_name}"
            logger.info(f"Successfully saved data to {gcs_path}")
            return gcs_path
        except Exception as e:
            attempt += 1
            logger.warning(f"Attempt {attempt} failed to upload to GCS: {e}")
            # exponential backoff
            try:
                sleep_time = backoff_base * (2 ** (attempt - 1))
                import time
                time.sleep(sleep_time)
            except Exception:
                pass

    # If we reach here, all retries failed — write to local fallback and log
    logger.error(f"All {max_retries} attempts to upload to GCS failed. Writing to local fallback.")
    try:
        fallback_dir = os.path.join(os.getcwd(), "storage_fallback", folder)
        os.makedirs(fallback_dir, exist_ok=True)
        local_path = os.path.join(fallback_dir, f"{file_id}.json")
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(payload)
        local_uri = f"file://{local_path}"
        logger.info(f"Wrote fallback file to {local_uri}")
        return local_uri
    except Exception as e:
        logger.error(f"Failed to write fallback file to disk after GCS retries: {e}")
        return None

def enter_customer_info(
    name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    address: Optional[str] = None,
    company: Optional[str] = None,
    category: Optional[str] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """Enters customer information into the system.
    
    This tool extracts and stores customer data from prompts or uploaded files.
    All fields are optional - extract whatever information is available.
    Missing fields will be stored as None/null to indicate they were not provided.
    
    Args:
        name: Customer's full name
        email: Customer's email address
        phone: Customer's phone number
        address: Customer's physical address
        company: Customer's company name
        category: Customer category/classification (can be None if not provided)
        notes: Additional notes or comments about the customer
    
    Returns:
        dict: Status and confirmation message with entered data
    """
    # Store all fields explicitly, including None for missing data
    customer_data = {
        "name": name,
        "email": email,
        "phone": phone,
        "address": address,
        "company": company,
        "category": category,  # Can be None if not provided
        "notes": notes,
    }
    
    # Check if at least one field has a value
    has_data = any(value is not None and value != "" for value in customer_data.values())
    
    if not has_data:
        return {
            "status": "error",
            "error_message": "No customer information provided. Please extract at least one field (name, email, phone, address, company, category, or notes)."
        }
    
    # Create a summary of what was entered vs what's missing
    entered_fields = {k: v for k, v in customer_data.items() if v is not None and v != ""}
    missing_fields = {k: None for k, v in customer_data.items() if v is None or v == ""}
    
    # Store in file-based storage for persistence
    entry_with_timestamp = {
        **customer_data,
        "timestamp": datetime.now().isoformat()
    }
    
    entry_id = str(uuid.uuid4())
    gcs_path = _upload_json_to_gcs(entry_with_timestamp, "customer_info", entry_id)
    
    if not gcs_path:
        return {
            "status": "error",
            "error_message": "Data was captured but failed to save to cloud storage. Check server logs.",
            "data": customer_data
        }
    
    return {
        "status": "success",
        "message": f"Successfully entered customer information. Entered: {entered_fields}. Missing fields set to null: {list(missing_fields.keys())}",
        "data": customer_data,
        "gcs_path": gcs_path,
        "entered_fields": entered_fields,
        "missing_fields": list(missing_fields.keys())
    }

def enter_financial_data(
    amount: Optional[float] = None,
    currency: Optional[str] = None,
    transaction_type: Optional[str] = None,
    date: Optional[str] = None,
    description: Optional[str] = None,
    category: Optional[str] = None,
    inventory_item: Optional[str] = None,
    account_number: Optional[str] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """Enters financial data into the system.
    
    This tool extracts and stores financial information from prompts or uploaded files.
    All fields are optional - extract whatever information is available.
    Missing fields will be stored as None/null to indicate they were not provided.
    
    Args:
        amount: Transaction or financial amount
        currency: Currency code (e.g., USD, EUR, GBP)
        transaction_type: Type of transaction (e.g., income, expense, transfer, payment)
        date: Date of the transaction (format: YYYY-MM-DD or any readable format)
        description: Description of the financial transaction
        category: Category of the transaction (e.g., utilities, salary, rent, supplies)
        inventory_item: Associated inventory item or product
        account_number: Associated account number or reference
        notes: Additional notes or comments
    
    Returns:
        dict: Status and confirmation message with entered data
    """
    # Store all fields explicitly, including None for missing data
    financial_data = {
        "amount": amount,
        "currency": currency,
        "transaction_type": transaction_type,
        "date": date,
        "description": description,
        "category": category,
        "inventory_item": inventory_item,
        "account_number": account_number,
        "notes": notes,
    }
    
    # Check if at least one field has a value
    has_data = any(value is not None and value != "" for value in financial_data.values())
    
    if not has_data:
        return {
            "status": "error",
            "error_message": "No financial data provided. Please extract at least one field (amount, currency, transaction_type, date, description, category, inventory_item, account_number, or notes)."
        }
    
    # Create a summary of what was entered vs what's missing
    entered_fields = {k: v for k, v in financial_data.items() if v is not None and v != ""}
    missing_fields = {k: None for k, v in financial_data.items() if v is None or v == ""}
    
    # Store in file-based storage for persistence
    entry_with_timestamp = {
        **financial_data,
        "timestamp": datetime.now().isoformat()
    }
    entry_id = str(uuid.uuid4())
    gcs_path = _upload_json_to_gcs(entry_with_timestamp, "financial_data", entry_id)

    if not gcs_path:
        return {
            "status": "error",
            "error_message": "Data was captured but failed to save to cloud storage. Check server logs.",
            "data": financial_data
        }
    
    return {
        "status": "success",
        "message": f"Successfully entered financial data. Entered: {entered_fields}. Missing fields set to null: {list(missing_fields.keys())}",
        "data": financial_data,
        "gcs_path": gcs_path,
        "entered_fields": entered_fields,
        "missing_fields": list(missing_fields.keys())
    }

def extract_data_from_file(
    file_content: str,
    file_type: Optional[str] = None,
) -> Dict[str, Any]:
    """Extracts structured data from uploaded file content.
    
    This tool analyzes file content and extracts relevant information.
    It can be used by both Customer Info and Finances agents.
    
    Args:
        file_content: The text content of the uploaded file
        file_type: Type of file (e.g., 'pdf', 'txt', 'csv', 'json')
    
    Returns:
        dict: Extracted data and suggestions for which agent should process it
    """
    # Simple analysis to suggest agent type
    content_lower = file_content.lower()
    customer_keywords = ["name", "email", "phone", "address", "customer", "client", "contact"]
    finance_keywords = ["amount", "payment", "invoice", "transaction", "balance", "account", "financial", "revenue"]
    
    customer_score = sum(1 for keyword in customer_keywords if keyword in content_lower)
    finance_score = sum(1 for keyword in finance_keywords if keyword in content_lower)
    
    suggestion = "customer_info" if customer_score > finance_score else "finances"
    
    # Store file info in file-based storage
    file_entry = {
        "content_preview": file_content[:500] if len(file_content) > 500 else file_content,
        "file_type": file_type or "unknown",
        "timestamp": datetime.now().isoformat()
    }
    entry_id = str(uuid.uuid4())
    _upload_json_to_gcs(file_entry, "uploaded_files", entry_id) 

    return {
        "status": "success",
        "message": f"File content analyzed. Suggested agent: {suggestion}",
        "suggested_agent": suggestion,
        "customer_keywords_found": customer_score,
        "finance_keywords_found": finance_score,
        "file_content_preview": file_content[:500] if len(file_content) > 500 else file_content
    }

def get_storage() -> Dict[str, list]:
    """Get all stored data for viewing. Reloads from GCS to ensure latest data."""
    if not bucket:
        logger.error("GCS bucket not initialized.")
        return {"error": "GCS bucket not initialized."}

    storage_data = {
        "customer_info": [],
        "financial_data": [],
        "uploaded_files": []
    }
    
    try:
        # Get customers
        blobs = storage_client.list_blobs(BUCKET_NAME, prefix="customer_info/")
        for blob in blobs:
            storage_data["customer_info"].append(json.loads(blob.download_as_string()))
        
        # Get finance
        blobs = storage_client.list_blobs(BUCKET_NAME, prefix="financial_data/")
        for blob in blobs:
            storage_data["financial_data"].append(json.loads(blob.download_as_string()))

        # Get files
        blobs = storage_client.list_blobs(BUCKET_NAME, prefix="uploaded_files/")
        for blob in blobs:
            storage_data["uploaded_files"].append(json.loads(blob.download_as_string()))
            
    except Exception as e:
        logger.error(f"Error loading data from GCS: {e}")
        return {"error": f"Error loading data from GCS: {e}"}

    return storage_data

def clear_storage() -> Dict[str, str]:
    """Clear all stored data from GCS."""
    if not bucket:
        logger.error("GCS bucket not initialized.")
        return {"status": "error", "message": "GCS not initialized."}

    try:
        folders = ["customer_info/", "financial_data/", "uploaded_files/"]
        deleted_count = 0
        for folder in folders:
            blobs = storage_client.list_blobs(BUCKET_NAME, prefix=folder)
            for blob in blobs:
                blob.delete()
                deleted_count += 1
        
        message = f"Cleared {deleted_count} file(s) from GCS."
        logger.info(message)
        return {"status": "success", "message": message}
    except Exception as e:
        message = f"Error clearing storage from GCS: {e}"
        logger.error(message)
        return {"status": "error", "message": message}