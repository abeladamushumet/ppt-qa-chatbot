import os
import shutil
from fastapi import UploadFile
from datetime import datetime
from app.utils.logger import logger


# === Allowed File Extensions ===
ALLOWED_EXTENSIONS = {".ppt", ".pptx"}


def is_valid_ppt(filename: str) -> bool:
    """
    Check if the uploaded file has a valid PPT extension.
    """
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def save_uploaded_ppt(file: UploadFile, upload_dir: str) -> str:
    """
    Save an uploaded PowerPoint file to the raw_ppt directory.

    Args:
        file (UploadFile): Uploaded file object.
        upload_dir (str): Directory to save the file.

    Returns:
        str: Path of the saved file.
    """
    try:
        if not is_valid_ppt(file.filename):
            raise ValueError(f"Invalid file type: {file.filename}")

        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)

        # Save file to destination
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f" File saved successfully: {file.filename}")
        return file_path

    except Exception as e:
        logger.error(f" Failed to save file {file.filename}: {e}")
        raise


def get_file_info(file_path: str) -> dict:
    """
    Return metadata info for a saved file.
    """
    try:
        stats = os.stat(file_path)
        file_info = {
            "filename": os.path.basename(file_path),
            "size_kb": round(stats.st_size / 1024, 2),
            "created_at": datetime.fromtimestamp(stats.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
        }
        logger.info(f" File info retrieved for {file_path}")
        return file_info

    except Exception as e:
        logger.error(f"Failed to get file info for {file_path}: {e}")
        return {}
