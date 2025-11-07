import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.config.settings import RAW_PPT_DIR
from app.services.ppt_loader import process_ppt
from app.services.vector_store import process_text_for_embeddings
import re
from app.services.ppt_retriever import PPTRetriever
from app.utils.logger import logger

router = APIRouter(
    prefix="/upload",
    tags=["upload"]
)


@router.post("/ppt")
async def upload_ppt(file: UploadFile = File(...), generate_embeddings: bool = True):
    """
    Upload a PPT file, extract text, and optionally generate embeddings.

    Args:
        file (UploadFile): Uploaded PPTX file.
        generate_embeddings (bool): Whether to generate embeddings immediately.

    Returns:
        dict: Paths of saved text and embeddings.
    """
    # Validate file extension
    if not file.filename.lower().endswith(".pptx"):
        raise HTTPException(status_code=400, detail="Only .pptx files are allowed.")

    # Save uploaded file
    ppt_path = os.path.join(RAW_PPT_DIR, file.filename)
    try:
        contents = await file.read()
        with open(ppt_path, "wb") as f:
            f.write(contents)
        logger.info(f" Uploaded PPT: {file.filename}")
    except Exception as e:
        logger.error(f" Failed to save uploaded PPT: {e}")
        raise HTTPException(status_code=500, detail="Failed to save PPT.")

    # Extract text
    txt_path = process_ppt(ppt_path)

    # Semantic chunking and FAISS index update
    retriever = PPTRetriever()
    with open(txt_path, "r", encoding="utf-8") as f:
        text = f.read()
    # Simple chunking: split by double newlines or every 500 chars
    chunks = [chunk.strip() for chunk in re.split(r'\n\n+', text) if chunk.strip()]
    if not chunks or len(chunks) < 2:
        # fallback: fixed-size chunks
        chunks = [text[i:i+500] for i in range(0, len(text), 500)]
    retriever.create_index(chunks)

    return {
        "ppt_path": ppt_path,
        "extracted_text_path": txt_path,
        "faiss_index_path": retriever.index_path,
        "faiss_chunks_path": retriever.chunk_path,
        "num_chunks": len(chunks)
    }
