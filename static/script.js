// Client-side behavior integrated with backend API
console.log('static/script.js loaded');
const messages = document.getElementById('messages');
const messageInput = document.getElementById('messageInput');
const inputBar = document.getElementById('inputBar');
const sendBtn = document.getElementById('sendBtn');
const uploadBtn = document.getElementById('uploadBtn');
const fileInput = document.getElementById('fileInput');
const fileNameSpan = document.getElementById('fileName');
const deleteFileBtn = document.getElementById('deleteFileBtn');
const typingIndicator = document.getElementById('typingIndicator');
const embeddingsSelect = document.getElementById('embeddingsSelect');

let typingTimeout = null;
let currentEmbeddingsFile = ''; // basename of embeddings JSON to use with /api/chat

function appendMessage(text, who = 'bot') {
	const el = document.createElement('div');
	el.className = `message ${who}`;
	el.textContent = text;
	messages.appendChild(el);
	messages.scrollTop = messages.scrollHeight;
}

function showTyping() {
	typingIndicator.style.visibility = 'visible';
	typingIndicator.setAttribute('aria-hidden', 'false');
}

function hideTyping() {
	typingIndicator.style.visibility = 'hidden';
	typingIndicator.setAttribute('aria-hidden', 'true');
}

function setControlsDisabled(disabled) {
	messageInput.disabled = disabled;
	sendBtn.disabled = disabled;
	uploadBtn.disabled = disabled;
	deleteFileBtn.disabled = disabled || !fileInput.files.length;
}

// Fetch and populate embeddings dropdown with retries
async function loadEmbeddingsList(retries = 3, delayMs = 500) {
	let attempt = 0;
	while (attempt < retries) {
		try {
			const res = await fetch('/api/chat/embeddings-list');
			if (!res.ok) {
				// try to get response body for more info
				const text = await res.text().catch(() => '');
				throw new Error(`HTTP ${res.status} ${res.statusText} ${text}`);
			}
			const data = await res.json();
			const files = data.embeddings || [];
			embeddingsSelect.innerHTML = '<option value="ALL">All PPTs</option><option value="">Select PPT Embeddings...</option>';
			files.forEach(f => {
				const opt = document.createElement('option');
				opt.value = f;
				opt.textContent = f.replace('_embeddings.json', '');
				embeddingsSelect.appendChild(opt);
			});
			// If currentEmbeddingsFile is set, select it
			if (currentEmbeddingsFile) {
				embeddingsSelect.value = currentEmbeddingsFile;
			}
			return; // success
		} catch (err) {
			console.error('loadEmbeddingsList attempt', attempt + 1, err);
			attempt += 1;
			if (attempt < retries) {
				// small exponential backoff
				await new Promise(r => setTimeout(r, delayMs * attempt));
				continue;
			}
			// final failure: show a subtle UI message but don't spam the chat
			const notice = `Could not load embeddings list (${err.message}). You can still upload and then select from the dropdown.`;
			appendMessage(notice, 'bot');
			return;
		}
	}
}

messageInput.addEventListener('input', () => {
	showTyping();
	if (typingTimeout) clearTimeout(typingTimeout);
	typingTimeout = setTimeout(() => {
		hideTyping();
	}, 900);
});

// Upload handling: POST /api/upload/upload/ppt (expects 'file')
async function uploadPpt() {
	const file = fileInput.files[0];
	if (!file) return;
	if (!file.name.toLowerCase().endsWith('.pptx')) {
		appendMessage('Only .pptx files are allowed for upload.', 'bot');
		return;
	}

	const fd = new FormData();
	fd.append('file', file);
	// the backend accepts a generate_embeddings boolean; add it as a form field
	fd.append('generate_embeddings', 'true');

	try {
		setControlsDisabled(true);
		appendMessage(`Uploading ${file.name}...`, 'user');
		const res = await fetch('/api/upload/upload/ppt', { method: 'POST', body: fd });
		if (!res.ok) {
			const payload = await res.json().catch(() => ({}));
			const message = payload.detail || res.statusText || 'Upload failed';
			appendMessage(`Upload error: ${message}`, 'bot');
			return;
		}

		const data = await res.json();
		const embPath = data.embeddings_path || '';
		const embName = embPath ? embPath.split(/[\\/]/).pop() : '';
		if (embName) {
			currentEmbeddingsFile = embName;
			fileNameSpan.textContent = `${file.name} → ${embName}`;
			appendMessage(`Uploaded and processed. Embeddings: ${embName}`, 'bot');
			await loadEmbeddingsList();
			embeddingsSelect.value = embName;
		} else {
			fileNameSpan.textContent = file.name;
			appendMessage('Uploaded but no embeddings were generated.', 'bot');
		}
	} catch (err) {
		appendMessage(`Upload failed: ${err.message}`, 'bot');
	} finally {
		setControlsDisabled(false);
	}
}

// When user selects a different embeddings file
embeddingsSelect.addEventListener('change', () => {
  currentEmbeddingsFile = embeddingsSelect.value;
});

// Chat handling: GET /api/chat/chat/?query=...&embeddings_file=...
async function sendChatMessage(text) {
	if (!text) return;
	if (!currentEmbeddingsFile) {
		appendMessage('Please select a PPT embeddings file from the dropdown.', 'bot');
		return;
	}
	showTyping();
	setControlsDisabled(true);

	try {
	const params = new URLSearchParams({ query: text, embeddings_file: currentEmbeddingsFile });
	const res = await fetch(`/api/chat/?${params.toString()}`, { method: 'GET' });
		if (!res.ok) {
			const payload = await res.json().catch(() => ({}));
			const message = payload.detail || res.statusText || 'Chat request failed';
			appendMessage(`Chat error: ${message}`, 'bot');
			return;
		}

		const payload = await res.json();
		const answer = payload.answer || JSON.stringify(payload);
		appendMessage(answer, 'bot');
	} catch (err) {
		appendMessage(`Chat failed: ${err.message}`, 'bot');
	} finally {
		hideTyping();
		setControlsDisabled(false);
	}
}

inputBar.addEventListener('submit', (e) => {
	e.preventDefault();
	const text = messageInput.value.trim();
	const hasFile = fileInput.files.length > 0;
	if (!text && !hasFile) return;

	if (text) {
		appendMessage(text, 'user');
	}

	// If a file is selected, upload it first and then optionally send a message
	if (hasFile) {
		// Upload will set currentEmbeddingsFile when complete
		uploadPpt().then(() => {
			// If there was also text, send chat after upload
			if (text) sendChatMessage(text);
		});
	} else if (text) {
		// Just send the chat message
		sendChatMessage(text);
	}

	messageInput.value = '';
	hideTyping();
});

uploadBtn.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', () => {
	if (fileInput.files.length) {
		fileNameSpan.textContent = fileInput.files[0].name;
		deleteFileBtn.disabled = false;
	} else {
		fileNameSpan.textContent = '';
		deleteFileBtn.disabled = true;
	}
});

deleteFileBtn.addEventListener('click', () => {
	// Clear the file input and reset embeddings selection on the frontend
	fileInput.value = '';
	fileNameSpan.textContent = '';
	currentEmbeddingsFile = '';
	deleteFileBtn.disabled = true;
	appendMessage('Cleared selected file and embeddings selection.', 'user');
});

// Allow Enter to send
messageInput.addEventListener('keydown', (e) => {
	if (e.key === 'Enter' && !e.shiftKey) {
		e.preventDefault();
		inputBar.dispatchEvent(new Event('submit', { cancelable: true }));
	}
});

// On page load, fetch embeddings list
window.addEventListener('DOMContentLoaded', loadEmbeddingsList);

// Initial welcome message
appendMessage('Welcome! Upload a .pptx to generate embeddings, then ask questions. If you already have embeddings, you can enter the filename when prompted.', 'bot');
