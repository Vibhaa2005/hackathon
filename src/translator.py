import base64
import io
import os
import wave
import requests
from typing import Optional

SARVAM_BASE = "https://api.sarvam.ai"

LANGUAGE_CODES = {
    "English":   "en-IN",
    "Hindi":     "hi-IN",
    "Tamil":     "ta-IN",
    "Telugu":    "te-IN",
    "Kannada":   "kn-IN",
    "Malayalam": "ml-IN",
    "Bengali":   "bn-IN",
    "Marathi":   "mr-IN",
    "Gujarati":  "gu-IN",
    "Punjabi":   "pa-IN",
    "Odia":      "od-IN",
}

GTTS_CODES = {
    "English":   "en",
    "Hindi":     "hi",
    "Tamil":     "ta",
    "Telugu":    "te",
    "Kannada":   "kn",
    "Malayalam": "ml",
    "Bengali":   "bn",
    "Marathi":   "mr",
    "Gujarati":  "gu",
    "Punjabi":   "pa",
    "Odia":      "or",
}

_TRANSLATE_CHUNK = 900   # Sarvam translation limit
_TTS_CHUNK       = 480   # Sarvam TTS limit


def _get_api_key() -> Optional[str]:
    return os.environ.get("SARVAM_API_KEY", "")


# ── Translation ──────────────────────────────────────────────────────────────

def translate_to_english(text: str, source_lang: str) -> str:
    if source_lang == "English":
        return text
    api_key = _get_api_key()
    if not api_key:
        return text
    src_code = LANGUAGE_CODES.get(source_lang, "hi-IN")
    chunks = [text[i:i + _TRANSLATE_CHUNK] for i in range(0, len(text), _TRANSLATE_CHUNK)]
    parts = []
    for chunk in chunks:
        try:
            resp = requests.post(
                f"{SARVAM_BASE}/translate",
                json={
                    "input": chunk,
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
                parts.append(resp.json().get("translated_text", chunk))
            else:
                parts.append(chunk)
        except Exception:
            parts.append(chunk)
    return " ".join(parts)


def translate_from_english(text: str, target_lang: str) -> str:
    if target_lang == "English":
        return text
    api_key = _get_api_key()
    if not api_key:
        return text
    tgt_code = LANGUAGE_CODES.get(target_lang, "hi-IN")
    chunks = [text[i:i + _TRANSLATE_CHUNK] for i in range(0, len(text), _TRANSLATE_CHUNK)]
    parts = []
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
                parts.append(resp.json().get("translated_text", chunk))
            else:
                parts.append(chunk)
        except Exception:
            parts.append(chunk)
    return " ".join(parts)


# ── Speech-to-text ───────────────────────────────────────────────────────────

def _stt_sarvam(audio_bytes: bytes, language: str, api_key: str) -> str:
    lang_code = LANGUAGE_CODES.get(language, "hi-IN")
    try:
        resp = requests.post(
            f"{SARVAM_BASE}/speech-to-text",
            files={"file": ("audio.wav", audio_bytes, "audio/wav")},
            data={
                "language_code": lang_code,
                "model": "saarika:v2.5",
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


def _stt_google(audio_bytes: bytes, language: str) -> str:
    try:
        import speech_recognition as sr
        lang_code = LANGUAGE_CODES.get(language, "hi-IN")
        r = sr.Recognizer()
        with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
            audio = r.record(source)
        return r.recognize_google(audio, language=lang_code)
    except Exception:
        return ""


def speech_to_text(audio_bytes: bytes, language: str) -> str:
    api_key = _get_api_key()
    if api_key:
        result = _stt_sarvam(audio_bytes, language, api_key)
        if result:
            return result
    return _stt_google(audio_bytes, language)


# ── Text-to-speech ───────────────────────────────────────────────────────────

def _concat_wavs(wav_bytes_list: list[bytes]) -> bytes:
    """Concatenate multiple WAV byte-strings into one, re-writing the header."""
    if not wav_bytes_list:
        return b""
    if len(wav_bytes_list) == 1:
        return wav_bytes_list[0]

    # Read params from the first chunk
    with wave.open(io.BytesIO(wav_bytes_list[0])) as w:
        params = w.getparams()
        frames = w.readframes(w.getnframes())

    all_frames = bytearray(frames)
    for chunk in wav_bytes_list[1:]:
        with wave.open(io.BytesIO(chunk)) as w:
            all_frames.extend(w.readframes(w.getnframes()))

    out = io.BytesIO()
    with wave.open(out, "wb") as w:
        w.setparams(params)
        w.writeframes(bytes(all_frames))
    return out.getvalue()


def _tts_sarvam(text: str, language: str, api_key: str) -> Optional[bytes]:
    """Try Sarvam bulbul:v2 TTS. Returns WAV bytes or None."""
    lang_code = LANGUAGE_CODES.get(language, "hi-IN")
    chunks = [text[i:i + _TTS_CHUNK] for i in range(0, len(text), _TTS_CHUNK)]
    wav_chunks: list[bytes] = []
    for chunk in chunks:
        try:
            resp = requests.post(
                f"{SARVAM_BASE}/text-to-speech",
                json={
                    "inputs": [chunk],
                    "target_language_code": lang_code,
                    "speaker": "meera",
                    "pitch": 0,
                    "pace": 1.0,
                    "loudness": 1.5,
                    "speech_sample_rate": 22050,
                    "enable_preprocessing": True,
                    "model": "bulbul:v2",
                },
                headers={"api-subscription-key": api_key},
                timeout=30,
            )
            if resp.status_code == 200:
                audio_b64 = resp.json().get("audios", [""])[0]
                if audio_b64:
                    wav_chunks.append(base64.b64decode(audio_b64))
        except Exception:
            pass
    return _concat_wavs(wav_chunks) if wav_chunks else None


def _tts_gtts(text: str, language: str) -> Optional[bytes]:
    """Fallback TTS via gTTS (Google). Returns MP3 bytes or None."""
    try:
        from gtts import gTTS
        lang_code = GTTS_CODES.get(language, "en")
        buf = io.BytesIO()
        gTTS(text=text, lang=lang_code, slow=False).write_to_fp(buf)
        buf.seek(0)
        return buf.read()
    except Exception:
        return None


def text_to_speech(text: str, language: str) -> tuple[Optional[bytes], str]:
    """Returns (audio_bytes, fmt). Tries Sarvam first, falls back to gTTS.
    fmt is 'audio/wav' for Sarvam, 'audio/mp3' for gTTS, '' on failure.
    """
    api_key = _get_api_key()
    if api_key:
        audio = _tts_sarvam(text, language, api_key)
        if audio:
            return audio, "audio/wav"

    # Fallback: gTTS (no API key required)
    audio = _tts_gtts(text, language)
    if audio:
        return audio, "audio/mp3"

    return None, ""
