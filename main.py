"""
FastAPI application with LangChain Agent integration and items CRUD API
"""
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from api.items import router as items_router
from api.categories import router as categories_router
from agent import get_agent_service, reset_agent_service
from auth import require_api_key
from exceptions import AppError


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create SQLite tables on startup (import ORM models so metadata is registered)."""
    from sqlalchemy import text

    from database import Base, engine

    import db_models  # noqa: F401

    Base.metadata.create_all(bind=engine)

    # Lightweight migration for existing local DBs:
    # add items.category_id if this project started before Step 4.
    with engine.connect() as connection:
        columns = connection.execute(text("PRAGMA table_info(items)")).fetchall()
        has_category_id = any(col[1] == "category_id" for col in columns)
        if not has_category_id:
            connection.execute(text("ALTER TABLE items ADD COLUMN category_id INTEGER"))
            connection.commit()
    yield


# Initialize FastAPI app
app = FastAPI(
    title="LangChain Agent API",
    description="A FastAPI application with a LangChain tool-using agent and items CRUD",
    version="2.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["carepay.money"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["Content-Type", "Authorization"],
)

# ---------------------------------------------------------------------------
# Global exception handlers — every error returns the same JSON shape:
# {"status_code": ..., "error": "...", "detail": "..."}
# ---------------------------------------------------------------------------

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Handles all intentional AppErrors raised anywhere in the codebase."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"status_code": exc.status_code, "error": exc.error, "detail": exc.detail},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Wraps FastAPI's built-in HTTPException into the standard error envelope."""
    from http import HTTPStatus
    try:
        error_name = HTTPStatus(exc.status_code).phrase
    except ValueError:
        error_name = "HTTP Error"
    return JSONResponse(
        status_code=exc.status_code,
        content={"status_code": exc.status_code, "error": error_name, "detail": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handles Pydantic validation errors (422 Unprocessable Entity).
    Returns each field error in a readable list instead of Pydantic's raw output.
    """
    errors = []
    for err in exc.errors():
        field = " → ".join(str(loc) for loc in err["loc"] if loc != "body")
        errors.append({"field": field or "request", "message": err["msg"]})
    return JSONResponse(
        status_code=422,
        content={"status_code": 422, "error": "Validation Error", "detail": errors},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for any unexpected Python exceptions — never leaks tracebacks."""
    return JSONResponse(
        status_code=500,
        content={"status_code": 500, "error": "Internal Server Error", "detail": "An unexpected error occurred"},
    )


# Mount items CRUD routes under /items (see api/items.py for prefix and tags)
app.include_router(items_router, dependencies=[Depends(require_api_key)])
app.include_router(categories_router, dependencies=[Depends(require_api_key)])


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


class VersionResponse(BaseModel):
    """Response model for the public version/metadata endpoint."""

    title: str
    version: str
    description: str


@app.get("/version", response_model=VersionResponse, tags=["meta"])
async def api_version() -> VersionResponse:
    """Public: app name and version (no API key; safe for load balancers and clients)."""
    return VersionResponse(
        title=app.title,
        version=app.version,
        description=app.description or "",
    )


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return {
        "status": "healthy",
        "message": "LangChain Agent API is running",
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Try to get agent service to verify it's initialized
        get_agent_service()
        return {
            "status": "healthy",
            "message": "Agent service is ready",
        }
    except Exception as e:
        # Reset service on error to allow retry
        reset_agent_service()
        raise HTTPException(
            status_code=503,
            detail=f"Agent service not available: {str(e)}",
        )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, _: None = Depends(require_api_key)):
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
                detail="Message cannot be empty",
            )

        # Get agent service
        agent_service = get_agent_service()

        # Process the message
        result = agent_service.process_message(
            message=request.message,
            chat_history=request.chat_history,
        )

        # Return response
        return ChatResponse(
            response=result["response"],
            tools_used=result["tools_used"],
            success=result["success"],
        )

    except ValueError as e:
        # Handle configuration errors - reset service to allow retry
        reset_agent_service()
        raise HTTPException(
            status_code=500,
            detail=f"Configuration error: {str(e)}",
        )
    except Exception as e:
        # Handle other errors
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}",
        )
