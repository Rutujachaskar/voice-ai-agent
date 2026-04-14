# 🎙️ VoiceAgent — Voice-Controlled Local AI Agent

> Mem0 AI/ML & Generative AI Developer Internship Assignment

A voice-controlled AI agent that accepts audio input, classifies user intent using an LLM, executes local tools, and displays the full pipeline in a clean Streamlit UI.

---

## 🏗️ Architecture

```
Audio Input (mic/upload/text)
        │
        ▼
   STT — Groq Whisper API (whisper-large-v3)
        │
        ▼
  Intent Classification — Groq LLM (LLaMA 3)
        │
        ├── create_file  → Write text/markdown file to output/
        ├── write_code   → Generate & save code to output/
        ├── summarize    → Summarize provided text
        └── general_chat → Conversational response
        │
        ▼
   Streamlit UI — displays all 4 pipeline steps
```

---

## 🤖 Models Used

### Speech-to-Text (STT)

* **Whisper Large v3 (via Groq API)**

  * Fast (<1s latency)
  * High accuracy
  * No GPU required

### LLM (Intent Classification)

* **LLaMA 3 8B** → Fast (default)
* **LLaMA 3 70B** → More accurate (optional)

---

## 📁 Files

| File        | Purpose                                                          |
| ----------- | ---------------------------------------------------------------- |
| `app.py`    | Streamlit UI — orchestrates the full pipeline                    |
| `stt.py`    | Speech-to-text via Groq Whisper API                              |
| `intent.py` | LLM intent classifier — returns structured JSON                  |
| `tools.py`  | Tool executor — file creation, code writing, summarization, chat |
| `memory.py` | Session memory — rolling action history injected as LLM context  |

---

## ⚡ Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/voice-agent
cd voice-agent
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up API key

```bash
cp .env.example .env
# Add your GROQ_API_KEY
```

Get a free key: https://console.groq.com

### 4. Run the app

```bash
streamlit run app.py
```

Open: http://localhost:8501

---

## 🎯 Supported Intents

| Intent         | Example command                                    |
| -------------- | -------------------------------------------------- |
| `create_file`  | "Create a README file explaining this project"     |
| `write_code`   | "Create a Python file with a bubble sort function" |
| `summarize`    | "Summarize this: AI is transforming industries..." |
| `general_chat` | "What is machine learning?"                        |

---

## 📸 Example Output

### Input

"Create a Python file with a bubble sort function"

### Output (UI)

* Transcription: Create a Python file with a bubble sort function
* Intent: write_code (high confidence)
* Action: Code written to `bubble_sort.py`
* Result: File saved in `output/` folder

---

## ✅ Features

### Required

* [x] Audio input via microphone
* [x] Audio input via file upload
* [x] Speech-to-text transcription
* [x] Intent classification using LLM
* [x] File operations (restricted to `output/`)
* [x] UI shows full pipeline (transcription → intent → action → result)

### Bonus

* [x] **Human-in-the-Loop** confirmation before file/code execution
* [x] **Session Memory** for contextual understanding
* [x] **Graceful Error Handling**
* [x] **Text Input Fallback**
* [x] **Model Selection (LLaMA 3 variants)**

---

## 🧠 Human-in-the-Loop

Before executing file or code operations, the system asks for user confirmation.

This prevents:

* Accidental file creation
* Unwanted code execution
* Unsafe operations

---

## ⚠️ Error Handling

The system gracefully handles:

* Invalid or unclear audio input
* API failures (with fallback)
* Missing parameters
* Unsupported intents

All errors are displayed clearly in the UI.

---

## 🔧 Hardware Notes

### Why Groq API for STT?

* No GPU required
* Whisper-large-v3 quality
* <1 second latency
* Free tier available

Local fallback available using `openai-whisper`.

---

### Why Groq for LLM?

* Very fast inference
* Free tier
* Reliable structured JSON output
* No local setup needed

---

## 🧪 Test Commands

```
Create a Python file with a bubble sort function
Write a JavaScript function to reverse a string
Create a README file for a todo app
Summarize this: Artificial Intelligence is transforming industries...
What is machine learning?
```

---

## 🗂️ Project Structure

```
voice-agent/
├── app.py
├── stt.py
├── intent.py
├── tools.py
├── memory.py
├── requirements.txt
├── .env.example
├── output/
└── README.md
```

---

## 📦 Dependencies

* streamlit
* groq
* python-dotenv

---

## 🚀 Future Improvements

* Support compound commands (e.g., summarize + save)
* Add voice output (Text-to-Speech)
* Integrate local LLM (Ollama)
* Persistent memory across sessions
* File editing support

---

## 🔗 Links

* **GitHub**: [Add your repo link]
* **Demo Video**: [Add YouTube unlisted link]
* **Article**: [Add Medium/Dev.to link]
