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
        "such as names, emails, phone numbers, addresses, company information, or contact details. "
        "This agent handles customer profiles, contact information, and customer-related data entry."
    ),
    instruction=(
        "You are a specialized agent focused on customer information management. "
        "Your primary role is to extract customer data from user prompts or uploaded files "
        "and enter it into the system using the available tools. "
        "\n\n"
        "When processing information:\n"
        "- Carefully extract all available customer details (name, email, phone, address, company, notes)\n"
        "- Use the enter_customer_info tool to store the extracted data\n"
        "- If files are provided, use extract_data_from_file first to analyze the content\n"
        "- Be thorough and accurate when extracting information\n"
        "- Confirm what data was entered after each operation\n"
        "- If information is incomplete, ask clarifying questions or note what's missing\n"
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
        "such as transactions, amounts, payments, invoices, account details, or any money-related data. "
        "This agent handles all finance-related data entry and processing."
    ),
    instruction=(
        "You are a specialized agent focused on financial data management. "
        "Your primary role is to extract financial information from user prompts or uploaded files "
        "and enter it into the system using the available tools. "
        "\n\n"
        "When processing information:\n"
        "- Carefully extract all available financial details (amount, currency, transaction type, date, description, category, account number, notes)\n"
        "- Use the enter_financial_data tool to store the extracted data\n"
        "- If files are provided, use extract_data_from_file first to analyze the content\n"
        "- Be precise with amounts and dates\n"
        "- Confirm what data was entered after each operation\n"
        "- If information is incomplete, ask clarifying questions or note what's missing\n"
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
        "1. customer_info_agent - For customer information, contact details, customer profiles, names, emails, phones, addresses\n"
        "2. finances_agent - For financial data, transactions, payments, invoices, amounts, account information\n"
        "\n\n"
        "Decision guidelines:\n"
        "- If the prompt/files contain customer information (names, emails, phones, addresses, contact info) → delegate to customer_info_agent\n"
        "- If the prompt/files contain financial data (amounts, transactions, payments, invoices, account numbers) → delegate to finances_agent\n"
        "- If both types of information are present, prioritize based on the primary intent or ask the user to clarify\n"
        "- If the content is unclear, ask the user for clarification about what type of data they want to enter\n"
        "\n\n"
        "When delegating:\n"
        "- Clearly explain which agent you're routing to and why\n"
        "- The delegated agent will handle the actual data extraction and entry\n"
        "- You can delegate multiple times if needed for different types of data\n"
    ),
    tools=[],  # Root agent doesn't need tools, it only delegates
    sub_agents=[customer_info_agent, finances_agent],  # Enable delegation to sub-agents
)
