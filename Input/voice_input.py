"""
Combined Voice Pipeline: Speech-to-Text → Text-to-Speech

Usage:
    python voice_input.py [language_code]
    Example: python voice_input.py hi   (for Hindi)
    Example: python voice_input.py mr   (for Marathi)
    Example: python voice_input.py en   (for English, default)
"""

import os
import sys
import signal
import threading

import pyaudio
from dotenv import load_dotenv
from deepgram import DeepgramClient
from deepgram.core.events import EventType
from deepgram.listen import ListenV1Results

load_dotenv()

API_KEY = os.getenv("DEEPGRAM_API_KEY")
if not API_KEY or API_KEY == "your_api_key_here":
    print("ERROR: Please set your DEEPGRAM_API_KEY in the .env file.")
    sys.exit(1)

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 4096

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "pipeline_output.wav")
VOICE_MODEL = "aura-asteria-en"

# Nova-2 Supported Languages
SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "mr": "Marathi",
    "ta": "Tamil",
    "te": "Telugu",
    "bn": "Bengali",
    "gu": "Gujarati",
    "kn": "Kannada",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "ja": "Japanese",
}

# Ensure Windows terminal supports UTF-8, emojis, and Indic scripts
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Determine language from command line argument (default: "en")
def _resolve_default_language() -> str:
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower().strip()
        if not arg.startswith("-") and arg not in ("text", "interactive"):
            return arg
    return "en"

SELECTED_LANGUAGE = _resolve_default_language()
if __name__ == "__main__" and SELECTED_LANGUAGE not in SUPPORTED_LANGUAGES:
    print(f"⚠️  Warning: '{SELECTED_LANGUAGE}' not in known list. Passing directly to Deepgram.")


def capture_speech(language: str = None) -> str:
    transcript_parts: list[str] = []
    lang = language or SELECTED_LANGUAGE

    client = DeepgramClient(api_key=API_KEY)

    with client.listen.v1.connect(
        model="nova-2",
        language=lang,
        smart_format=True,
        interim_results=True,
        encoding="linear16",
        channels=CHANNELS,
        sample_rate=RATE,
    ) as ws:

        stop_event = threading.Event()
        silence_timer = None

        def on_open(_data):
            print("\n🎙️  Listening — speak your command!")
            print("   (Recording auto-completes after speaking, or press Ctrl+C)\n")

        def on_close(_data):
            print("\n🔌 Connection closed.")

        def on_error(error):
            print(f"\n❌ Error: {error}")

        def on_message(message):
            nonlocal silence_timer
            if not isinstance(message, ListenV1Results):
                return

            alternative = message.channel.alternatives[0]
            sentence = alternative.transcript
            if not sentence:
                return

            if message.is_final:
                transcript_parts.append(sentence)
                print(f"  ✅ [{lang.upper()}] {sentence}")

                # Automatically complete 1.5 seconds after a finalized sentence
                if silence_timer:
                    silence_timer.cancel()
                silence_timer = threading.Timer(1.5, stop_event.set)
                silence_timer.start()
            else:
                print(f"  ⏳ {sentence}", end="\r")
                if silence_timer:
                    silence_timer.cancel()

        ws.on(EventType.OPEN, on_open)
        ws.on(EventType.CLOSE, on_close)
        ws.on(EventType.ERROR, on_error)
        ws.on(EventType.MESSAGE, on_message)

        listener_thread = threading.Thread(target=ws.start_listening, daemon=True)
        listener_thread.start()

        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )

        try:
            while not stop_event.is_set():
                data = stream.read(CHUNK, exception_on_overflow=False)
                ws.send_media(data)
        except KeyboardInterrupt:
            print("\n⏹️  Recording stopped.")
        finally:
            if silence_timer:
                silence_timer.cancel()
            stream.stop_stream()
            stream.close()
            audio.terminate()
            ws.send_close_stream()
            listener_thread.join(timeout=3)

    full_text = " ".join(transcript_parts).strip()
    return full_text


def main():
    lang_name = SUPPORTED_LANGUAGES.get(SELECTED_LANGUAGE, SELECTED_LANGUAGE)
    print("=" * 55)
    print(f"  🎤 Deepgram Voice Pipeline ({lang_name} - '{SELECTED_LANGUAGE}')")
    print("=" * 55)
    
    print("\n📌 STEP 1: Speech-to-Text")
    print("   Speak into your microphone. Press Ctrl+C to finish.\n")

    transcribed_text = capture_speech()
    if not transcribed_text:
        print("\n⚠️  No speech was detected. Exiting.")
        return
    print(f"\n📄 Full transcription:\n   \"{transcribed_text}\"\n")


if __name__ == "__main__":
    main()
