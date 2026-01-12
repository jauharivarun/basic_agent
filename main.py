"""
FastAPI application with LangChain Agent integration
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from agent import get_agent_service, reset_agent_service

# Initialize FastAPI app
app = FastAPI(
    title="LangChain Agent API",
    description="A FastAPI application with a LangChain tool-using agent",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["carepay.money"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)


# Request/Response Models
class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str
    chat_history: Optional[List[dict]] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str
    tools_used: List[str]
    success: bool


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    message: str


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return {
        "status": "healthy",
        "message": "LangChain Agent API is running"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Try to get agent service to verify it's initialized
        agent_service = get_agent_service()
        return {
            "status": "healthy",
            "message": "Agent service is ready"
        }
    except Exception as e:
        # Reset service on error to allow retry
        reset_agent_service()
        raise HTTPException(
            status_code=503,
            detail=f"Agent service not available: {str(e)}"
        )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main endpoint to interact with the agent.
    
    Args:
        request: ChatRequest containing the user message and optional chat history
    
    Returns:
        ChatResponse with the agent's response and metadata
    """
    try:
        # Validate message
        if not request.message or not request.message.strip():
            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty"
            )
        
        # Get agent service
        agent_service = get_agent_service()
        
        # Process the message
        result = agent_service.process_message(
            message=request.message,
            chat_history=request.chat_history
        )
        
        # Return response
        return ChatResponse(
            response=result["response"],
            tools_used=result["tools_used"],
            success=result["success"]
        )
    
    except ValueError as e:
        # Handle configuration errors - reset service to allow retry
        reset_agent_service()
        raise HTTPException(
            status_code=500,
            detail=f"Configuration error: {str(e)}"
        )
    except Exception as e:
        # Handle other errors
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


