from google.cloud import aiplatform_v1 #Vertex AI's API client library
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import logging
import uuid
from dotenv import load_dotenv
from agent_logic.agent import root_agent, customer_info_agent, finances_agent
from agent_logic.tools import get_storage, clear_storage, update_all_customers_category
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.runners import types as runner_types

# Set up logging
logger = logging.getLogger(__name__)

# loding environment variables from .env file
load_dotenv()

app = FastAPI(title="Hackathon API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3002",
        "http://127.0.0.1:3002",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Accept-Language",
        "Origin",
        "X-Requested-With",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
    ],
    expose_headers=["*"],
    max_age=600,
)

# gcloud configuration

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID", "ferrous-plating-477602-p2")
REGION = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# a check for gcloud
if not GOOGLE_APPLICATION_CREDENTIALS and not os.path.exists(os.path.expanduser("~/.config/gcloud/application_default_credentials.json")):
    print("WARNING: Google Cloud credentials not found. Set GOOGLE_APPLICATION_CREDENTIALS in .env or run 'gcloud auth application-default login'")

AGENT_RESOURCE_NAME = f"projects/{PROJECT_ID}/locations/{REGION}/agents/1234567890"

# constants for session management
APP_NAME = "multi_agent_system"
DEFAULT_USER_ID = "default_user"

# initializing SessionService for state management
session_service = InMemorySessionService()

# initializing Runner for agent execution with delegation support
runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service,
)

# initializing separate runners for direct agent access
customer_runner = Runner(
    agent=customer_info_agent,
    app_name=APP_NAME,
    session_service=session_service,
)

finance_runner = Runner(
    agent=finances_agent,
    app_name=APP_NAME,
    session_service=session_service,
) 

# Example request/response models
class HealthResponse(BaseModel):
    status: str
    message: str

class AIRequest(BaseModel):
    prompt: str
    max_tokens: Optional[int] = 100

class AIResponse(BaseModel):
    response: str
    tokens_used: Optional[int] = None

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Hackathon API is running"}

@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return {"status": "ok", "message": "API is healthy"}

@app.post("/api/ai/generate", response_model=AIResponse)
async def generate_ai_response(request: AIRequest):
    """
    Example AI endpoint - replace with your actual AI service integration
    
    Example integrations:
    - OpenAI: from openai import OpenAI
    - Anthropic: from anthropic import Anthropic
    - Hugging Face: from transformers import pipeline
    """
    try:
        ai_api_key = os.getenv("AI_API_KEY", "")
        
        if not ai_api_key:
            return {
                "response": "AI API key not configured. Set AI_API_KEY in your .env file.",
                "tokens_used": 0
            }
        
        # TODO: Integrate with your AI service
        # Example with OpenAI:
        # from openai import OpenAI
        # client = OpenAI(api_key=ai_api_key)
        # response = client.chat.completions.create(
        #     model="gpt-3.5-turbo",
        #     messages=[{"role": "user", "content": request.prompt}],
        #     max_tokens=request.max_tokens
        # )
        # return {
        #     "response": response.choices[0].message.content,
        #     "tokens_used": response.usage.total_tokens
        # }
        
        return {
            "response": f"Mock response to: {request.prompt}",
            "tokens_used": len(request.prompt.split())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class AgentRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    file_content: Optional[str] = None  # For uploaded file content

class AgentResponse(BaseModel):
    response: str
    session_id: Optional[str] = None

class SessionStateResponse(BaseModel):
    session_id: str
    customer_info: Optional[list] = None
    financial_data: Optional[list] = None
    uploaded_files: Optional[list] = None
    full_state: Optional[dict] = None

async def _run_agent_helper(
    runner: Runner,
    message: str,
    user_id: str,
    session_id: Optional[str] = None
) -> tuple[str, str]:
    """Helper function to run an agent and return response and session_id."""
    # Get or create session
    if session_id:
        session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id
        )
        if not session:
            # Session doesn't exist, create new one with generated ID
            session_id = str(uuid.uuid4())
            await session_service.create_session(
                app_name=APP_NAME,
                user_id=user_id,
                session_id=session_id
            )
    else:
        # Create new session with generated ID
        session_id = str(uuid.uuid4())
        await session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id
        )
    
    # Run the agent - Runner.run_async takes new_message, user_id, and session_id
    # Convert string message to Content object
    content_message = runner_types.Content(
        parts=[runner_types.Part(text=message)]
    ) if message else None
    
    result_chunks = []
    final_result = None
    
    async for chunk in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content_message,
    ):
        # Handle Content objects (from ADK)
        if isinstance(chunk, runner_types.Content):
            if chunk.parts:
                for part in chunk.parts:
                    if hasattr(part, 'text') and part.text:
                        result_chunks.append(part.text)
        # Handle chunks with content attribute
        elif hasattr(chunk, 'content'):
            if isinstance(chunk.content, runner_types.Content):
                if chunk.content.parts:
                    for part in chunk.content.parts:
                        if hasattr(part, 'text') and part.text:
                            result_chunks.append(part.text)
            else:
                result_chunks.append(str(chunk.content))
        # Handle chunks with text attribute
        elif hasattr(chunk, 'text'):
            result_chunks.append(str(chunk.text))
        # Handle string chunks
        elif isinstance(chunk, str):
            result_chunks.append(chunk)
        # Handle dict chunks
        elif isinstance(chunk, dict):
            if "content" in chunk:
                result_chunks.append(str(chunk["content"]))
            elif "text" in chunk:
                result_chunks.append(str(chunk["text"]))
            else:
                result_chunks.append(str(chunk))
        # Fallback: try to convert to string
        else:
            try:
                result_chunks.append(str(chunk))
            except:
                result_chunks.append(repr(chunk))
        
        final_result = chunk
    
    # Combine all chunks
    if result_chunks:
        result = "".join(result_chunks)
    elif final_result:
        # Handle Content objects
        if isinstance(final_result, runner_types.Content):
            if final_result.parts:
                text_parts = []
                for part in final_result.parts:
                    if hasattr(part, 'text') and part.text:
                        text_parts.append(part.text)
                result = "".join(text_parts) if text_parts else "No response from agent"
            else:
                result = "No response from agent"
        elif hasattr(final_result, 'content'):
            if isinstance(final_result.content, runner_types.Content):
                if final_result.content.parts:
                    text_parts = []
                    for part in final_result.content.parts:
                        if hasattr(part, 'text') and part.text:
                            text_parts.append(part.text)
                    result = "".join(text_parts) if text_parts else "No response from agent"
                else:
                    result = "No response from agent"
            else:
                result = str(final_result.content)
        elif hasattr(final_result, 'text'):
            result = str(final_result.text)
        else:
            result = str(final_result)
    else:
        result = "No response from agent"
    
    return result, session_id

@app.post("/api/agent/chat", response_model=AgentResponse)
async def chat_with_agent(request: AgentRequest):
    """
    Chat with the multi-agent system using Google ADK.
    The root agent will analyze the prompt and delegate to the appropriate specialized agent.
    Supports file content uploads and maintains session state across conversations.
    """
    try:
        # Get or create session
        user_id = request.user_id or DEFAULT_USER_ID
        session_id = request.session_id
        
        # Prepare the message - include file content if provided
        message = request.message
        if request.file_content:
            message = f"{message}\n\nUploaded file content:\n{request.file_content}"
        
        # Get or create session
        if session_id:
            session = await session_service.get_session(
                app_name=APP_NAME,
                user_id=user_id,
                session_id=session_id
            )
            if not session:
                # Session doesn't exist, create new one with generated ID
                session_id = str(uuid.uuid4())
                await session_service.create_session(
                    app_name=APP_NAME,
                    user_id=user_id,
                    session_id=session_id
                )
        else:
            # Create new session with generated ID
            session_id = str(uuid.uuid4())
            await session_service.create_session(
                app_name=APP_NAME,
                user_id=user_id,
                session_id=session_id
            )
        
        # Run the agent with the runner (supports delegation)
        # Convert string message to Content object
        content_message = runner_types.Content(
            parts=[runner_types.Part(text=message)]
        ) if message else None
        
        result_chunks = []
        final_result = None
        
        async for chunk in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content_message,
        ):
            # Handle Content objects (from ADK)
            if isinstance(chunk, runner_types.Content):
                if chunk.parts:
                    for part in chunk.parts:
                        if hasattr(part, 'text') and part.text:
                            result_chunks.append(part.text)
            # Handle chunks with content attribute
            elif hasattr(chunk, 'content'):
                if isinstance(chunk.content, runner_types.Content):
                    if chunk.content.parts:
                        for part in chunk.content.parts:
                            if hasattr(part, 'text') and part.text:
                                result_chunks.append(part.text)
                else:
                    result_chunks.append(str(chunk.content))
            # Handle chunks with text attribute
            elif hasattr(chunk, 'text'):
                result_chunks.append(str(chunk.text))
            # Handle string chunks
            elif isinstance(chunk, str):
                result_chunks.append(chunk)
            # Handle dict chunks
            elif isinstance(chunk, dict):
                if "content" in chunk:
                    result_chunks.append(str(chunk["content"]))
                elif "text" in chunk:
                    result_chunks.append(str(chunk["text"]))
                else:
                    result_chunks.append(str(chunk))
            # Fallback: try to convert to string
            else:
                try:
                    result_chunks.append(str(chunk))
                except:
                    result_chunks.append(repr(chunk))
            
            final_result = chunk
        
        # Combine all chunks
        if result_chunks:
            result = "".join(result_chunks)
        elif final_result:
            # Handle Content objects
            if isinstance(final_result, runner_types.Content):
                if final_result.parts:
                    text_parts = []
                    for part in final_result.parts:
                        if hasattr(part, 'text') and part.text:
                            text_parts.append(part.text)
                    result = "".join(text_parts) if text_parts else "No response from agent"
                else:
                    result = "No response from agent"
            elif hasattr(final_result, 'content'):
                if isinstance(final_result.content, runner_types.Content):
                    if final_result.content.parts:
                        text_parts = []
                        for part in final_result.content.parts:
                            if hasattr(part, 'text') and part.text:
                                text_parts.append(part.text)
                        result = "".join(text_parts) if text_parts else "No response from agent"
                    else:
                        result = "No response from agent"
                else:
                    result = str(final_result.content)
            elif hasattr(final_result, 'text'):
                result = str(final_result.text)
            else:
                result = str(final_result)
        else:
            result = "No response from agent"
        
        return {
            "response": result,
            "session_id": session_id
        }
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=f"Agent error: {error_detail}")

@app.post("/api/agent/customer", response_model=AgentResponse)
async def chat_with_customer_agent(request: AgentRequest):
    """
    Chat directly with the customer_info_agent.
    Bypasses the root agent and goes straight to customer information processing.
    Supports file content uploads and maintains session state.
    """
    try:
        user_id = request.user_id or DEFAULT_USER_ID
        
        # Prepare the message - include file content if provided
        message = request.message
        if request.file_content:
            message = f"{message}\n\nUploaded file content:\n{request.file_content}"
        
        result, session_id = await _run_agent_helper(
            customer_runner,
            message,
            user_id,
            request.session_id
        )
        
        return {
            "response": result,
            "session_id": session_id
        }
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=f"Customer agent error: {error_detail}")

@app.post("/api/agent/finance", response_model=AgentResponse)
async def chat_with_finance_agent(request: AgentRequest):
    """
    Chat directly with the finances_agent.
    Bypasses the root agent and goes straight to financial data processing.
    Supports file content uploads and maintains session state.
    """
    try:
        user_id = request.user_id or DEFAULT_USER_ID
        
        # Prepare the message - include file content if provided
        message = request.message
        if request.file_content:
            message = f"{message}\n\nUploaded file content:\n{request.file_content}"
        
        result, session_id = await _run_agent_helper(
            finance_runner,
            message,
            user_id,
            request.session_id
        )
        
        return {
            "response": result,
            "session_id": session_id
        }
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=f"Finance agent error: {error_detail}")

@app.get("/api/agent/session/{session_id}", response_model=SessionStateResponse)
async def get_session_state(session_id: str, user_id: Optional[str] = None):
    """
    Get the current session state for debugging and testing.
    Shows all stored customer info, financial data, and uploaded files.
    """
    try:
        user_id = user_id or DEFAULT_USER_ID
        
        session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id
        )
        
        if not session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        # Extract state data
        state = session.state if hasattr(session, 'state') else {}
        
        return {
            "session_id": session_id,
            "customer_info": state.get("customer_info", []),
            "financial_data": state.get("financial_data", []),
            "uploaded_files": state.get("uploaded_files", []),
            "full_state": state
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving session state: {str(e)}")

@app.get("/api/customers/stats")
async def get_customer_stats():
    """
    Get customer statistics (counts by category, totals).
    """
    try:
        storage = get_storage()
        
        # Check if get_storage returned an error - return empty stats instead of failing
        if "error" in storage:
            logger.warning(f"Storage error (returning empty stats): {storage.get('error', 'Unknown error')}")
            return {
                "status": "success",
                "stats": {
                    "total": 0,
                    "prospective": 0,
                    "current": 0,
                    "inactive": 0,
                    "uncategorized": 0
                }
            }
        
        customers = storage.get("customer_info", [])
        
        stats = {
            "total": len(customers),
            "prospective": 0,
            "current": 0,
            "inactive": 0,
            "uncategorized": 0
        }
        
        for customer in customers:
            category = customer.get("category")
            if not category:
                stats["uncategorized"] += 1
            elif category.lower() == "prospective":
                stats["prospective"] += 1
            elif category.lower() == "current":
                stats["current"] += 1
            elif category.lower() == "inactive":
                stats["inactive"] += 1
            else:
                stats["uncategorized"] += 1
        
        return {
            "status": "success",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving customer stats: {str(e)}")

@app.get("/api/customers")
async def get_customers(category: Optional[str] = None):
    """
    Get all customers, optionally filtered by category.
    Query param: ?category=Prospective|Current|Inactive
    """
    try:
        storage = get_storage()
        
        # Check if get_storage returned an error - return empty list instead of failing
        if "error" in storage:
            logger.warning(f"Storage error (returning empty list): {storage.get('error', 'Unknown error')}")
            return {
                "status": "success",
                "count": 0,
                "customers": []
            }
        
        customers = storage.get("customer_info", [])
        
        if category:
            # Filter by category (case-insensitive)
            customers = [
                c for c in customers
                if c.get("category") and c.get("category").lower() == category.lower()
            ]
        
        return {
            "status": "success",
            "count": len(customers),
            "customers": customers
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving customers: {str(e)}")

@app.get("/api/customers/{customer_id}")
async def get_customer(customer_id: str):
    """
    Get a specific customer by email (used as ID).
    """
    try:
        storage = get_storage()
        
        # Check if get_storage returned an error
        if "error" in storage:
            logger.warning(f"Storage error: {storage.get('error', 'Unknown error')}")
            raise HTTPException(
                status_code=404,
                detail=f"Customer not found (storage unavailable: {storage.get('error', 'Unknown error')})"
            )
        
        customers = storage.get("customer_info", [])
        
        # Find customer by email (case-insensitive)
        customer = None
        for c in customers:
            if c.get("email") and c.get("email").lower() == customer_id.lower():
                customer = c
                break
        
        if not customer:
            raise HTTPException(status_code=404, detail=f"Customer with email {customer_id} not found")
        
        return {
            "status": "success",
            "customer": customer
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving customer: {str(e)}")

class UpdateCategoryRequest(BaseModel):
    category: str

@app.post("/api/customers/update-category")
async def update_customers_category(request: UpdateCategoryRequest):
    """
    Update all customers to have the specified category.
    Category must be: Prospective, Current, or Inactive
    """
    try:
        result = update_all_customers_category(request.category)
        
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message", "Failed to update categories"))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating customer categories: {str(e)}")

@app.get("/api/storage")
async def view_storage():
    """
    View all data stored by the tools (customer info, financial data, uploaded files).
    Quick endpoint to check if data is being entered correctly.
    """
    try:
        storage = get_storage()
        return {
            "status": "success",
            "customer_info_count": len(storage["customer_info"]),
            "financial_data_count": len(storage["financial_data"]),
            "uploaded_files_count": len(storage["uploaded_files"]),
            "customer_info": storage["customer_info"],
            "financial_data": storage["financial_data"],
            "uploaded_files": storage["uploaded_files"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving storage: {str(e)}")

@app.delete("/api/storage")
async def clear_storage_endpoint():
    """
    Clear all stored data (customer info, financial data, uploaded files).
    """
    try:
        clear_storage()
        return {
            "status": "success",
            "message": "All stored data cleared"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing storage: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


