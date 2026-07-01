#  Video QA Chatbot

Ask questions about any YouTube video and get answers grounded in that respective video only ,
 with timestamps — by Whisper (speech-to-text),
Qdrant (vector search), a reranker, and Groq's LLaMA 3.3 for the final answer.

---

## How it works (pipeline overview)

```
YouTube URL
   │
   ▼
[1] Download the audio only (yt-dlp)
   │
   ▼
[2] Convert to 16kHz mono WAV (ffmpeg)
   │
   ▼
[3] Transcribe to text with timestamps (whisper tiny)
   │
   ▼
[4] Split transcript into overlapping chunks, each tagged
    with the timestamp range it covers (langchain text splitter) (RecursiveCharacterTextSplitter)
   │
   ▼
[5] Embed each chunk (BAAI/bge-m3 sentence-transformer)
   │
   ▼
[6] Store chunks + embeddings in Qdrant (local vector database)
   
    │
    ▼

When you ask a question:

Question
   │
   ▼
[7] Embed the question, retrieve the 20 most similar chunks
    from Qdrant 
   │
   ▼
[8] Rerank those 20 chunks with a reranker
    (BAAI/bge-reranker-v2-m3), keep the top 5
   │
   ▼
[9] Send the top 5 chunks + question to Groq's LLaMA 3.3,
    instructed to answer only from that context, with timestamps
   │
   ▼
Answer, shown in the Streamlit UI
```

---

## Project structure

| File | Purpose |
|---|---|
| `main.py` | **Run this one.** Checks requirements are installed, installs if missing, launches the app. |
| `app.py` | The Streamlit UI — text inputs, buttons, and wiring to the pipeline. |
| `config.py` | All settings in one place: paths, model names, chunk size, top-K values. Change behavior here. |
| `models.py` | Loads Whisper, the embedding model, and the reranker only once. |
| `db.py` | Shared Qdrant client (local, file-backed database at `./qdrant_db`). |
| `ingest.py` | The download → transcribe → chunk → embed → store pipeline. Exposes `process_video(url)`. |
| `retrieval.py` | The retrieve → rerank pipeline. Exposes `ask_question(query, video_id)`. |
| `answer.py` | Builds the prompt and calls the Groq LLM. Exposes `generate_answer(query, chunks)`. |
| `requirements.txt` | Python package list. |
| `app.log` | Created automatically when you run the app — a plain-text log of what happened. |
| `data/` | Created automatically — stores downloaded audio, transcripts, and chunk JSON files per video. |
| `qdrant_db/` | Created automatically — the local vector database on disk. |

---

## Installation


1. Clone the repository
git clone https://github.com/your-username/vqacht.git
cd vqacht


2. Create virtual environment (recommended)
python -m venv .venv
# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate


3. Install dependencies

Don't need to do this manually — `main.py` does it for you. 

To do it yourself

```powershell
pip install -r requirements.txt
```


4. Set  Groq API key
The app needs a Groq API key to generate answers (get one free at
[console.groq.com](https://console.groq.com)). Set it as an environment
variable before running:

```powershell
$env:GROQ_API_KEY = "your-key-here"
```

5. Run the App
streamlit run app.py

Then open:

http://localhost:8501
