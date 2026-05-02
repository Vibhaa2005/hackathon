import os
import requests
from typing import Optional

SARVAM_BASE = "https://api.sarvam.ai"

LANGUAGE_CODES = {
    "English": "en-IN",
    "Hindi": "hi-IN",
    "Tamil": "ta-IN",
    "Telugu": "te-IN",
    "Kannada": "kn-IN",
    "Malayalam": "ml-IN",
    "Bengali": "bn-IN",
    "Marathi": "mr-IN",
    "Gujarati": "gu-IN",
    "Punjabi": "pa-IN",
    "Odia": "od-IN",
}


def _get_api_key() -> Optional[str]:
    return os.environ.get("SARVAM_API_KEY", "")


def translate_to_english(text: str, source_lang: str) -> str:
    if source_lang == "English":
        return text
    api_key = _get_api_key()
    if not api_key:
        return text
    src_code = LANGUAGE_CODES.get(source_lang, "hi-IN")
    try:
        resp = requests.post(
            f"{SARVAM_BASE}/translate",
            json={
                "input": text,
                "source_language_code": src_code,
                "target_language_code": "en-IN",
                "speaker_gender": "Male",
                "mode": "formal",
                "model": "mayura:v1",
                "enable_preprocessing": True,
            },
            headers={"api-subscription-key": api_key},
            timeout=15,
        )
        if resp.status_code == 200:
            return resp.json().get("translated_text", text)
    except Exception:
        pass
    return text


def translate_from_english(text: str, target_lang: str) -> str:
    if target_lang == "English":
        return text
    api_key = _get_api_key()
    if not api_key:
        return text
    tgt_code = LANGUAGE_CODES.get(target_lang, "hi-IN")
    # Split into chunks of 1000 chars for Sarvam API limit
    chunks = [text[i:i+900] for i in range(0, len(text), 900)]
    translated_parts = []
    for chunk in chunks:
        try:
            resp = requests.post(
                f"{SARVAM_BASE}/translate",
                json={
                    "input": chunk,
                    "source_language_code": "en-IN",
                    "target_language_code": tgt_code,
                    "speaker_gender": "Male",
                    "mode": "formal",
                    "model": "mayura:v1",
                    "enable_preprocessing": True,
                },
                headers={"api-subscription-key": api_key},
                timeout=15,
            )
            if resp.status_code == 200:
                translated_parts.append(resp.json().get("translated_text", chunk))
            else:
                translated_parts.append(chunk)
        except Exception:
            translated_parts.append(chunk)
    return " ".join(translated_parts)


def speech_to_text(audio_bytes: bytes, language: str) -> str:
    api_key = _get_api_key()
    if not api_key:
        return ""
    lang_code = LANGUAGE_CODES.get(language, "hi-IN")
    try:
        resp = requests.post(
            f"{SARVAM_BASE}/speech-to-text",
            files={"file": ("audio.wav", audio_bytes, "audio/wav")},
            data={
                "language_code": lang_code,
                "model": "saarika:v1",
                "with_timestamps": "false",
            },
            headers={"api-subscription-key": api_key},
            timeout=30,
        )
        if resp.status_code == 200:
            return resp.json().get("transcript", "")
    except Exception:
        pass
    return ""


def text_to_speech(text: str, language: str) -> Optional[bytes]:
    api_key = _get_api_key()
    if not api_key:
        return None
    lang_code = LANGUAGE_CODES.get(language, "hi-IN")
    snippet = text[:500]
    try:
        resp = requests.post(
            f"{SARVAM_BASE}/text-to-speech",
            json={
                "inputs": [snippet],
                "target_language_code": lang_code,
                "speaker": "meera",
                "pitch": 0,
                "pace": 1.0,
                "loudness": 1.5,
                "speech_sample_rate": 22050,
                "enable_preprocessing": True,
                "model": "bulbul:v1",
            },
            headers={"api-subscription-key": api_key},
            timeout=30,
        )
        if resp.status_code == 200:
            import base64
            audio_b64 = resp.json().get("audios", [""])[0]
            if audio_b64:
                return base64.b64decode(audio_b64)
    except Exception:
        pass
    return None
