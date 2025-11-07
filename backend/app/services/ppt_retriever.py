import os
import pickle
import numpy as np
import faiss
import re
from sentence_transformers import SentenceTransformer
from app.config.settings import EMBEDDINGS_DIR

class PPTRetriever:
    def __init__(self,
                 model_name='sentence-transformers/all-MiniLM-L6-v2',
                 index_path=None,
                 chunk_path=None):
        self.model = SentenceTransformer(model_name)
        self.index_path = index_path or os.path.join(EMBEDDINGS_DIR, 'faiss.index')
        self.chunk_path = chunk_path or os.path.join(EMBEDDINGS_DIR, 'faiss_chunks.pkl')
        self.index = None
        self.chunks = []
        self.load_index()

    def clean_text(self, text):
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def create_index(self, text_chunks):
        text_chunks = [self.clean_text(chunk) for chunk in text_chunks]
        embeddings = self.model.encode(text_chunks, convert_to_numpy=True, show_progress_bar=True)
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(np.array(embeddings, dtype='float32'))
        self.chunks = text_chunks
        self.save_index()

    def retrieve(self, query, top_k=3):
        if self.index is None:
            raise ValueError("FAISS index not loaded. Please upload or process a PPT first.")
        query_vec = self.model.encode([query], convert_to_numpy=True)
        D, I = self.index.search(np.array(query_vec, dtype='float32'), top_k)
        return [self.chunks[i] for i in I[0]]

    def save_index(self):
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.chunk_path, 'wb') as f:
            pickle.dump(self.chunks, f)

    def load_index(self):
        if os.path.exists(self.index_path) and os.path.exists(self.chunk_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.chunk_path, 'rb') as f:
                self.chunks = pickle.load(f)
