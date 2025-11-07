import os
import pytest
from app.services.ppt_loader import process_ppt
from app.config.settings import RAW_PPT_DIR, EXTRACTED_TEXT_DIR

# Test PPT file (make sure this exists in data/raw_ppt/ for testing)
TEST_PPT_FILE = os.path.join(RAW_PPT_DIR, "Chapter 1.pptx")


def test_process_ppt_creates_text_file():
    """
    Test that process_ppt extracts text and saves to a .txt file.
    """
    # Run text extraction
    txt_path = process_ppt(TEST_PPT_FILE)

    # Check the file was created
    assert os.path.exists(txt_path), f"Text file not created: {txt_path}"

    # Check that it is a non-empty file
    with open(txt_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert len(content.strip()) > 0, "Extracted text is empty"

    # Check the filename is in EXTRACTED_TEXT_DIR
    assert txt_path.startswith(EXTRACTED_TEXT_DIR), "Text file not in correct directory"
