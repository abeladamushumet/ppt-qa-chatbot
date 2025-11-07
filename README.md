<<<<<<< HEAD
# RAG PPT Chatbot

A powerful Retrieval-Augmented Generation (RAG) chatbot that enables you to ask questions and get intelligent answers based on the content of your PowerPoint presentations.

## Features

- **Multi-PPT Support**: Upload and process multiple PowerPoint presentations simultaneously
- **Smart Text Extraction**: Automatically extracts text from slides, tables, and shapes
- **Vector-Based Search**: Uses FAISS for efficient semantic search across presentation content
 - **Intelligent Responses**: Powered by the Gemini API (Google) models with context-aware answers
- **Modern Web UI**: Beautiful, responsive interface for easy interaction
- **Fast API**: Built with FastAPI for high performance and async operations

##  Requirements

- Python 
- Gemini API key (or configure HuggingFace models as alternative)
- 4GB+ RAM recommended
- Modern web browser

##  Installation

###  Local Installation

1. **Clone the repository**
```bash
git clone https://github.com/abeladamushumet/ppt-qa-chatbot.git
cd ppt-qa-chatbot
```

2. **Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r backend/requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY (and optionally GEMINI_MODEL)
```

5. **Run the backend**
```bash
cd backend
python -m app.main
```

6. **Open the frontend**
Open `frontend/index.html` in your web browser or serve it with a local web server:
```bash
# Using Python's built-in server
cd frontend
python -m http.server 3000
```

##  Usage

### 1. Upload PowerPoint Files

- Drag and drop PPTX files onto the upload area
- Or click to browse and select files
- Maximum file size: 100MB per file
- Supported formats: .pptx, .ppt

### 2. Wait for Processing

- Files are automatically processed in the background
- Text extraction and vectorization happen automatically
- Progress is shown in real-time

### 3. Ask Questions

- Type your question in the chat interface
- Get intelligent answers based on your presentations
- The system retrieves relevant context from all uploaded files

##  Architecture

```
┌─────────────┐
│   Frontend  │  HTML/CSS/JS
│  (Browser)  │
└──────┬──────┘
       │
       ↓
┌─────────────────┐
│   FastAPI       │  REST API
│   Backend       │
└─────┬───────────┘
      │
      ├───→ PPT Loader ──→ Extract Text
      │
      ├───→ Vector Store ──→ FAISS Index
      │
      └───→ Generator ──→ Gemini API
```

### Components

- **Backend**: FastAPI application with async support
- **PPT Loader**: Extracts text from PowerPoint files using python-pptx
- **Vector Store**: Manages FAISS-based semantic search
- **Generator**: Handles RAG-based response generation using the Gemini API
- **Frontend**: Modern web interface for user interaction

## Project Structure

```
ppt-qa-chatbot/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # Application entry point
│   │   ├── routes/         # API endpoints
│   │   ├── services/       # Core logic
│   │   ├── utils/          # Helper functions
│   │   └── config/         # Configuration
│   ├── tests/              # Unit tests
│   └── requirements.txt    # Dependencies
├── static/                # Web interface
│   ├── index.html         # Main page
│   ├── style.css          # Styling
│   ├── script.js          # Frontend logic
├── data/                   # Data storage
│   ├── raw_ppt/           # Uploaded files
│   ├── extracted_texts/   # Processed text
│   └── embeddings/        # Vector indexes
└── README.md             # This file
```

##  Configuration

Key configuration options in `.env`:

- `GEMINI_API_KEY`: Your Gemini API key (required)
- `GEMINI_MODEL`: Gemini model for chat/generation (example: `gemini-pro`)
- `EMBEDDING_MODEL`: Model for embeddings (example: `textembedding-gecko-001`)
- `TOP_K_RESULTS`: Number of context chunks to retrieve (default: 3)
- `MAX_TOKENS`: Maximum response length (default: 1000)
- `TEMPERATURE`: Response creativity (default: 0.7)

Notes:
- This README assumes use of the Gemini API for text generation and embeddings. If you prefer another provider (e.g., OpenAI), update the `.env` variables and generator implementation accordingly.

##  Testing

Run tests with pytest:
```bash
cd backend
pytest tests/
```
=======
# ppt-qa-chatbot
An AI chatbot that extracts text and context from PowerPoint presentations and answers questions using a Retrieval-Augmented Generation (RAG) pipeline.
>>>>>>> aa6a319b899225ec444f39f1b43bd33bb9a2dae0
