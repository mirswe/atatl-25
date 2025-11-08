"""Tools for Customer Info and Finances agents."""

from typing import Dict, Any, Optional
from datetime import datetime
import json
import os
import logging

# Set up logging
logger = logging.getLogger(__name__)

# File-based storage for persistence across process restarts
STORAGE_FILE = os.path.join(os.path.dirname(__file__), "..", "storage.json")

def _load_storage() -> Dict[str, list]:
    """Load storage from file or return empty storage."""
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading storage file: {e}")
    return {
        "customer_info": [],
        "financial_data": [],
        "uploaded_files": []
    }

def _save_storage(storage: Dict[str, list]):
    """Save storage to file."""
    try:
        os.makedirs(os.path.dirname(STORAGE_FILE), exist_ok=True)
        with open(STORAGE_FILE, 'w') as f:
            json.dump(storage, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving storage file: {e}")

# Initialize storage
_storage = _load_storage()


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
    _storage["customer_info"].append(entry_with_timestamp)
    _save_storage(_storage)
    logger.info(f"Stored customer info: {entered_fields}")
    
    return {
        "status": "success",
        "message": f"Successfully entered customer information. Entered: {entered_fields}. Missing fields set to null: {list(missing_fields.keys())}",
        "data": customer_data,
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
    _storage["financial_data"].append(entry_with_timestamp)
    _save_storage(_storage)
    logger.info(f"Stored financial data: {entered_fields}")
    
    return {
        "status": "success",
        "message": f"Successfully entered financial data. Entered: {entered_fields}. Missing fields set to null: {list(missing_fields.keys())}",
        "data": financial_data,
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
    _storage["uploaded_files"].append(file_entry)
    _save_storage(_storage)
    logger.info(f"Stored uploaded file: {file_type}")
    
    return {
        "status": "success",
        "message": f"File content analyzed. Suggested agent: {suggestion}",
        "suggested_agent": suggestion,
        "customer_keywords_found": customer_score,
        "finance_keywords_found": finance_score,
        "file_content_preview": file_content[:500] if len(file_content) > 500 else file_content
    }


def get_storage() -> Dict[str, list]:
    """Get all stored data for viewing. Reloads from file to ensure latest data."""
    global _storage
    _storage = _load_storage()
    return _storage.copy()


def clear_storage():
    """Clear all stored data."""
    _storage["customer_info"].clear()
    _storage["financial_data"].clear()
    _storage["uploaded_files"].clear()
    _save_storage(_storage)

