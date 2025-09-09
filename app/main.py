from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.core.config import settings
from app.api.v1.api import api_router
from app.api.v1.endpoints.chat import initialize_chatbot_embeddings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    await initialize_chatbot_embeddings()
    yield
    # Code to run on shutdown (if any)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    openapi_url=f"/openapi.json" if settings.DEBUG else None
)

# CORS middleware untuk widget
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Sesuaikan dengan domain website Anda
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Simple chat widget demo"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Atabot-Lite Demo</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            .chat-container { max-width: 600px; margin: 0 auto; }
            h1 { text-align: center; }
            .info { background: #f0f0f0; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <h1>Atabot-Lite Demo</h1>
            <div class="info">
                <p><strong>API Endpoints:</strong></p>
                <ul>
                    <li>POST /api/v1/chat/message - Send message</li>
                    <li>GET /api/v1/chat/history/{session_id} - Get history</li>
                    <li>DELETE /api/v1/chat/session/{session_id} - Clear session</li>
                    <li>POST /api/v1/chat/reload - Reload data</li>
                </ul>
                <p>Documentation: <a href="/docs">/docs</a></p>
            </div>
        </div>
    </body>
    </html>
    """

# Include routers
app.include_router(api_router, prefix="/api/v1")