


"""
intent.py — Intent classification using Groq LLM
"""

import os
import json
import re


SYSTEM_PROMPT = """You are an intent classifier and code/content generator for a voice-controlled AI agent.

Classify into EXACTLY ONE of:
- create_file
- write_code
- summarize
- general_chat

Rules:
- If user wants to create/save file → create_file
- If user asks for code → write_code
- If user asks to summarize → summarize
- Otherwise → general_chat

Return ONLY valid JSON:
{
  "intent": "...",
  "confidence": "high|medium|low",
  "reasoning": "...",
  "params": {
    "filename": "...",
    "language": "...",
    "content": "...",
    "code": "...",
    "response": "..."
  }
}
"""


def classify_intent(
    transcript: str,
    model: str = "llama-3.1-8b-instant",
    context: str = "",
) -> dict:

    # ✅ EDGE CASE: empty or noise input
    if not transcript or len(transcript.strip()) < 3:
        return {
            "intent": "general_chat",
            "confidence": "low",
            "reasoning": "Empty or unclear input",
            "params": {
                "response": "I didn't catch that. Could you please repeat?"
            }
        }

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError("GROQ_API_KEY not set")

    user_message = transcript
    if context:
        user_message = f"[Context]\n{context}\n\nUser: {transcript}"

    from groq import Groq
    client = Groq(api_key=api_key)

    try:
        print(f"[INTENT] Using model: {model}")

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.2,
            max_tokens=1200,
            response_format={"type": "json_object"},
        )

    except Exception as e:
        print(f"[WARNING] Model failed: {model} → Falling back")

        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.2,
                max_tokens=1200,
                response_format={"type": "json_object"},
            )
        except Exception as e2:
            print(f"[ERROR] Fallback model also failed: {e2}")

            # ✅ FINAL SAFE FALLBACK
            return {
                "intent": "general_chat",
                "confidence": "low",
                "reasoning": "LLM failure fallback",
                "params": {
                    "response": "Sorry, something went wrong while understanding your request."
                }
            }

    raw = response.choices[0].message.content
    return _parse_response(raw)


def _parse_response(raw: str) -> dict:
    """Clean and safely parse model JSON output"""

    if not raw:
        return _default_response()

    cleaned = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()

    try:
        data = json.loads(cleaned)
    except Exception:
        print("[PARSE ERROR] Raw output:", raw)
        return _default_response()

    # ✅ Defaults
    data.setdefault("intent", "general_chat")
    data.setdefault("confidence", "low")
    data.setdefault("reasoning", "fallback")
    data.setdefault("params", {})

    # ✅ Normalize confidence
    conf = str(data["confidence"]).lower()
    if conf not in ("high", "medium", "low"):
        data["confidence"] = "medium" if "0." in conf else "low"
    else:
        data["confidence"] = conf

    # ✅ Ensure params exist
    for key in ("filename", "language", "content", "code", "response"):
        data["params"].setdefault(key, None)

    return data


def _default_response():
    return {
        "intent": "general_chat",
        "confidence": "low",
        "reasoning": "Parsing fallback",
        "params": {
            "response": "I couldn't understand that properly. Try again."
        }
    }