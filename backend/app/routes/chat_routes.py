import os
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse
from app.config.settings import EMBEDDINGS_DIR
from app.services.generator import generate_answer
from app.services.ppt_retriever import PPTRetriever
from app.config.settings import GEMINI_API_KEY
import requests
from app.utils.logger import logger

router = APIRouter(
    prefix="",  # actual API prefix is applied in main.py as /api/chat
    tags=["chat"]
)

# Endpoint to list all available embeddings files
@router.get("/embeddings-list", response_class=JSONResponse)
def list_embeddings():
    try:
        files = [f for f in os.listdir(EMBEDDINGS_DIR) if f.endswith("_embeddings.json")]
        return {"embeddings": files}
    except Exception as e:
        logger.error(f"Failed to list embeddings: {e}")
        raise HTTPException(status_code=500, detail="Failed to list embeddings files.")


# Endpoint to check Gemini API key and list available models
@router.get("/gemini-models-check", response_class=JSONResponse)
def gemini_models_check():
    """
    Check Gemini API key and list available models for this key.
    """
    if not GEMINI_API_KEY:
        return JSONResponse({"ok": False, "error": "GEMINI_API_KEY not set in backend."}, status_code=400)
    url = "https://generativelanguage.googleapis.com/v1/models"
    params = {"key": GEMINI_API_KEY}
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code != 200:
            return JSONResponse({"ok": False, "error": f"Gemini API error: {resp.status_code} {resp.text}"}, status_code=resp.status_code)
        data = resp.json()
        models = [m.get("name", "") for m in data.get("models", [])]
        return {"ok": True, "models": models, "raw": data}
    except Exception as e:
        logger.error(f"Gemini models check failed: {e}")
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@router.get("/gemini-test", response_class=JSONResponse)
def gemini_test(model: str = None, prompt: str = "Hello"):
    """
    Attempt a small Gemini generation using the provided model (or CHAT_MODEL from settings).
    Returns basic response info to help debug 404 / permission issues.
    """
    from app.config.settings import CHAT_MODEL, GEMINI_API_KEY
    if not GEMINI_API_KEY:
        return JSONResponse({"ok": False, "error": "GEMINI_API_KEY not set."}, status_code=400)

    model_to_try = model or CHAT_MODEL or 'models/gemini-1.0'
    url_text = f"https://generativelanguage.googleapis.com/v1/{model_to_try}:generateText"
    url_content = f"https://generativelanguage.googleapis.com/v1/{model_to_try}:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    data = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        # try generateText
        resp = requests.post(url_text, headers=headers, params=params, json=data, timeout=12)
        if resp.status_code == 404:
            # try generateContent
            resp = requests.post(url_content, headers=headers, params=params, json=data, timeout=12)

        # return status and body (truncated)
        body = None
        try:
            body = resp.json()
        except Exception:
            body = resp.text

        return {"ok": resp.ok, "status_code": resp.status_code, "body": body}
    except Exception as e:
        logger.error(f"gemini_test failed: {e}")
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@router.get("/")
def chat(query: str = Query(..., description="User question"),
         embeddings_file: str = Query(None, description="Name of embeddings JSON file (optional). Use 'ALL' to search all files")):
    """
    Query the RAG chatbot and return a generated answer.

    Args:
        query (str): The question from the user.
        embeddings_file (str): Embeddings file to search for context.

    Returns:
        dict: Generated answer.
    """
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    try:
        # Use FAISS-based semantic retrieval
        retriever = PPTRetriever()
        top_chunks = retriever.retrieve(query, top_k=3)
        answer = "\n---\n".join(top_chunks)
        return {"query": query, "answer": answer}
    except Exception as e:
        logger.error(f" Failed to generate answer for query '{query}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate answer: {e}")
