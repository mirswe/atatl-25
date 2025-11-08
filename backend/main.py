from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


