# Building a Voice-Controlled AI Agent with Whisper + LLMs

*A step-by-step walkthrough of my Mem0 internship assignment — architecture, model choices, and challenges faced.*

---

## What I Built

A voice-controlled local AI agent that:
1. Accepts audio via microphone or file upload
2. Transcribes speech to text using Whisper
3. Classifies user intent using a Large Language Model
4. Executes local tools (file creation, code writing, summarization, chat)
5. Displays the full pipeline in a Streamlit UI

---

## Architecture

```
Audio → STT (Groq Whisper) → Intent (LLaMA 3) → Tool Executor → Streamlit UI
```

I chose a clean 4-module separation:

- **stt.py** — handles transcription, provider-agnostic
- **intent.py** — LLM classification with structured JSON output
- **tools.py** — tool execution, safety-sandboxed to output/
- **memory.py** — session-level rolling memory

---

## Model Choices

### Speech-to-Text: Groq Whisper (whisper-large-v3)

I initially tried local Whisper on CPU. On my machine, whisper-base took 10–15 seconds per clip and had noticeably worse accuracy. Whisper-large-v3 would require a GPU I don't have.

Groq offers whisper-large-v3 via API with < 1 second latency and a generous free tier. Same model weights, just faster. This was an easy choice.

### LLM: LLaMA 3 via Groq

For intent classification, I needed:
- Reliable JSON output (for parsing)
- Fast inference (for demo responsiveness)
- Free tier availability

LLaMA 3 8B on Groq delivers ~600 tokens/sec. I used `response_format: {"type": "json_object"}` to enforce structured output, which made parsing reliable.

I also tested Mixtral 8x7B — slightly more accurate on edge cases but slower. For the demo, LLaMA 3 8B is the sweet spot.

---

## Intent Classification Design

The key challenge was getting reliable structured output from the LLM. My system prompt explicitly:

1. Defines exactly 4 intents with examples
2. Requires the LLM to generate actual content (not just classify)
3. Enforces JSON-only output (no markdown fences)
4. Specifies every field in the schema

This "generate-while-classifying" approach means one LLM call handles both classification AND content generation, keeping latency low.

---

## Safety Design

All file operations are restricted to an `output/` folder:
- `Path(filename).name` strips any directory traversal attempts
- Regex sanitizes filenames before writing
- The output/ directory is clearly separated from the codebase

---

## Challenges

### 1. JSON Parsing Reliability

LLMs sometimes add markdown fences or preamble despite being told not to. I added a multi-layer parser:
- Strip backtick fences with regex
- Try `json.loads()` directly
- Fall back to regex-extract the JSON object
- Default to `general_chat` if all else fails

### 2. Audio Format Compatibility

Streamlit's `st.audio_input()` returns WAV. Uploaded files can be MP3/M4A. Groq Whisper handles all formats natively — no conversion needed.

### 3. Session Memory Without a Database

I implemented a simple in-memory rolling history that injects recent actions as LLM context. This gives the agent basic multi-turn awareness without needing a vector database.

---

## What I'd Improve

- **Persistent memory** using Mem0 or a local vector DB (ChromaDB)
- **Ollama support** for fully offline operation on capable hardware
- **Compound commands** — parsing "summarize AND save to file" as two intents
- **Streaming output** — stream LLM tokens to the UI for faster perceived response

---

## Key Takeaway

The hardest part wasn't the code — it was designing the prompt. Getting the LLM to reliably return structured JSON that includes both the classification AND generated content in one call took several iterations. Once that was solid, everything else fell into place.

---

*Built for the Mem0 AI/ML & Generative AI Developer Internship Assignment.*
