"""Tools for Customer Info and Finances agents."""

from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import json
import os
import logging
import uuid
from google.cloud import storage
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

# --- Google Cloud Storage (GCS) Configuration ---
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID", "ferrous-plating-477602-p2")
BUCKET_NAME = "aiatl2025"

try:
    # Try to initialize GCS client with explicit project
    if PROJECT_ID:
        storage_client = storage.Client(project=PROJECT_ID)
    else:
        # Fallback: try without explicit project (uses default credentials)
        storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    # Don't test bucket access here - let it fail gracefully when actually used
    logger.info(f"GCS client initialized successfully with project: {PROJECT_ID}, bucket: {BUCKET_NAME}")
except Exception as e:
    logger.warning(f"Failed to initialize GCS client or bucket. Is 'google-cloud-storage' installed? {e}")
    logger.warning("Continuing without GCS - data will not be persisted to cloud storage")
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

def _find_existing_customer(
    name: Optional[str] = None,
    email: Optional[str] = None,
) -> Optional[Tuple[Dict[str, Any], str]]:
    """Find existing customer in GCS by email (primary) or name.
    
    Returns:
        tuple of (customer_data, blob_name) if found, None otherwise
    """
    if not bucket:
        return None
    
    try:
        blobs = storage_client.list_blobs(BUCKET_NAME, prefix="customer_info/")
        for blob in blobs:
            try:
                customer_data = json.loads(blob.download_as_string())
                
                # Match by email (primary) - case-insensitive
                if email and customer_data.get("email"):
                    if email.lower().strip() == customer_data.get("email", "").lower().strip():
                        return (customer_data, blob.name)
                
                # Match by name if no email match and name is provided - case-insensitive
                if name and customer_data.get("name"):
                    if name.lower().strip() == customer_data.get("name", "").lower().strip():
                        # Only use name match if email wasn't provided or doesn't exist in existing
                        if not email or not customer_data.get("email"):
                            return (customer_data, blob.name)
            except Exception as e:
                logger.warning(f"Error reading customer blob {blob.name}: {e}")
                continue
    except Exception as e:
        logger.error(f"Error searching for existing customer: {e}")
    
    return None

def _merge_customer_data(
    existing: Dict[str, Any],
    new: Dict[str, Any],
) -> Dict[str, Any]:
    """Merge new customer data into existing customer data.
    
    Merging strategy:
    - Update fields that are None in existing but provided in new
    - Merge lists (prevOrders, interests) - append new items, avoid duplicates
    - Sum rewardPoints if both exist
    - Keep earliest timestamp
    """
    merged = existing.copy()
    
    # Update None fields with new values
    for key, new_value in new.items():
        if key == "timestamp":
            # Keep earliest timestamp
            if existing.get("timestamp") and new_value:
                existing_time = datetime.fromisoformat(existing["timestamp"])
                new_time = datetime.fromisoformat(new_value)
                merged["timestamp"] = existing_time.isoformat() if existing_time < new_time else new_time
            elif new_value:
                merged["timestamp"] = new_value
        elif key == "rewardPoints":
            # Sum rewardPoints if both exist
            existing_points = existing.get("rewardPoints") or 0
            new_points = new_value or 0
            merged["rewardPoints"] = existing_points + new_points
        elif key == "prevOrders":
            # Merge prevOrders lists, avoid duplicates by order_id or order_number
            existing_orders = existing.get("prevOrders") or []
            new_orders = new_value or []
            merged_orders = existing_orders.copy()
            
            # Track existing order identifiers to avoid duplicates
            existing_ids = set()
            for order in existing_orders:
                if order.get("order_id"):
                    existing_ids.add(order.get("order_id"))
                if order.get("order_number"):
                    existing_ids.add(order.get("order_number"))
            
            # Add new orders that aren't duplicates
            for order in new_orders:
                order_id = order.get("order_id") or order.get("order_number")
                if order_id and order_id not in existing_ids:
                    merged_orders.append(order)
                    if order.get("order_id"):
                        existing_ids.add(order.get("order_id"))
                    if order.get("order_number"):
                        existing_ids.add(order.get("order_number"))
                elif not order_id:
                    # If no identifier, add it anyway (might be duplicate but can't tell)
                    merged_orders.append(order)
            
            merged["prevOrders"] = merged_orders if merged_orders else None
        elif key == "interests":
            # Merge interests lists, avoid duplicates
            existing_interests = set((existing.get("interests") or []))
            new_interests = set((new_value or []))
            merged_interests = list(existing_interests.union(new_interests))
            merged["interests"] = merged_interests if merged_interests else None
        elif key == "category":
            # Normalize category when merging
            if new_value is not None:
                normalized = _normalize_category(new_value)
                merged[key] = normalized
            elif merged.get(key) is not None:
                # Normalize existing category if it's invalid
                merged[key] = _normalize_category(merged.get(key))
        elif merged.get(key) is None and new_value is not None:
            # Update None fields with new values
            merged[key] = new_value
        elif new_value is not None and merged.get(key) != new_value:
            # If both have values and they differ, prefer new value (but log it)
            logger.info(f"Field {key} differs: existing={merged.get(key)}, new={new_value}. Using new value.")
            merged[key] = new_value
    
    return merged

# Valid customer categories
VALID_CUSTOMER_CATEGORIES = ["Prospective", "Current", "Inactive"]

def _normalize_category(category: Optional[str]) -> Optional[str]:
    """Normalize category to valid values: Prospective, Current, Inactive, or None.
    
    Args:
        category: Category string (case-insensitive) or None
        
    Returns:
        Normalized category string or None
    """
    if not category:
        return None
    
    category_lower = category.strip().lower()
    
    # Map common variations to valid categories
    category_map = {
        "prospective": "Prospective",
        "current": "Current",
        "active": "Current",  # Map "active" to "Current"
        "inactive": "Inactive",
    }
    
    normalized = category_map.get(category_lower)
    if normalized:
        return normalized
    
    # If it's already a valid category (case-insensitive match), return capitalized version
    for valid_cat in VALID_CUSTOMER_CATEGORIES:
        if category_lower == valid_cat.lower():
            return valid_cat
    
    # If not a valid category, log warning and return None
    logger.warning(f"Invalid category '{category}' provided. Valid categories are: {VALID_CUSTOMER_CATEGORIES}. Setting to None.")
    return None

def enter_customer_info(
    name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    rewardPoints: Optional[int] = None,
    prevOrders: Optional[list[dict]] = None,
    birthday: Optional[str] = None,
    interests: Optional[list[str]] = None,
    address: Optional[str] = None,
    company: Optional[str] = None,
    category: Optional[str] = None,
    notes: Optional[str] = None,
    paymentMethod: Optional[str] = None,
    paymentLast4: Optional[str] = None,
) -> Dict[str, Any]:
    """Enters customer information into the system.
    
    This tool extracts and stores customer data from prompts or uploaded files.
    All fields are optional - extract whatever information is available.
    Missing fields will be stored as None/null to indicate they were not provided.
    
    Category must be one of: "Prospective", "Current", "Inactive", or None.
    Invalid category values will be normalized or set to None.
    
    If a customer with the same email or name already exists, the data will be merged
    instead of creating a duplicate entry.
    
    Returns:
        dict: Status and confirmation message with entered data
    """
    # Normalize category to valid values
    normalized_category = _normalize_category(category)
    
    # Store all fields explicitly, including None for missing data
    customer_data = {
        "name": name,
        "email": email,
        "phone": phone,
        "rewardPoints": rewardPoints,
        "prevOrders": prevOrders,
        "birthday": birthday,
        "interests": interests,
        "address": address,
        "company": company,
        "category": normalized_category,  # Normalized category
        "notes": notes,
        "paymentMethod": paymentMethod,
        "paymentLast4": paymentLast4,
    }
    
    # Check if at least one field has a value
    has_data = any(value is not None and value != "" for value in customer_data.values())
    
    if not has_data:
        return {
            "status": "error",
            "error_message": "No customer data was received. Please provide at least one piece of information (such as name, email, phone, address, company, category, or notes) to enter a customer record."
        }
    
    # Check for existing customer (duplicate detection)
    existing_customer = _find_existing_customer(name=name, email=email)
    is_update = existing_customer is not None
    
    if is_update:
        existing_data, blob_name = existing_customer
        logger.info(f"Found existing customer: {existing_data.get('name')} ({existing_data.get('email')}). Merging data.")
        
        # Merge customer data
        customer_data = _merge_customer_data(existing_data, customer_data)
        
        # Delete old blob
        try:
            old_blob = bucket.blob(blob_name)
            old_blob.delete()
            logger.info(f"Deleted old customer entry: {blob_name}")
        except Exception as e:
            logger.warning(f"Failed to delete old customer entry {blob_name}: {e}")
    
    # Add timestamp if not present (for new entries) or keep merged timestamp
    if "timestamp" not in customer_data:
        customer_data["timestamp"] = datetime.now().isoformat()
    
    # Store in GCS for persistence
    entry_id = str(uuid.uuid4())
    gcs_path = _upload_json_to_gcs(customer_data, "customer_info", entry_id)
    
    if not gcs_path:
        return {
            "status": "error",
            "error_message": "Data was captured but failed to save to cloud storage. Check server logs.",
            "data": customer_data
        }
    
    # Create a summary of what was entered vs what's missing
    entered_fields = {k: v for k, v in customer_data.items() if v is not None and v != "" and k != "timestamp"}
    missing_fields = {k: None for k, v in customer_data.items() if v is None or v == "" and k != "timestamp"}
    
    action = "updated" if is_update else "entered"
    logger.info(f"{action.capitalize()} customer info: {entered_fields}")
    
    return {
        "status": "success",
        "message": f"Successfully {action} customer information. Entered: {entered_fields}. Missing fields set to null: {list(missing_fields.keys())}",
        "data": customer_data,
        "gcs_path": gcs_path,
        "entered_fields": entered_fields,
        "missing_fields": list(missing_fields.keys()),
        "is_update": is_update
    }

def enter_financial_data(
    name: Optional[str] = None,  # customer name to link financial data to customer
    category: Optional[str] = None,
    # Transaction Records fields
    transactions: Optional[list[dict]] = None,  # cashflow in/out records
    # Expenses fields
    expenses: Optional[list[dict]] = None,  # taxes, bills, utilities, etc.
    # Banking fields
    bankStatements: Optional[list[dict]] = None,  # bank statements, credit card statements, etc.
    # Finance Reports fields
    financeReports: Optional[list[dict]] = None,  # profit and loss statements, balance sheets, etc.
    # Tax Documents fields
    taxDocuments: Optional[list[dict]] = None,  # tax returns, tax forms, etc.
) -> Dict[str, Any]:
    """Enters financial data into the system.
    
    This tool extracts and stores financial information from prompts or uploaded files.
    All fields are optional - extract whatever information is available.
    Missing fields will be stored as None/null to indicate they were not provided.
    
    Categories (frontend maps to these backend fields):
    1. "Transaction Records" → transactions field (cashflow in/out)
    2. "Expenses" → expenses field (taxes, bills, utilities, etc.)
    3. "Banking" → bankStatements field (bank statements, credit card statements, etc.)
    4. "Finance Reports" → financeReports field (profit and loss statements, balance sheets, etc.)
    5. "Tax Documents" → taxDocuments field (tax returns, tax forms, etc.)
    
    IMPORTANT - Structure for list items:
    Each item in the category lists should be a dictionary with:
    - "type" field: subcategory for frontend differentiation (e.g., "taxes", "bills", "utilities" for expenses)
    - Common fields inside each dict: amount, currency, date, description, notes
    - Category-specific fields as needed
    
    Example structure:
    {
      "category": "Expenses",
      "expenses": [
        {
          "type": "taxes",  # Frontend can filter/group by this
          "amount": 1000,
          "currency": "USD",
          "date": "2024-01-15",
          "description": "Q4 income tax",
          "notes": "Filed electronically"
        },
        {
          "type": "bills",
          "amount": 200,
          "currency": "USD",
          "date": "2024-01-20",
          "description": "Electric bill"
        }
      ]
    }
    
    For Finance Reports, use types like: "profit_and_loss", "balance_sheet", "cash_flow_statement"
    For Banking, use types like: "bank_statement", "credit_card_statement"
    For Tax Documents, use types like: "tax_return", "tax_form"
    For Transactions, use types like: "income", "expense", "transfer", "payment"
    
    Returns:
        dict: Status and confirmation message with entered data
    """
    # Store all fields explicitly, including None for missing data
    financial_data = {
        "name": name,
        "category": category,
        "transactions": transactions,
        "expenses": expenses,
        "bankStatements": bankStatements,
        "financeReports": financeReports,
        "taxDocuments": taxDocuments,
    }
    
    # Check if at least one category list has data
    category_lists = [transactions, expenses, bankStatements, financeReports, taxDocuments]
    has_data = any(
        value is not None and value != "" and (isinstance(value, list) and len(value) > 0)
        for value in category_lists
    )
    
    if not has_data:
        return {
            "status": "error",
            "error_message": (
                "No financial data was provided. Please enter at least one category with data: "
                "transactions, expenses, bankStatements, financeReports, or taxDocuments. "
                "Each item in the lists should include a 'type' field and common fields (amount, currency, date, description, notes)."
            )
        }
    
    # create a summary of what was entered vs what's missing
    entered_fields = {k: v for k, v in financial_data.items() if v is not None and v != ""}
    missing_fields = {k: None for k, v in financial_data.items() if v is None or v == ""}
    
    # store in GCS for persistence
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
    
    logger.info(f"Stored financial data: {entered_fields}")
    
    return {
        "status": "success",
        "message": f"Successfully entered financial data. Entered: {entered_fields}. Missing fields set to null: {list(missing_fields.keys())}",
        "data": financial_data,
        "gcs_path": gcs_path,
        "entered_fields": entered_fields,
        "missing_fields": list(missing_fields.keys())
    }

def _extract_with_gemini(
    file_content: str,
    file_type: Optional[str] = None,
) -> Dict[str, Any]:
    """Uses Gemini to extract structured data from file content.
    
    This leverages Gemini's advanced understanding to extract structured data
    in the exact format needed by the agents.
    
    Args:
        file_content: The text content of the uploaded file
        file_type: Type of file (e.g., 'pdf', 'txt', 'csv', 'json', 'image')
    
    Returns:
        dict: Structured extracted data with confidence scores
    """
    try:
        # gemini model for extraction
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
        
        # extraction prompt with structured output format
        extraction_prompt = f"""Analyze the following file content and extract all relevant structured data.

File Type: {file_type or 'unknown'}

File Content:
{file_content[:50000]}  # Limit to 50k chars to avoid token limits

Extract and return a JSON object with the following structure. Be thorough and accurate:

{{
  "data_type": "customer_info" | "financial_data" | "mixed" | "unknown",
  "confidence": 0.0-1.0,
  "customer_info": {{
    "name": string or null,
    "email": string or null,
    "phone": string or null,
    "address": string or null,
    "rewardPoints": integer or null,
    "prevOrders": [{{"order_id": string, "order_number": string, "date": string, "amount": number}}] or null,
    "birthday": string (YYYY-MM-DD) or null,
    "interests": [string] or null,
    "company": string or null,
    "category": "Prospective" | "Current" | "Inactive" | null,  # Must be one of these exact values
    "notes": string or null,
    "paymentMethod": string or null,
    "paymentLast4": string or null
  }},
  "financial_data": {{
    "name": string or null,  # customer name to link financial data to customer
    "category": "Transaction Records" | "Expenses" | "Banking" | "Finance Reports" | "Tax Documents" | null,
    "transactions": [
      {{
        "type": "income" | "expense" | "transfer" | "payment",
        "amount": number,
        "currency": string (e.g., "USD"),
        "date": string (YYYY-MM-DD),
        "description": string,
        "notes": string or null
      }}
    ] or null,
    "expenses": [
      {{
        "type": "taxes" | "bills" | "utilities" | "rent" | "supplies" | etc,
        "amount": number,
        "currency": string,
        "date": string (YYYY-MM-DD),
        "description": string,
        "notes": string or null
      }}
    ] or null,
    "bankStatements": [
      {{
        "type": "bank_statement" | "credit_card_statement",
        "amount": number,
        "currency": string,
        "date": string (YYYY-MM-DD),
        "description": string,
        "notes": string or null
      }}
    ] or null,
    "financeReports": [
      {{
        "type": "profit_and_loss" | "balance_sheet" | "cash_flow_statement",
        "amount": number or null,
        "currency": string or null,
        "date": string (YYYY-MM-DD) or null,
        "description": string,
        "notes": string or null
      }}
    ] or null,
    "taxDocuments": [
      {{
        "type": "tax_return" | "tax_form",
        "amount": number or null,
        "currency": string or null,
        "date": string (YYYY-MM-DD) or null,
        "description": string,
        "notes": string or null
      }}
    ] or null
  }},
  "extraction_notes": "string describing what was found and any ambiguities",
  "missing_fields": ["list of fields that were expected but not found"]
}}

CRITICAL INSTRUCTIONS:
1. Extract ALL available data - be thorough
2. Use null for missing fields, not empty strings or empty arrays
3. For dates, normalize to YYYY-MM-DD format
4. For amounts, extract numeric values only (remove currency symbols)
5. For financial data, determine the correct category and type
6. Extract customer name from financial data when available (e.g., from invoices, receipts, purchase records)
7. Group related items into appropriate lists
8. Set confidence based on how clear and complete the data is
9. If data is ambiguous or unclear, note it in extraction_notes
10. Return ONLY valid JSON, no markdown formatting

Return the JSON object now:"""

        # Use Gemini API for extraction
        # Note: This uses the direct Gemini API, not ADK
        # If you want to use ADK agents, you could create a dedicated extraction agent
        api_key = os.getenv("GEMINI_API_KEY")
        
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name)
            
            # Generate extraction
            response = model.generate_content(
                extraction_prompt,
                generation_config={
                    "temperature": 0.1,  # Low temperature for accuracy
                    "top_p": 0.95,
                    "top_k": 40,
                }
            )
            
            # Parse JSON from response
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            try:
                extracted_data = json.loads(response_text)
                logger.info(f"Successfully extracted data with Gemini (confidence: {extracted_data.get('confidence', 0)})")
                return extracted_data
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse Gemini JSON response: {e}")
                logger.debug(f"Response text: {response_text[:500]}")
                # Fall back to basic extraction
                return _basic_extraction(file_content, file_type)
        else:
            logger.warning("GEMINI_API_KEY not set, falling back to basic extraction")
            return _basic_extraction(file_content, file_type)
            
    except Exception as e:
        logger.error(f"Error in Gemini extraction: {e}")
        # Fall back to basic extraction
        return _basic_extraction(file_content, file_type)


def _basic_extraction(
    file_content: str,
    file_type: Optional[str] = None,
) -> Dict[str, Any]:
    """Basic keyword-based extraction as fallback.
    
    Args:
        file_content: The text content of the uploaded file
        file_type: Type of file
    
    Returns:
        dict: Basic extracted data
    """
    content_lower = file_content.lower()
    customer_keywords = ["name", "email", "phone", "address", "customer", "client", "contact", "birthday", "reward"]
    finance_keywords = ["amount", "payment", "invoice", "transaction", "balance", "account", "financial", "revenue", "expense", "tax"]
    
    customer_score = sum(1 for keyword in customer_keywords if keyword in content_lower)
    finance_score = sum(1 for keyword in finance_keywords if keyword in content_lower)
    
    # Determine data type
    if customer_score > finance_score:
        data_type = "customer_info"
        confidence = min(0.7, 0.3 + (customer_score * 0.1))
    elif finance_score > customer_score:
        data_type = "financial_data"
        confidence = min(0.7, 0.3 + (finance_score * 0.1))
    elif customer_score > 0 and finance_score > 0:
        data_type = "mixed"
        confidence = 0.5
    else:
        data_type = "unknown"
        confidence = 0.2
    
    return {
        "data_type": data_type,
        "confidence": confidence,
        "customer_info": None,
        "financial_data": None,
        "extraction_notes": f"Basic keyword extraction used. Customer keywords: {customer_score}, Finance keywords: {finance_score}",
        "missing_fields": []
    }


def extract_data_from_file(
    file_content: str,
    file_type: Optional[str] = None,
) -> Dict[str, Any]:
    """Extracts structured data from uploaded file content using Gemini.
    
    This tool uses Gemini's advanced understanding to extract structured data
    in the exact format needed by Customer Info and Finances agents.
    Falls back to basic keyword extraction if Gemini is unavailable.
    
    Args:
        file_content: The text content of the uploaded file
        file_type: Type of file (e.g., 'pdf', 'txt', 'csv', 'json', 'image')
    
    Returns:
        dict: Extracted structured data with:
            - data_type: "customer_info" | "financial_data" | "mixed" | "unknown"
            - confidence: 0.0-1.0 score
            - customer_info: structured customer data or null
            - financial_data: structured financial data or null
            - extraction_notes: notes about the extraction
            - missing_fields: list of expected but missing fields
    """
    # Use Gemini for advanced extraction
    extracted = _extract_with_gemini(file_content, file_type)
    
    # Store file info in GCS
    file_entry = {
        "content_preview": file_content[:500] if len(file_content) > 500 else file_content,
        "file_type": file_type or "unknown",
        "timestamp": datetime.now().isoformat(),
        "extraction_confidence": extracted.get("confidence", 0),
        "data_type": extracted.get("data_type", "unknown")
    }
    entry_id = str(uuid.uuid4())
    _upload_json_to_gcs(file_entry, "uploaded_files", entry_id)
    logger.info(f"Stored uploaded file: {file_type} (confidence: {extracted.get('confidence', 0)})")
    
    # Format response for agents
    data_type = extracted.get("data_type", "unknown")
    confidence = extracted.get("confidence", 0)
    
    # Determine suggested agent
    if data_type == "customer_info":
        suggested_agent = "customer_info"
    elif data_type == "financial_data":
        suggested_agent = "finances"
    elif data_type == "mixed":
        suggested_agent = "both"
    else:
        suggested_agent = "unknown"
    
    return {
        "status": "success",
        "message": f"File content analyzed using {'Gemini' if extracted.get('confidence', 0) > 0.5 else 'basic extraction'}. Data type: {data_type}, Confidence: {confidence:.2f}",
        "suggested_agent": suggested_agent,
        "data_type": data_type,
        "confidence": confidence,
        "extracted_data": extracted,
        "customer_info": extracted.get("customer_info"),
        "financial_data": extracted.get("financial_data"),
        "extraction_notes": extracted.get("extraction_notes", ""),
        "missing_fields": extracted.get("missing_fields", []),
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

def update_all_customers_category(category: str) -> Dict[str, Any]:
    """Update all customers to have the specified category.
    
    Args:
        category: Category to set for all customers ("Prospective", "Current", or "Inactive")
        
    Returns:
        dict: Status and count of updated customers
    """
    if not bucket:
        logger.error("GCS bucket not initialized.")
        return {"status": "error", "message": "GCS not initialized."}
    
    normalized_category = _normalize_category(category)
    if not normalized_category:
        return {
            "status": "error",
            "message": f"Invalid category '{category}'. Must be one of: {VALID_CUSTOMER_CATEGORIES}"
        }
    
    try:
        updated_count = 0
        blobs = storage_client.list_blobs(BUCKET_NAME, prefix="customer_info/")
        
        for blob in blobs:
            try:
                customer_data = json.loads(blob.download_as_string())
                
                # Update category
                customer_data["category"] = normalized_category
                
                # Re-upload with updated category
                blob.upload_from_string(
                    json.dumps(customer_data, indent=2),
                    content_type="application/json"
                )
                updated_count += 1
            except Exception as e:
                logger.warning(f"Error updating customer blob {blob.name}: {e}")
                continue
        
        message = f"Updated {updated_count} customer(s) to category '{normalized_category}'."
        logger.info(message)
        return {
            "status": "success",
            "message": message,
            "updated_count": updated_count,
            "category": normalized_category
        }
    except Exception as e:
        message = f"Error updating customer categories: {e}"
        logger.error(message)
        return {"status": "error", "message": message}

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
