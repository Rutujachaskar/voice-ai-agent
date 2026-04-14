


# """
# app.py — Voice-Controlled Local AI Agent
# Mem0 Internship Assignment — Rutuja
# """

# import os
# import tempfile
# from pathlib import Path

# import streamlit as st
# from dotenv import load_dotenv

# load_dotenv()

# from stt import transcribe_audio
# from intent import classify_intent
# from tools import execute_tool
# from memory import SessionMemory

# # ── CONFIG ─────────────────────────────────────────────────────────────
# st.set_page_config(
#     page_title="VoiceAgent · Mem0",
#     page_icon="🎙️",
#     layout="wide"
# )

# # ── SESSION STATE ──────────────────────────────────────────────────────
# if "memory" not in st.session_state:
#     st.session_state.memory = SessionMemory()
# if "history" not in st.session_state:
#     st.session_state.history = []
# if "pending" not in st.session_state:
#     st.session_state.pending = None
# if "last_result" not in st.session_state:
#     st.session_state.last_result = None

# OUTPUT_DIR = Path("output")
# OUTPUT_DIR.mkdir(exist_ok=True)

# # ── SIDEBAR ────────────────────────────────────────────────────────────
# with st.sidebar:
#     st.markdown("## ⚙ Settings")

#     llm_model = st.selectbox(
#         "LLM Model",
#         ["llama-3.1-8b-instant", "llama-3.3-70b-versatile"]
#     )

#     require_confirm = st.toggle("Human-in-the-Loop", value=True)

#     if st.button("🗑 Clear History"):
#         st.session_state.history.clear()
#         st.session_state.memory.clear()
#         st.session_state.last_result = None
#         st.rerun()

# # ── MAIN UI ────────────────────────────────────────────────────────────
# st.title("🎙 VoiceAgent")
# st.caption("Voice-controlled AI agent · Mem0 Internship Assignment")

# tab_input, tab_output, tab_files = st.tabs(
#     ["🎤 Input", "📊 Pipeline", "📁 Output Files"]
# )

# # ── INPUT TAB ──────────────────────────────────────────────────────────
# with tab_input:
#     audio_mic = st.audio_input("🎤 Record Audio")
#     audio_file = st.file_uploader(
#         "📎 Upload Audio",
#         type=["wav", "mp3", "m4a", "ogg", "flac"]
#     )

#     text_cmd = st.text_area("✏️ Or Type Command")

#     run_btn = st.button("▶ Run Agent")

#     if not os.getenv("GROQ_API_KEY"):
#         st.warning("⚠️ GROQ_API_KEY not set in .env")

# # ── FILES TAB ──────────────────────────────────────────────────────────
# with tab_files:
#     files = list(OUTPUT_DIR.glob("*"))

#     if not files:
#         st.info("No files yet.")
#     else:
#         for f in sorted(files, key=lambda x: x.stat().st_mtime, reverse=True):
#             with st.expander(f"📄 {f.name} ({f.stat().st_size} bytes)"):
#                 try:
#                     content = f.read_text(encoding="utf-8")
#                     st.code(content)
#                 except:
#                     st.warning("Cannot read file")

# # ── PIPELINE RENDER ────────────────────────────────────────────────────
# def render_pipeline(transcript, intent_data, result):
#     with tab_output:
#         st.subheader("1. Transcription")
#         st.write(transcript)

#         st.subheader("2. Intent")
#         st.json(intent_data)

#         st.subheader("3. Action")
#         st.write(result.get("action"))

#         st.subheader("4. Output")

#         if result.get("error"):
#             st.error(result["error"])
#         else:
#             intent = intent_data.get("intent")

#             if intent == "write_code":
#                 lang = result.get("language", "python")
#                 st.code(result.get("output"), language=lang)
#             else:
#                 st.write(result.get("output"))

#         if result.get("file_path"):
#             st.success(f"Saved → {result['file_path']}")

# # ── APPROVAL FLOW ──────────────────────────────────────────────────────
# if st.session_state.pending:
#     pend = st.session_state.pending

#     with tab_output:
#         st.warning(f"⚠️ Confirm action: {pend['intent']}")

#         preview = pend["params"].get("code") or pend["params"].get("content")
#         if preview:
#             st.code(preview[:500])

#         col1, col2 = st.columns(2)

#         if col1.button("✅ Approve"):
#             result = execute_tool(pend["intent"], pend["params"], OUTPUT_DIR)

#             st.session_state.memory.add(
#                 pend["transcript"], pend["intent_data"], result
#             )

#             st.session_state.last_result = (
#                 pend["transcript"],
#                 pend["intent_data"],
#                 result,
#             )

#             st.session_state.pending = None

#             st.success("✅ Executed successfully")

#             st.rerun()  # IMPORTANT

#         if col2.button("❌ Cancel"):
#             st.session_state.pending = None
#             st.info("Action cancelled")
#             st.rerun()

# # ── SHOW LAST RESULT ───────────────────────────────────────────────────
# if st.session_state.last_result and not st.session_state.pending:
#     render_pipeline(*st.session_state.last_result)

# # ── MAIN PIPELINE ──────────────────────────────────────────────────────
# if run_btn:
#     audio_source = audio_mic or audio_file

#     if not audio_source and not text_cmd.strip():
#         st.warning("Provide audio or text input.")
#         st.stop()

#     with tab_output:
#         status = st.status("Running pipeline…", expanded=True)

#         # ── STEP 1: INPUT / STT ────────────────────────────────────────
#         if text_cmd.strip():
#             transcript = text_cmd.strip()
#         else:
#             audio_bytes = audio_source.read()

#             if not audio_bytes or len(audio_bytes) < 1000:
#                 st.warning("⚠️ No audio detected.")
#                 st.stop()

#             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
#                 tmp.write(audio_bytes)
#                 tmp_path = tmp.name

#             try:
#                 transcript = transcribe_audio(tmp_path)

#                 if not transcript or len(transcript.strip()) < 3:
#                     st.warning("⚠️ No clear speech detected.")
#                     st.stop()

#             except Exception as e:
#                 st.error(f"STT Error: {e}")
#                 st.stop()
#             finally:
#                 try:
#                     os.unlink(tmp_path)
#                 except:
#                     pass

#         # ── STEP 2: INTENT ────────────────────────────────────────────
#         try:
#             context = st.session_state.memory.get_context()

#             intent_data = classify_intent(
#                 transcript,
#                 model=llm_model,
#                 context=context
#             )

#         except Exception as e:
#             st.error(f"LLM Error: {e}")
#             st.stop()

#         intent = intent_data.get("intent", "general_chat")
#         params = intent_data.get("params", {}) or {}

#         # ── STEP 3: TOOL / CONFIRM ────────────────────────────────────
#         if require_confirm and intent in ("create_file", "write_code"):
#             st.session_state.pending = {
#                 "transcript": transcript,
#                 "intent": intent,
#                 "intent_data": intent_data,
#                 "params": params,
#             }
#             st.rerun()

#         else:
#             result = execute_tool(intent, params, OUTPUT_DIR)

#             st.session_state.memory.add(transcript, intent_data, result)

#             st.session_state.last_result = (
#                 transcript,
#                 intent_data,
#                 result,
#             )

#             status.update(label="Pipeline complete ✅", state="complete")

#             st.rerun()

"""
app.py — Voice-Controlled Local AI Agent
Mem0 Internship Assignment — Rutuja
"""

import os
import tempfile
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from stt import transcribe_audio
from intent import classify_intent
from tools import execute_tool
from memory import SessionMemory

# ── CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VoiceAgent · Mem0",
    page_icon="🎙️",
    layout="wide"
)

# ── SESSION STATE ──────────────────────────────────────────────────────
if "memory" not in st.session_state:
    st.session_state.memory = SessionMemory()
if "history" not in st.session_state:
    st.session_state.history = []
if "pending" not in st.session_state:
    st.session_state.pending = None
if "last_result" not in st.session_state:
    st.session_state.last_result = None

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# ── SIDEBAR ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙ Settings")

    llm_model = st.selectbox(
        "LLM Model",
        ["llama-3.1-8b-instant", "llama-3.3-70b-versatile"]
    )

    require_confirm = st.toggle("Human-in-the-Loop", value=True)

    st.divider()

    col1, col2 = st.columns(2)
    col1.metric("Requests", len(st.session_state.history))
    col2.metric("Files", len(list(OUTPUT_DIR.glob("*"))))

    st.divider()

    st.markdown("### 📜 History")

    if st.session_state.history:
        intent_colors = {
            "create_file": "🟢",
            "write_code": "🔵",
            "summarize": "🟡",
            "general_chat": "🟣",
        }
        for item in reversed(st.session_state.history[-8:]):
            icon = intent_colors.get(item["intent"], "⚪")
            st.markdown(
                f"{icon} **{item['intent'].replace('_', ' ')}**  \n"
                f"<span style='color:#888;font-size:0.8rem'>{item['transcript'][:45]}…</span>",
                unsafe_allow_html=True
            )
            st.divider()
    else:
        st.info("Run a command to see history here.")

    if st.button("🗑 Clear History"):
        st.session_state.history.clear()
        st.session_state.memory.clear()
        st.session_state.last_result = None
        st.rerun()

# ── MAIN UI ────────────────────────────────────────────────────────────
st.title("🎙 VoiceAgent")
st.caption("Voice-controlled AI agent · Mem0 Internship Assignment")

tab_input, tab_output, tab_files = st.tabs(
    ["🎤 Input", "📊 Pipeline", "📁 Output Files"]
)

# ── INPUT TAB ──────────────────────────────────────────────────────────
with tab_input:
    audio_mic = st.audio_input("🎤 Record Audio")
    audio_file = st.file_uploader(
        "📎 Upload Audio",
        type=["wav", "mp3", "m4a", "ogg", "flac"]
    )

    text_cmd = st.text_area("✏️ Or Type Command")

    run_btn = st.button("▶ Run Agent")

    if not os.getenv("GROQ_API_KEY"):
        st.warning("⚠️ GROQ_API_KEY not set in .env")

# ── FILES TAB ──────────────────────────────────────────────────────────
with tab_files:
    files = list(OUTPUT_DIR.glob("*"))

    if not files:
        st.info("No files yet.")
    else:
        for f in sorted(files, key=lambda x: x.stat().st_mtime, reverse=True):
            with st.expander(f"📄 {f.name} ({f.stat().st_size} bytes)"):
                try:
                    content = f.read_text(encoding="utf-8")
                    st.code(content)
                except Exception:
                    st.warning("Cannot read file")

# ── PIPELINE RENDER ────────────────────────────────────────────────────
def render_pipeline(transcript, intent_data, result):
    with tab_output:
        st.subheader("1. Transcription")
        st.write(transcript)

        st.subheader("2. Intent")
        st.json(intent_data)

        st.subheader("3. Action")
        st.write(result.get("action"))

        st.subheader("4. Output")

        if result.get("error"):
            st.error(result["error"])
        else:
            intent = intent_data.get("intent")
            if intent == "write_code":
                lang = result.get("language", "python")
                st.code(result.get("output"), language=lang)
            else:
                st.write(result.get("output"))

        if result.get("file_path"):
            st.success(f"Saved → {result['file_path']}")

# ── APPROVAL FLOW ──────────────────────────────────────────────────────
if st.session_state.pending:
    pend = st.session_state.pending

    with tab_output:
        st.warning(f"⚠️ Confirm action: {pend['intent']}")

        preview = pend["params"].get("code") or pend["params"].get("content")
        if preview:
            st.code(preview[:500])

        col1, col2 = st.columns(2)

        if col1.button("✅ Approve"):
            result = execute_tool(pend["intent"], pend["params"], OUTPUT_DIR)

            st.session_state.memory.add(
                pend["transcript"], pend["intent_data"], result
            )

            st.session_state.history.append({
                "transcript": pend["transcript"],
                "intent": pend["intent"],
            })

            st.session_state.last_result = (
                pend["transcript"],
                pend["intent_data"],
                result,
            )

            st.session_state.pending = None
            st.rerun()

        if col2.button("❌ Cancel"):
            st.session_state.pending = None
            st.rerun()

# ── SHOW LAST RESULT ───────────────────────────────────────────────────
if st.session_state.last_result and not st.session_state.pending:
    render_pipeline(*st.session_state.last_result)

# ── MAIN PIPELINE ──────────────────────────────────────────────────────
if run_btn:
    audio_source = audio_mic or audio_file

    if not audio_source and not text_cmd.strip():
        st.warning("Provide audio or text input.")
        st.stop()

    with tab_output:
        status = st.status("Running pipeline…", expanded=True)

        if text_cmd.strip():
            transcript = text_cmd.strip()
        else:
            audio_bytes = audio_source.read()

            if not audio_bytes or len(audio_bytes) < 1000:
                st.warning("⚠️ No audio detected.")
                st.stop()

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name

            try:
                transcript = transcribe_audio(tmp_path)

                if not transcript or len(transcript.strip()) < 3:
                    st.warning("⚠️ No clear speech detected.")
                    st.stop()

            except Exception as e:
                st.error(f"STT Error: {e}")
                st.stop()
            finally:
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

        try:
            context = st.session_state.memory.get_context()
            intent_data = classify_intent(
                transcript,
                model=llm_model,
                context=context
            )
        except Exception as e:
            st.error(f"LLM Error: {e}")
            st.stop()

        intent = intent_data.get("intent", "general_chat")
        params = intent_data.get("params", {}) or {}

        if require_confirm and intent in ("create_file", "write_code"):
            st.session_state.pending = {
                "transcript": transcript,
                "intent": intent,
                "intent_data": intent_data,
                "params": params,
            }
            st.rerun()

        else:
            result = execute_tool(intent, params, OUTPUT_DIR)

            st.session_state.memory.add(transcript, intent_data, result)

            # ✅ FIXED: append to history
            st.session_state.history.append({
                "transcript": transcript,
                "intent": intent,
            })

            st.session_state.last_result = (
                transcript,
                intent_data,
                result,
            )

            status.update(label="Pipeline complete ✅", state="complete")

            st.rerun()