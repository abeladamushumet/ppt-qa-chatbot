import os
import json
from app.config.settings import EXTRACTED_TEXT_DIR, EMBEDDINGS_DIR
from app.utils.logger import logger

# === Ensure embeddings folder exists ===
os.makedirs(EMBEDDINGS_DIR, exist_ok=True)

def create_dummy_embeddings(text: str) -> dict:
    """
    Example placeholder: converts text into dummy embeddings.
    Replace this with real Gemini embeddings later.
    """
    # TODO: Replace this with Gemini or OpenAI embedding API call for real semantic search
    embedding = [ord(c) for c in text[:50]]  # simple example: convert chars to numbers
    return {"text": text, "embedding": embedding}

# --- Example for real Gemini embedding integration (not yet active) ---
# from app.config.settings import GEMINI_API_KEY, EMBEDDING_MODEL
# import requests
# def create_gemini_embeddings(text: str) -> dict:
#     """
#     Call Gemini embedding API to get real embeddings for the text.
#     """
#     if not GEMINI_API_KEY:
#         raise RuntimeError("GEMINI_API_KEY not set")
#     model = EMBEDDING_MODEL or 'models/embedding-001'  # update as needed
#     url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:embedText"
#     headers = {"Content-Type": "application/json"}
#     params = {"key": GEMINI_API_KEY}
#     data = {"text": text}
#     resp = requests.post(url, headers=headers, params=params, json=data, timeout=10)
#     resp.raise_for_status()
#     result = resp.json()
#     # Parse embedding from result as needed
#     return {"text": text, "embedding": result.get("embedding", [])}


def save_embeddings(filename: str, embeddings: dict) -> str:
    """
    Save embeddings dictionary to a JSON file.

    Args:
        filename (str): Name of the embeddings file
        embeddings (dict): Dictionary mapping text chunks to embeddings

    Returns:
        str: Path of saved embeddings file
    """
    try:
        filepath = os.path.join(EMBEDDINGS_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(embeddings, f, ensure_ascii=False, indent=4)
        logger.info(f"Saved embeddings: {filename}")
        return filepath
    except Exception as e:
        logger.error(f"Failed to save embeddings for {filename}: {e}")
        return ""


def load_embeddings(filename: str) -> dict:
    """
    Load embeddings from a JSON file.

    Args:
        filename (str): Name of embeddings file to load

    Returns:
        dict: Embeddings dictionary
    """
    filepath = os.path.join(EMBEDDINGS_DIR, filename)
    if not os.path.exists(filepath):
        logger.warning(f"Embeddings file does not exist: {filename}")
        return {}

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            embeddings = json.load(f)
        logger.info(f"Loaded embeddings: {filename}")
        return embeddings
    except Exception as e:
        logger.error(f"Failed to load embeddings from {filename}: {e}")
        return {}


def process_text_for_embeddings(text: str, filename_base: str) -> str:
    """
    Process a single text string and save its embeddings.

    Args:
        text (str): The extracted text from the PPT
        filename_base (str): Base name of the PPT file (without extension)

    Returns:
        str: Path to the saved embeddings JSON file
    """
    try:
        # Generate dummy embeddings (replace later with real Gemini embeddings)
        embeddings = create_dummy_embeddings(text)

        # Define output filename
        filename = f"{filename_base}_embeddings.json"

        # Save embeddings to disk
        emb_path = save_embeddings(filename, embeddings)
        logger.info(f"Embeddings generated and saved for {filename_base}")

        return emb_path
    except Exception as e:
        logger.error(f"Error generating embeddings for {filename_base}: {e}")
        return ""


def process_all_texts():
    """
    Process all .txt files in extracted_texts/ and save embeddings
    """
    txt_files = [f for f in os.listdir(EXTRACTED_TEXT_DIR) if f.endswith(".txt")]
    if not txt_files:
        logger.warning("No .txt files found in extracted_texts/")
        return

    for txt_file in txt_files:
        txt_path = os.path.join(EXTRACTED_TEXT_DIR, txt_file)
        with open(txt_path, "r", encoding="utf-8") as f:
            text = f.read()
        embeddings = create_dummy_embeddings(text)
        save_embeddings(txt_file.replace(".txt", "_embeddings.json"), embeddings)

    logger.info("All text files processed and embeddings saved!")


# === Run automatically if executed directly ===
if __name__ == "__main__":
    process_all_texts()
