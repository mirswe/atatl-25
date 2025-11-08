"""Tools for Customer Info and Finances agents."""

from typing import Dict, Any, Optional
from google.adk.core import ToolContext


def enter_customer_info(
    name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    address: Optional[str] = None,
    company: Optional[str] = None,
    notes: Optional[str] = None,
    context: ToolContext = None,
) -> Dict[str, Any]:
    """Enters customer information into the system.
    
    This tool extracts and stores customer data from prompts or uploaded files.
    All fields are optional - extract whatever information is available.
    
    Args:
        name: Customer's full name
        email: Customer's email address
        phone: Customer's phone number
        address: Customer's physical address
        company: Customer's company name
        notes: Additional notes or comments about the customer
        context: ToolContext for accessing session state (automatically provided)
    
    Returns:
        dict: Status and confirmation message with entered data
    """
    customer_data = {}
    if name:
        customer_data["name"] = name
    if email:
        customer_data["email"] = email
    if phone:
        customer_data["phone"] = phone
    if address:
        customer_data["address"] = address
    if company:
        customer_data["company"] = company
    if notes:
        customer_data["notes"] = notes
    
    # Store in session state if context is available
    if context and hasattr(context, "session_state"):
        if "customer_info" not in context.session_state:
            context.session_state["customer_info"] = []
        context.session_state["customer_info"].append(customer_data)
    
    if not customer_data:
        return {
            "status": "error",
            "error_message": "No customer information provided. Please extract at least one field (name, email, phone, address, company, or notes)."
        }
    
    return {
        "status": "success",
        "message": f"Successfully entered customer information: {customer_data}",
        "data": customer_data
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
    context: ToolContext = None,
) -> Dict[str, Any]:
    """Enters financial data into the system.
    
    This tool extracts and stores financial information from prompts or uploaded files.
    All fields are optional - extract whatever information is available.
    
    Args:
        amount: Transaction or financial amount
        currency: Currency code (e.g., USD, EUR, GBP)
        transaction_type: Type of transaction (e.g., income, expense, transfer, payment)
        date: Date of the transaction (format: YYYY-MM-DD or any readable format)
        description: Description of the financial transaction
        category: Category of the transaction (e.g., utilities, salary, rent, supplies)
        account_number: Associated account number or reference
        notes: Additional notes or comments
        context: ToolContext for accessing session state (automatically provided)
    
    Returns:
        dict: Status and confirmation message with entered data
    """
    financial_data = {}
    if amount is not None:
        financial_data["amount"] = amount
    if inventory_item:
        financial_data["inventory_item"] = inventory_item
    if currency:
        financial_data["currency"] = currency
    if transaction_type:
        financial_data["transaction_type"] = transaction_type
    if date:
        financial_data["date"] = date
    if description:
        financial_data["description"] = description
    if category:
        financial_data["category"] = category
    if account_number:
        financial_data["account_number"] = account_number
    if notes:
        financial_data["notes"] = notes
    
    # Store in session state if context is available
    if context and hasattr(context, "session_state"):
        if "financial_data" not in context.session_state:
            context.session_state["financial_data"] = []
        context.session_state["financial_data"].append(financial_data)
    
    if not financial_data:
        return {
            "status": "error",
            "error_message": "No financial data provided. Please extract at least one field (amount, currency, transaction_type, date, description, category, account_number, or notes)."
        }
    
    return {
        "status": "success",
        "message": f"Successfully entered financial data: {financial_data}",
        "data": financial_data
    }


def extract_data_from_file(
    file_content: str,
    file_type: Optional[str] = None,
    context: ToolContext = None,
) -> Dict[str, Any]:
    """Extracts structured data from uploaded file content.
    
    This tool analyzes file content and extracts relevant information.
    It can be used by both Customer Info and Finances agents.
    
    Args:
        file_content: The text content of the uploaded file
        file_type: Type of file (e.g., 'pdf', 'txt', 'csv', 'json')
        context: ToolContext for accessing session state (automatically provided)
    
    Returns:
        dict: Extracted data and suggestions for which agent should process it
    """
    # Store file content in session state
    if context and hasattr(context, "session_state"):
        if "uploaded_files" not in context.session_state:
            context.session_state["uploaded_files"] = []
        context.session_state["uploaded_files"].append({
            "content": file_content,
            "type": file_type or "unknown"
        })
    
    # Simple analysis to suggest agent type
    content_lower = file_content.lower()
    customer_keywords = ["name", "email", "phone", "address", "customer", "client", "contact"]
    finance_keywords = ["amount", "payment", "invoice", "transaction", "balance", "account", "financial", "revenue"]
    
    customer_score = sum(1 for keyword in customer_keywords if keyword in content_lower)
    finance_score = sum(1 for keyword in finance_keywords if keyword in content_lower)
    
    suggestion = "customer_info" if customer_score > finance_score else "finances"
    
    return {
        "status": "success",
        "message": f"File content analyzed. Suggested agent: {suggestion}",
        "suggested_agent": suggestion,
        "customer_keywords_found": customer_score,
        "finance_keywords_found": finance_score,
        "file_content_preview": file_content[:500] if len(file_content) > 500 else file_content
    }

