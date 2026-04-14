# 🎙 Voice-Controlled AI Agent (Mem0 Assignment)

## 📌 Overview

This project is a Voice-Controlled AI Agent that processes user commands through speech or text and performs intelligent actions like code generation, file creation, summarization, and chat responses.

Pipeline:
Audio Input → Speech-to-Text → Intent Classification → Tool Execution → Output

---

## 🚀 Features

* 🎤 Speech-to-Text using Groq Whisper API
* 🧠 Intent classification using Groq LLM
* ⚙️ Tool execution (code generation, file creation, summarization)
* 📁 Output file generation
* 🔒 Human-in-the-loop confirmation for safety
* 🧾 Session memory tracking

---

## 🏗 Architecture

User Input (Audio/Text)
↓
Speech-to-Text (Groq Whisper)
↓
Intent Classification (Groq LLM)
↓
Tool Execution Layer
↓
Output (UI + File System)

---

## 🛠 Tech Stack

* Streamlit (Frontend UI)
* Groq API (LLM + Whisper)
* Python
* File System for storage

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/Rutujachaskar/voice-ai-agent.git
cd voice-ai-agent
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add environment variables

Create a `.env` file:

```env
GROQ_API_KEY=your_api_key_here
```

### 4. Run the app

```bash
streamlit run app.py
```

---

## 🎤 Usage

### Input methods:

* Record audio 🎤
* Upload audio file 📎
* Type command ✏️

### Example commands:

* "Write a Python bubble sort program"
* "Create a text file with hello world"
* "What is machine learning?"

---

## ⚠️ Limitations & Workarounds

* Background noise may affect speech recognition
* Microphone input may not work in deployed environments
* Uses Groq API (internet required)

---

## 📁 Output

Generated files are stored in:

```bash
/output
```

---

## 🎥 Demo

(Add your YouTube demo link here)

---

## 📝 Author

Rutuja Chaskar
