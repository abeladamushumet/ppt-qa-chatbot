"""Answer generator helpers and a tiny simple RAG implementation."""
import re
import difflib
import os
import requests
from app.utils.logger import logger
from app.services.vector_store import load_embeddings
from app.config.settings import GEMINI_API_KEY, CHAT_MODEL


def _clean_text(text: str) -> str:
    """Remove non-printable/control characters and collapse whitespace."""
    if not text:
        return ""
    # Replace non-printable characters with a space
    cleaned = ''.join(ch if ch.isprintable() else ' ' for ch in text)
    # Collapse whitespace (spaces, newlines, tabs, vertical tabs, etc.)
    cleaned = re.sub(r"\s+", ' ', cleaned).strip()
    return cleaned


def _find_best_sentence(query: str, text: str, max_len: int = 300) -> str:
    """Find the sentence most similar to the query using fuzzy matching."""
    if not text:
        return ""

    sentences = re.split(r'(?<=[\.\?!])\s+', text)
    qlow = query.lower()
    # First, try exact or substring match
    for s in sentences:
        if qlow in s.lower():
            s = s.strip()
            return s if len(s) <= max_len else s[:max_len].rstrip() + '...'

    # Fuzzy match: find the sentence with highest similarity
    best = ""
    best_score = 0.0
    for s in sentences:
        score = difflib.SequenceMatcher(None, qlow, s.lower()).ratio()
        if score > best_score:
            best_score = score
            best = s.strip()

    if best_score > 0.3 and best:
        return best if len(best) <= max_len else best[:max_len].rstrip() + '...'

    # Fallback: snippet around first word match
    m = re.search(re.escape(query.split()[0]), text, flags=re.IGNORECASE) if query.split() else None
    if m:
        start = max(0, m.start() - 100)
        end = min(len(text), m.end() + 100)
        snippet = text[start:end].strip()
        return snippet if len(snippet) <= max_len else snippet[:max_len].rstrip() + '...'

    return text[:max_len].rstrip() + ('...' if len(text) > max_len else '')


def simple_rag(query: str, embeddings_file: str) -> str:
    """Search embeddings JSON for text and return a concise snippet relevant to query."""
    embeddings = load_embeddings(embeddings_file)
    if not embeddings:
        logger.warning("No embeddings found; cannot answer query.")
        return "No data available to answer your query."

    if isinstance(embeddings, dict):
        raw_text = embeddings.get('text', '')
    else:
        raw_text = str(embeddings)

    cleaned = _clean_text(raw_text)
    if not cleaned:
        logger.warning(f"Embeddings file '{embeddings_file}' contains no text after cleaning.")
        return "No usable text found in embeddings."

    snippet = _find_best_sentence(query, cleaned)
    if snippet:
        answer = f"Found relevant info: {snippet}"
    else:
        answer = "No relevant info found in embeddings."

    logger.info(f"Query processed: {query}")
    return answer


def search_all_embeddings(query: str):
    """Search across all embeddings files and return the best snippet and its source filename."""
    best_score = 0.0
    best_snippet = ""
    best_file = None

    from app.config.settings import EMBEDDINGS_DIR

    for fname in os.listdir(EMBEDDINGS_DIR):
        if not fname.endswith('_embeddings.json'):
            continue
        try:
            emb = load_embeddings(fname)
            if isinstance(emb, dict):
                raw = emb.get('text', '')
            else:
                raw = str(emb)
            cleaned = _clean_text(raw)
            if not cleaned:
                continue
            snippet = _find_best_sentence(query, cleaned)
            # compute a similarity score between query and snippet
            score = difflib.SequenceMatcher(None, query.lower(), snippet.lower()).ratio() if snippet else 0.0
            if score > best_score:
                best_score = score
                best_snippet = snippet
                best_file = fname
        except Exception as e:
            logger.error(f"Error searching embeddings file {fname}: {e}")
            continue

    if best_snippet:
        return (f"Found relevant info (from {best_file}): {best_snippet}", best_file)
    return ("No relevant info found across embeddings.", None)


def gemini_generate_answer(query: str, context: str = "") -> str:
    """Call Gemini API to generate an answer given a query and optional context."""
    if not GEMINI_API_KEY:
        return "Gemini API key not set."

    # Use CHAT_MODEL from settings (should be like 'models/text-bison-001' or 'models/gemini-1.0')
    model = CHAT_MODEL or 'models/gemini-1.0'
    url_text = f"https://generativelanguage.googleapis.com/v1/{model}:generateText"
    url_content = f"https://generativelanguage.googleapis.com/v1/{model}:generateContent"

    headers = {"Content-Type": "application/json"}
    prompt = query if not context else f"{query}\nContext: {context}"
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    params = {"key": GEMINI_API_KEY}

    try:
        # Try generateText first, then generateContent
        resp = requests.post(url_text, headers=headers, params=params, json=data, timeout=15)
        if resp.status_code == 404:
            resp = requests.post(url_content, headers=headers, params=params, json=data, timeout=15)

        if resp.status_code == 404:
            return "[Gemini API error: 404 Not Found. Check your API key and model name — try listing available models.]"

        resp.raise_for_status()
        result = resp.json()

        # Common response shapes
        if isinstance(result, dict):
            if 'candidates' in result and result['candidates']:
                return result['candidates'][0]['content']['parts'][0]['text']
            if 'outputs' in result and result['outputs']:
                out = result['outputs'][0]
                # try to find text in outputs
                if isinstance(out, dict):
                    if 'content' in out and isinstance(out['content'], list):
                        for c in out['content']:
                            if isinstance(c, dict) and 'text' in c:
                                return c['text']
        # Fallback: return a short JSON summary
        text_preview = str(result)
        return text_preview[:1000]

    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return f"[Gemini API error: {e}]"


def generate_answer(query: str, embeddings_file: str = None, use_gemini: bool = True) -> str:
    """Generate an answer; use Gemini if enabled, else use RAG/simple_rag."""
    if not query:
        return "Please provide a valid question."

    # If Gemini is enabled and key is set, use Gemini with context from embeddings
    if use_gemini and GEMINI_API_KEY:
        # Use RAG to get context (best snippet)
        context = ""
        if not embeddings_file:
            try:
                context, _ = search_all_embeddings(query)
            except Exception as e:
                logger.error(f"search_all_embeddings failed: {e}")
        else:
            try:
                context = simple_rag(query, embeddings_file)
            except Exception as e:
                logger.error(f"simple_rag failed for '{embeddings_file}': {e}")
        return gemini_generate_answer(query, context)

    # Fallback: use RAG only
    if not embeddings_file:
        try:
            answer, src = search_all_embeddings(query)
            return answer
        except Exception as e:
            logger.error(f"search_all_embeddings failed: {e}")

    if embeddings_file:
        try:
            return simple_rag(query, embeddings_file)
        except Exception as e:
            logger.error(f"simple_rag failed for '{embeddings_file}': {e}")

    return f"Answer generated for query: '{query}'"
