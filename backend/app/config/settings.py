import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# === API KEYS ===
# Gemini API Key for Google Generative AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Model configuration from environment
CHAT_MODEL = os.getenv("CHAT_MODEL")  # expected to be a full model resource like 'models/text-bison-001' or 'models/gemini-1.0'
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

# === PATH CONFIGURATIONS ===
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))

DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_PPT_DIR = os.path.join(DATA_DIR, "raw_ppt")
EXTRACTED_TEXT_DIR = os.path.join(DATA_DIR, "extracted_texts")
EMBEDDINGS_DIR = os.path.join(DATA_DIR, "embeddings")

# === SERVER CONFIG ===
APP_NAME = "RAG PPT Chatbot"
HOST = "0.0.0.0"
PORT = 8000
DEBUG = True

# === VALIDATIONS ===
if not GEMINI_API_KEY:
    # Don't raise here to allow using other API providers in future; log at runtime if missing
    print("Warning: GEMINI_API_KEY is not set. Gemini-based features will be disabled until a key is provided.")

# === PRINT PATHS FOR DEBUGGING ===
if DEBUG:
    print(f" Configuration Loaded:")
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"DATA_DIR: {DATA_DIR}")
    print(f"RAW_PPT_DIR: {RAW_PPT_DIR}")
    print(f"EXTRACTED_TEXT_DIR: {EXTRACTED_TEXT_DIR}")
    print(f"EMBEDDINGS_DIR: {EMBEDDINGS_DIR}")
