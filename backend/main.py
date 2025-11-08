from google.cloud import aiplatform_v1 #Vertex AI's API client library
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
from agent_logic.agent import root_agent
from agent_logic.tools import get_storage, clear_storage
from google.adk import Runner
from google.adk.sessions import InMemorySessionService

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="Hackathon API", version="1.0.0")

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Google Cloud Vertex AI configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID", "ferrous-plating-477602-p2")
REGION = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Check if Google Cloud credentials are configured
if not GOOGLE_APPLICATION_CREDENTIALS and not os.path.exists(os.path.expanduser("~/.config/gcloud/application_default_credentials.json")):
    print("WARNING: Google Cloud credentials not found. Set GOOGLE_APPLICATION_CREDENTIALS in .env or run 'gcloud auth application-default login'")

AGENT_RESOURCE_NAME = f"projects/{PROJECT_ID}/locations/{REGION}/agents/1234567890"

# Constants for session management
APP_NAME = "multi_agent_system"
DEFAULT_USER_ID = "default_user"

# Initialize SessionService for state management
session_service = InMemorySessionService()

# Initialize Runner for agent execution with delegation support
runner = Runner(
    agent=root_agent,
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
        # Example: Replace this with your actual AI service call
        # For now, returning a mock response
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
                # Session doesn't exist, create new one
                session = await session_service.create_session(
                    app_name=APP_NAME,
                    user_id=user_id
                )
                session_id = session.session_id
        else:
            # Create new session
            session = await session_service.create_session(
                app_name=APP_NAME,
                user_id=user_id
            )
            session_id = session.session_id
        
        # Run the agent with the runner (supports delegation)
        result_chunks = []
        final_result = None
        
        async for chunk in runner.run_async(
            message,
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
        ):
            # Handle different chunk types
            if hasattr(chunk, 'content'):
                result_chunks.append(str(chunk.content))
            elif hasattr(chunk, 'text'):
                result_chunks.append(str(chunk.text))
            elif isinstance(chunk, str):
                result_chunks.append(chunk)
            elif isinstance(chunk, dict):
                if "content" in chunk:
                    result_chunks.append(str(chunk["content"]))
                elif "text" in chunk:
                    result_chunks.append(str(chunk["text"]))
                else:
                    result_chunks.append(str(chunk))
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
            if hasattr(final_result, 'content'):
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


