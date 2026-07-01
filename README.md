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

## Setup

### 1. Install Python dependencies

Don't need to do this manually — `main.py` does it for you. 

To do it yourself

```powershell
pip install -r requirements.txt
```

### 2. Set your Groq API key

The app needs a Groq API key to generate answers (get one free at
[console.groq.com](https://console.groq.com)). Set it as an environment
variable before running:

```powershell
$env:GROQ_API_KEY = "your-key-here"
```

This only lasts for the current PowerShell session. To set it permanently,
add it through Windows' Environment Variables settings, or use a `.env`
file with a package like `python-dotenv` if you'd prefer.

### 3. (Optional) YouTube bot-check workaround

Some videos trigger YouTube's "Sign in to confirm you're not a bot" error.
If you hit this, open `config.py` and set:

```python
YTDLP_COOKIES_BROWSER = "chrome"   # or "firefox", "edge", etc.
```

This makes `yt-dlp` borrow cookies from your logged-in browser session.
**Close that browser fully before running the app**, or its cookie
database will be locked and the read will fail.

---

## Running on any system

There are two ways to get this running on a machine you've never touched
before — pick based on how much control you want.

### Option A — Direct (Python + pip)

Works on Windows, Mac, or Linux, as long as Python 3.10+ is installed.

```bash
python main.py
```

`main.py` now checks for **two** kinds of dependencies before launching:

1. **`ffmpeg`** — a system-level binary, not something pip can install.
   If it's missing, `main.py` detects your OS and prints the right
   install command (`choco install ffmpeg` on Windows, `brew install
   ffmpeg` on Mac, `apt install ffmpeg` on Linux), then exits so you can
   install it and re-run.
2. **Python packages** — everything in `requirements.txt`. Installed
   automatically via pip if anything's missing.

This is the simplest option, but it does modify whatever Python
environment you run it in (or, better, whatever virtual environment
you've activated first).

### Option B — Docker (guaranteed identical everywhere)

If you want the app to run **exactly the same way** on any machine —
no manual ffmpeg install, no Python version mismatches, no "works on my
machine" — build it into a Docker image instead. This is the standard
answer to "how do I make sure this installs on any system."

Requires only [Docker](https://www.docker.com/products/docker-desktop/)
to be installed — nothing else.

```bash
# Build the image (only needs to be done once, or after code changes)
docker build -t video-qa-chatbot .

# Run it, passing your Groq API key in at runtime
docker run -e GROQ_API_KEY=your-key-here -p 8501:8501 video-qa-chatbot
```

Then open `http://localhost:8501` in your browser.

**Why this is more portable than Option A:** the `Dockerfile` bundles a
specific Python version, installs `ffmpeg` at the OS level inside the
container, and installs all pip packages inside that same container —
so the exact same image runs identically on Windows, Mac, Linux, or a
cloud server, regardless of what's already installed on the host machine.

---

## Running the app (Option A quick reference)

From inside the `vqacht` folder (or pointing at it from anywhere):

```powershell
python main.py
```

**First run will be slow** — Whisper, the embedding model, and the
reranker all need to download their weights (several GB total) the first
time they're used. Subsequent runs are much faster since they're cached
locally by Hugging Face.

### Using the app

1. Paste a YouTube URL into the **YouTube URL** field and click
   **▶ Process Video**. Wait for the "Processed ..." success message —
   this step downloads, transcribes, and indexes the video, so it can
   take a few minutes depending on video length.
2. Once processed, type a question into **Ask a question** and click
   **💬 Ask**. The answer will include timestamps referencing where in
   the video the information came from.
3. You can process a different video at any point — questions are
   always scoped to whichever video was processed most recently.

---

## Logging

Every run writes to both the terminal and a file called `app.log` in the
project folder, showing progress like:

```
2026-07-01 11:42:03,112 [INFO] ingest: Downloading audio for https://youtube.com/watch?v=...
2026-07-01 11:42:08,558 [INFO] ingest: Transcribing dQw4w9WgXcQ
2026-07-01 11:42:15,203 [INFO] retrieval: Question: 'what is a CT scan' (video_id='dQw4w9WgXcQ')
```

The log file **appends** across runs rather than overwriting, so it'll
keep growing. To reset it, just delete `app.log` — it'll be recreated
automatically next run.

---

## Troubleshooting

**"ffmpeg was not found on your system PATH"**
Install ffmpeg at the OS level (not with pip) — see the OS-specific
command `main.py` prints, or use the Docker option instead, which
includes ffmpeg automatically.

**"Sign in to confirm you're not a bot" error when processing a video**
See the cookies workaround in Setup step 3 above.

**App crashes immediately with no error in the terminal**
Usually a memory issue — Whisper + the embedding model + the reranker
all loading into RAM at once can be heavy on machines with limited memory.
Watch Task Manager's memory graph while the app starts up.

**`FileNotFoundError` for `requirements.txt`**
Make sure `requirements.txt` lives in the same folder as `main.py`
(inside `vqacht`), not the parent folder.

**Questions return "I could not find this in the video"**
Either the video's audio didn't contain relevant speech to your question,
or Whisper's transcription missed it (the `tiny` model trades some
accuracy for speed — try `base` or `small` in `config.py` if this
happens often).

**`RuntimeError: GROQ_API_KEY is not set`**
Set the environment variable as described in Setup step 2, then restart
the app (environment variables set with `$env:` only apply to that
PowerShell session).