from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from app.routes.upload_routes import router as upload_router
from app.routes.chat_routes import router as chat_router
import os

# Initialize FastAPI
app = FastAPI(
    title="RAG PPT Chatbot",
    description="Upload PPT files and chat with the content using Gemini-powered RAG pipeline.",
    version="1.0.0"
)

# Include API Routers
app.include_router(upload_router, prefix="/api/upload", tags=["Upload"])
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])

# Serve all static files from your moved 'static' folder
static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../static")
if not os.path.exists(static_path):
    os.makedirs(static_path)

app.mount("/static", StaticFiles(directory=static_path), name="static")

# Root endpoint: serve index.html
@app.get("/", response_class=HTMLResponse)
async def root():
    index_file = os.path.join(static_path, "index.html")
    if not os.path.exists(index_file):
        return HTMLResponse("<h1>index.html not found in static folder</h1>", status_code=404)
    with open(index_file, "r", encoding="utf-8") as f:
        return f.read()
