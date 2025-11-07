import os
import pytest
from app.services.vector_store import process_text_for_embeddings
from app.config.settings import EXTRACTED_TEXT_DIR, EMBEDDINGS_DIR

# Sample text file to test
TEST_TEXT_FILE = os.path.join(EXTRACTED_TEXT_DIR, "Chapter 1.txt")
TEST_OUTPUT_FILE = os.path.join(EMBEDDINGS_DIR, "Chapter_1_test_embeddings.json")


def test_process_text_for_embeddings_creates_file():
    """
    Test that process_text_for_embeddings generates a JSON embeddings file.
    """
    # Read the extracted text
    with open(TEST_TEXT_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    # Process embeddings
    output_path = process_text_for_embeddings(text, "Chapter_1_test")

    # Check the file was created
    assert os.path.exists(output_path), f"Embeddings file not created: {output_path}"

    # Check that file is non-empty
    assert os.path.getsize(output_path) > 0, "Embeddings file is empty"

    # Clean up test embeddings
    os.remove(output_path)
