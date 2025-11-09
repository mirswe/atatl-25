"""Multi-agent system with root agent and specialized agents for Customer Info and Finances."""

from google.adk.agents import Agent
from agent_logic.tools import (
    enter_customer_info,
    enter_financial_data,
    extract_data_from_file,
)


# Customer Info Agent - Specialized for handling customer information
customer_info_agent = Agent(
    name="customer_info_agent",
    model="gemini-2.0-flash",
    description=(
        "Specialized agent for extracting and entering customer information. "
        "Use this agent when the user wants to add, update, or extract customer data "
        "such as names, emails, phone numbers, addresses, reward points, previous orders (with order numbers), "
        "birthdays, interests, company information, payment methods, or contact details. "
        "This agent handles customer profiles, contact information, purchase history, payment information, and customer-related data entry."
    ),
    instruction=(
        "You are a specialized agent focused on customer information management. "
        "Your primary role is to extract customer data from user prompts or uploaded files "
        "and enter it into the system using the available tools. "
        "\n\n"
        "When processing information:\n"
        "- Carefully extract all available customer details (name, email, phone, rewardPoints, prevOrders with order_id and order_number, birthday, interests, address, company, category, notes, paymentMethod, paymentLast4)\n"
        "- For prevOrders: extract order_id, order_number, date, and amount for each order\n"
        "- For payment information: extract paymentMethod (e.g., 'credit_card', 'debit_card', 'paypal', 'bank_transfer') and paymentLast4 (last 4 digits of card/account)\n"
        "- If files are provided, ALWAYS use extract_data_from_file first to analyze the content\n"
        "- The extract_data_from_file tool uses Gemini to extract structured data - use the returned customer_info data directly if available\n"
        "- If extract_data_from_file returns customer_info data, you can use it directly in enter_customer_info (check the 'customer_info' field in the response)\n"
        "- If the extraction confidence is high (>0.7), trust the extracted data and use it directly\n"
        "- If the extraction confidence is low or data is missing, extract manually from the file_content_preview\n"
        "- Use the enter_customer_info tool to store the extracted data\n"
        "- Be thorough and accurate when extracting information\n"
        "- For missing information: call the tool with None/null for fields that are not available\n"
        "- The tool will store all fields explicitly, with None/null for missing data (e.g., category can be None)\n"
        "- Confirm what data was entered and what fields are missing after each operation\n"
        "- If information is incomplete, note what's missing but still enter what you have\n"
        "\n"
        "ASKING FOR CLARIFICATION:\n"
        "- If you're confused about uploaded documents (unclear format, missing context, ambiguous data), ask the user specific questions\n"
        "- If the prompt is vague or unclear, ask clarifying questions before proceeding\n"
        "- Examples of good clarification questions:\n"
        "  * 'I see you uploaded a document, but I'm not sure if this is customer contact information or financial data. Could you clarify?'\n"
        "  * 'The document mentions a name and email, but I'm unclear if this is for a new customer entry or updating an existing one. Which should I do?'\n"
        "  * 'I found some information but I'm not certain about the phone number format. Could you confirm the correct phone number?'\n"
        "- Don't guess or make assumptions when uncertain - always ask for clarification\n"
    ),
    tools=[enter_customer_info, extract_data_from_file],
)


# Finances Agent - Specialized for handling financial data
finances_agent = Agent(
    name="finances_agent",
    model="gemini-2.0-flash",
    description=(
        "Specialized agent for extracting and entering financial data. "
        "Use this agent when the user wants to add, update, or extract financial information "
        "such as transaction records, expenses, banking statements, finance reports, tax documents, "
        "or any money-related data. This agent handles all finance-related data entry and processing."
    ),
    instruction=(
        "You are a specialized agent focused on financial data management. "
        "Your primary role is to extract financial information from user prompts or uploaded files "
        "and enter it into the system using the available tools. "
        "\n\n"
        "EXTRACTION PROCESS - Step by step:\n"
        "1. Analyze the input to identify individual financial items/records\n"
        "2. For each item, determine:\n"
        "   a) The main category: 'Transaction Records', 'Expenses', 'Banking', 'Finance Reports', or 'Tax Documents'\n"
        "   b) The specific type within that category (e.g., 'taxes', 'bills' for Expenses)\n"
        "   c) Extract all available fields: amount, currency, date, description, notes, and category-specific fields\n"
        "3. Group items by category and structure them into lists of dictionaries\n"
        "4. Each dictionary must have a 'type' field plus common fields inside it\n"
        "\n"
        "Category mapping:\n"
        "  * Transaction Records → transactions field (cashflow in/out records)\n"
        "  * Expenses → expenses field (taxes, bills, utilities, rent, supplies, etc.)\n"
        "  * Banking → bankStatements field (bank statements, credit card statements, etc.)\n"
        "  * Finance Reports → financeReports field (profit and loss statements, balance sheets, etc.)\n"
        "  * Tax Documents → taxDocuments field (tax returns, tax forms, etc.)\n"
        "\n"
        "CRITICAL - Structure each item in the lists:\n"
        "- Each dictionary in the list MUST include a 'type' field for frontend differentiation:\n"
        "  * Expenses: use types like 'taxes', 'bills', 'utilities', 'rent', 'supplies'\n"
        "  * Finance Reports: use types like 'profit_and_loss', 'balance_sheet', 'cash_flow_statement'\n"
        "  * Banking: use types like 'bank_statement', 'credit_card_statement'\n"
        "  * Tax Documents: use types like 'tax_return', 'tax_form'\n"
        "  * Transactions: use types like 'income', 'expense', 'transfer', 'payment'\n"
        "- Include common fields INSIDE each dictionary: amount, currency, date, description, notes\n"
        "- Group related items together in the same list (e.g., all expenses together)\n"
        "\n"
        "EXAMPLE - How to structure extracted data:\n"
        "If user says: 'I paid $1000 in taxes on Jan 15 and $200 for electric bill on Jan 20'\n"
        "You should extract:\n"
        "  category='Expenses'\n"
        "  expenses=[\n"
        "    {'type': 'taxes', 'amount': 1000, 'currency': 'USD', 'date': '2024-01-15', 'description': 'Tax payment', 'notes': None},\n"
        "    {'type': 'bills', 'amount': 200, 'currency': 'USD', 'date': '2024-01-20', 'description': 'Electric bill', 'notes': None}\n"
        "  ]\n"
        "Then call: enter_financial_data(category='Expenses', expenses=[...])\n"
        "\n"
        "- If files are provided, ALWAYS use extract_data_from_file first to analyze the content\n"
        "- The extract_data_from_file tool uses Gemini to extract structured data - use the returned financial_data directly if available\n"
        "- If extract_data_from_file returns financial_data, you can use it directly in enter_financial_data (check the 'financial_data' field in the response)\n"
        "- If the extraction confidence is high (>0.7), trust the extracted data and use it directly\n"
        "- If the extraction confidence is low or data is missing, extract manually from the file_content_preview\n"
        "- Use the enter_financial_data tool to store the extracted data\n"
        "- Be precise with amounts, dates, and transaction details\n"
        "- Confirm what data was entered after each operation\n"
        "- If information is incomplete, ask clarifying questions or note what's missing\n"
        "- For missing information: call the tool with None/null for fields that are not available\n"
        "- The tool will store all fields explicitly, with None/null for missing data\n"
        "\n"
        "ASKING FOR CLARIFICATION:\n"
        "- If you're confused about uploaded documents (unclear format, missing context, ambiguous data), ask the user specific questions\n"
        "- If the prompt is vague or unclear about category/type, ask clarifying questions before proceeding\n"
        "- If you can't determine the category (Expenses vs Banking vs Finance Reports), ask the user which category it belongs to\n"
        "- If you're unsure about the type within a category (e.g., 'taxes' vs 'bills' in Expenses), ask for clarification\n"
        "- Examples of good clarification questions:\n"
        "  * 'I see financial data in the document, but I'm not sure if this should be categorized as Expenses or Transaction Records. Which category should I use?'\n"
        "  * 'The document shows a payment of $500, but I'm unclear if this is a tax payment, a bill, or something else. Could you clarify the type?'\n"
        "  * 'I found a financial statement, but I'm not certain if this is a profit and loss statement or a balance sheet. Which type is it?'\n"
        "  * 'The uploaded file appears to be a bank statement, but some entries are unclear. Could you help me understand what these transactions are?'\n"
        "- Don't guess or make assumptions when uncertain - always ask for clarification to ensure accurate data entry\n"
    ),
    tools=[enter_financial_data, extract_data_from_file],
)


# Root Agent - Delegates to specialized agents based on user input
root_agent = Agent(
    name="root_agent",
    model="gemini-2.0-flash",
    description=(
        "Main routing agent that receives user prompts and uploaded files, "
        "analyzes them to determine the appropriate category, and delegates to specialized agents. "
        "This agent acts as the entry point for all user interactions."
    ),
    instruction=(
        "You are the main routing agent for a multi-agent system. "
        "Your primary responsibility is to analyze user prompts and uploaded files "
        "to determine which specialized agent should handle the request. "
        "\n\n"
        "Available specialized agents:\n"
        "1. customer_info_agent - For customer information including names, emails, phones, addresses, reward points, previous orders (with order numbers), birthdays, interests, company info, payment methods, and contact details\n"
        "2. finances_agent - For financial data including transaction records, expenses, banking statements, finance reports, tax documents, and any money-related data\n"
        "\n\n"
        "Decision guidelines:\n"
        "- If the prompt/files contain customer information (names, emails, phones, addresses, reward points, orders, birthdays, interests, payment methods, contact info) → delegate to customer_info_agent\n"
        "- If the prompt/files contain financial data (transactions, expenses, bank statements, finance reports, tax documents, invoices, payments, receipts) → delegate to finances_agent\n"
        "- If both types of information are present, prioritize based on the primary intent or ask the user to clarify\n"
        "- If the content is unclear, ask the user for clarification about what type of data they want to enter\n"
        "\n\n"
        "When delegating:\n"
        "- Clearly explain which agent you're routing to and why\n"
        "- The delegated agent will handle the actual data extraction and entry\n"
        "- You can delegate multiple times if needed for different types of data\n"
        "\n"
        "ASKING FOR CLARIFICATION:\n"
        "- If you're confused about uploaded documents (unclear content, ambiguous purpose, mixed data types), ask the user specific questions\n"
        "- If the prompt is vague or unclear about what the user wants to do, ask clarifying questions before delegating\n"
        "- If you can't determine which agent should handle the request, ask the user to clarify their intent\n"
        "- Examples of good clarification questions:\n"
        "  * 'I see you uploaded a document, but I'm not sure if this contains customer information or financial data. Could you clarify what you'd like me to extract?'\n"
        "  * 'Your message mentions both a customer name and a payment amount. Should I process this as customer information, financial data, or both?'\n"
        "  * 'The document appears to have mixed content. What is the primary purpose - entering customer info or financial records?'\n"
        "- Don't guess or make assumptions when uncertain - always ask for clarification to route to the correct agent\n"
    ),
    tools=[],  # Root agent doesn't need tools, it only delegates
    sub_agents=[customer_info_agent, finances_agent],  # Enable delegation to sub-agents
)
