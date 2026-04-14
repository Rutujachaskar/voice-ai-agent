

"""
stt.py — Speech-to-Text module

Uses Groq Whisper API (fast, free).
Falls back safely to local Whisper.
Handles edge cases like empty audio.
"""

import os


def transcribe_audio(audio_path: str) -> str:
    """
    Transcribe audio file to text safely.
    """

    api_key = os.getenv("GROQ_API_KEY")

    # ✅ Try Groq first
    if api_key:
        try:
            print("[STT] Using Groq Whisper API...")
            text = _transcribe_groq(audio_path, api_key)

            # ✅ Handle empty / noise output
            if not text or len(text.strip()) < 2:
                return ""

            return text.strip()

        except Exception as e:
            print(f"[STT WARNING] Groq failed: {e}")
            print("[STT] Falling back to local Whisper...")

    # ✅ Safe fallback
    try:
        return _transcribe_local(audio_path)
    except Exception as e:
        print(f"[STT ERROR] Local fallback failed: {e}")
        return ""   # ⚠️ DO NOT CRASH APP


def _transcribe_groq(audio_path: str, api_key: str) -> str:
    """Groq Whisper API"""

    from groq import Groq
    client = Groq(api_key=api_key)

    # ✅ Ensure correct file handling
    filename = os.path.basename(audio_path)

    # Fix extension issue (important for Groq)
    if not filename.endswith((".wav", ".mp3", ".m4a", ".ogg", ".flac", ".webm")):
        filename = filename + ".wav"

    with open(audio_path, "rb") as f:
        transcription = client.audio.transcriptions.create(
            file=(filename, f.read()),
            model="whisper-large-v3",
            response_format="text",
            language="en",
        )

    return str(transcription)


def _transcribe_local(audio_path: str) -> str:
    """
    Local Whisper fallback
    """

    try:
        import whisper

        print("[STT] Using local Whisper model...")
        model = whisper.load_model("base")

        result = model.transcribe(audio_path)
        return result.get("text", "").strip()

    except ImportError:
        print("[STT ERROR] Whisper not installed")
        return ""

    except Exception as e:
        print(f"[STT ERROR] Local transcription failed: {e}")
        return ""