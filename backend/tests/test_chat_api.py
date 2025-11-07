import sys
import os
from fastapi.testclient import TestClient
from unittest.mock import patch

# Add backend/app to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "app"))

from app.main import app  # FastAPI instance

# Initialize test client
client = TestClient(app)

# -------------------------------
# Test root endpoint
# -------------------------------
def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "RAG PPT Chatbot API is running"}

# -------------------------------
# Test /chat endpoint with mock
# -------------------------------
@patch("app.routes.chat_routes.generate_answer")  # Mock the service function
def test_chat_endpoint_mock(mock_generate):
    # Define mock return value
    mock_generate.return_value = "This is a mocked summary of Chapter 1."

    response = client.get(
        "/chat/",
        params={
            "query": "Summarize Chapter 1",
            "embeddings_file": "dummy.json"  # file does not need to exist
        }
    )

    assert response.status_code == 200

    data = response.json()
    assert "query" in data
    assert "answer" in data
    assert data["answer"] == "This is a mocked summary of Chapter 1."
