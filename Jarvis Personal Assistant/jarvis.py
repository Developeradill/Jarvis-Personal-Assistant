import os
import sys
import time
import json
import tempfile
import platform
from pathlib import Path
from datetime import datetime, date
import random, re

# Ensure ffmpeg path is generic (user should install ffmpeg and add to PATH)
os.environ["PATH"] = os.environ.get("PATH", "") + os.pathsep + r";C:\ffmpeg\bin"  # Update if different

# Load environment variables (.env) for API keys
from dotenv import load_dotenv
load_dotenv()

# Text-to-Speech
import pyttsx3

# Speech-to-Text backends
import speech_recognition as sr

# Optional / fallback audio capture
try:
    import sounddevice as sd
    from scipy.io.wavfile import write as wav_write
    HAVE_SOUNDDEVICE = True
except Exception:
    HAVE_SOUNDDEVICE = False

# Whisper (offline STT)
import whisper

# Optional: Vosk offline STT
try:
    from vosk import Model as VoskModel, KaldiRecognizer
    import wave
    HAVE_VOSK = True
except Exception:
    HAVE_VOSK = False

# OpenAI API (chat brain)
try:
    from openai import OpenAI
    openai_client = OpenAI()  # Requires OPENAI_API_KEY in environment
except Exception:
    openai_client = None
    print("OpenAI client unavailable. Using offline fallback.")

# App directories
APP_DIR = Path(__file__).resolve().parent
MEMORY_FILE = APP_DIR / "memory.json"

def load_memory():
    if MEMORY_FILE.exists():
        try:
            return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"facts": {}, "notes": []}

def save_memory(mem):
    try:
        MEMORY_FILE.write_text(json.dumps(mem, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        print("Warning: Could not save memory.")

def speak(text, rate=None, volume=None):
    engine = pyttsx3.init()
    try:
        engine.setProperty('rate', rate or 170)
        engine.setProperty('volume', volume or 1.0)
    except Exception:
        pass
    engine.say(text)
    engine.runAndWait()

def pick_microphone(recognizer):
    try:
        mic_list = sr.Microphone.list_microphone_names()
        if not mic_list:
            return None
        return sr.Microphone()
    except Exception:
        return None

def record_with_speech_recognition(max_seconds=15):
    r = sr.Recognizer()
    mic = pick_microphone(r)
    if mic is None:
        raise RuntimeError("No microphone detected.")
    with mic as source:
        r.adjust_for_ambient_noise(source, duration=0.7)
        print("Listening...")
        audio = r.listen(source, timeout=10, phrase_time_limit=max_seconds)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    tmp.write(audio.get_wav_data())
    tmp.flush()
    tmp.close()
    return tmp.name

def record_with_sounddevice(max_seconds=15, samplerate=16000):
    if not HAVE_SOUNDDEVICE:
        raise RuntimeError("sounddevice not available")
    import numpy as np
    frames = int(max_seconds * samplerate)
    audio = sd.rec(frames, samplerate=samplerate, channels=1, dtype="int16")
    sd.wait()
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wav_write(tmp.name, samplerate, audio)
    return tmp.name

def transcribe_whisper(audio_path, model_size="base"):
    model = whisper.load_model(model_size)
    force_lang = os.getenv("FORCE_LANGUAGE", "").strip().lower()
    result = model.transcribe(audio_path, fp16=False, language=force_lang if force_lang else None)
    return (result.get("text") or "").strip()

def transcribe_vosk(audio_path, model_dir):
    if not HAVE_VOSK:
        raise RuntimeError("Vosk not installed.")
    if not Path(model_dir).exists():
        raise RuntimeError(f"Vosk model not found at {model_dir}")
    model = VoskModel(model_dir)
    rec = KaldiRecognizer(model, 16000)
    rec.SetWords(True)
    with wave.open(audio_path, "rb") as wf:
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            rec.AcceptWaveform(data)
    import json as _json
    res = _json.loads(rec.FinalResult())
    return (res.get("text") or "").strip()

def chat_reply(user_text, memory):
    if openai_client is None:
        return None
    facts_summary = "; ".join([f"{k}: {v}" for k, v in memory.get("facts", {}).items()]) or "none"
    system_msg = (
        "You are Jarvis, a generic desktop assistant. "
        f"Known facts: {facts_summary}."
    )
    try:
        resp = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_text},
            ],
            temperature=0.5,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return None

def maybe_store_memory(answer_text, memory):
    for line in (answer_text or "").splitlines():
        if line.strip().startswith("MEMO:"):
            payload = line.strip()[5:].strip()
            try:
                data = json.loads(payload)
                key = str(data.get("key", "")).strip()
                val = str(data.get("value", "")).strip()
                if key:
                    memory.setdefault("facts", {})[key] = val
                    save_memory(memory)
            except Exception:
                pass

def run_command_if_any(text):
    text_l = text.lower().strip()
    try:
        if text_l.startswith("open "):
            target = text_l[5:].strip()
            if target in ["notepad", "text editor"] and platform.system() == "Windows":
                os.system("start notepad")
                return "Opening Notepad."
            if target in ["calculator"]:
                os.system("start calc" if platform.system()=="Windows" else "gnome-calculator >/dev/null 2>&1 &")
                return "Opening calculator."
        if "time" in text_l:
            return "It is " + datetime.now().strftime("%I:%M %p")
    except Exception:
        return None
    return None

def offline_reply(user_text, memory):
    txt = user_text.strip().lower()
    if any(x in txt for x in ["hello", "hi", "hey"]):
        return "Hi! I’m listening. How can I help?"
    if "joke" in txt:
        return random.choice([
            "Why did the computer go to therapy? It had too many bugs!",
            "Why did the programmer quit? Because he didn't get arrays.",
            "Why don’t scientists trust atoms? Because they make up everything!"
        ])
    if "time" in txt:
        return "It is " + datetime.now().strftime("%I:%M %p")
    if "date" in txt:
        return "Today is " + date.today().strftime("%A, %B %d, %Y")
    m = re.search(r"(take|add)\s+a?\s*note\s+(.*)", txt)
    if m:
        note = m.group(2).strip()
        if note:
            notes_path = APP_DIR / "notes.txt"
            with open(notes_path, "a", encoding="utf-8") as f:
                f.write(note + "\n")
            return f"Noted: {note}"
    return "Offline mode: I can run local commands, tell time/date, remember notes, and tell jokes."

def main():
    print("=== Jarvis Assistant ===")
    print("Press Enter to talk. Ctrl+C to quit.\n")
    memory = load_memory()
    stt_backend = os.getenv("STT_BACKEND", "whisper").lower()
    whisper_size = os.getenv("WHISPER_MODEL_SIZE", "tiny")
    vosk_dir = os.getenv("VOSK_MODEL_DIR", "./models/vosk-small-en")

    while True:
        try:
            input(">> Press Enter to speak...")
            audio_path = None
            try:
                audio_path = record_with_speech_recognition(max_seconds=15)
            except Exception:
                if HAVE_SOUNDDEVICE:
                    audio_path = record_with_sounddevice(max_seconds=15)
                else:
                    print("No audio backend available.")
                    continue

            text = transcribe_vosk(audio_path, vosk_dir) if stt_backend=="vosk" else transcribe_whisper(audio_path, whisper_size)
            try: os.remove(audio_path)
            except Exception: pass
            if not text:
                print("(heard nothing intelligible)")
                continue
            print(f"You said: {text}")

            cmd_response = run_command_if_any(text)
            if cmd_response:
                print("Jarvis:", cmd_response)
                speak(cmd_response)
                continue

            reply = chat_reply(text, memory) or offline_reply(text, memory)
            maybe_store_memory(reply, memory)

            print("Jarvis:", reply)
            speak(reply)

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print("Error:", e)
            time.sleep(1)

if __name__ == "__main__":
    main()
