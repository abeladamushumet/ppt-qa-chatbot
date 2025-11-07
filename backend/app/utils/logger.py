import logging
import os

# === Log Directory ===
LOG_DIR = os.path.join(os.path.dirname(__file__), "../../..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# === Log File Path ===
LOG_FILE = os.path.join(LOG_DIR, "app.log")

# === Logging Configuration ===
logging.basicConfig(
    level=logging.INFO,  # INFO (production) | DEBUG (development)
    format="%(asctime)s [%(levelname)s] - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),  # Save logs to file
        logging.StreamHandler()         # Also show in console
    ]
)

# === Logger Object ===
logger = logging.getLogger("ppt-qa-chatbot")

# === Example Startup Log ===
logger.info("Logger initialized successfully.")
