"""
Combined Voice Pipeline: Speech-to-Text → Text-to-Speech

Usage:
    python input.py

1. Listens to your microphone and transcribes speech in real-time.
2. When you press Ctrl+C, takes the full transcription and converts it
   back to speech using Deepgram TTS.
3. Plays the generated audio.
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


def play_audio(filepath: str):
    if sys.platform == "win32":
        import winsound
        winsound.PlaySound(filepath, winsound.SND_FILENAME)
    else:
        try:
            from playsound import playsound
            playsound(filepath)
        except ImportError:
            print(f"ℹ️  Audio saved to {filepath}")
            print("   Install 'playsound' to auto-play: pip install playsound")


def capture_speech() -> str:
    # Collect all final transcript segments
    transcript_parts: list[str] = []

    client = DeepgramClient(api_key=API_KEY)

    with client.listen.v1.connect(
        model="nova-2",
        language="en",
        smart_format=True,
        interim_results=True,
        encoding="linear16",
        channels=CHANNELS,
        sample_rate=RATE,
    ) as ws:

        # ── Event handlers ──

        def on_open(_data):
            print("\n🎙️  Connection opened — start speaking!")
            print("   Press Ctrl+C when you're done.\n")

        def on_close(_data):
            print("\n🔌 Connection closed.")

        def on_error(error):
            print(f"\n❌ Error: {error}")

        def on_message(message):
            if not isinstance(message, ListenV1Results):
                return

            sentence = message.channel.alternatives[0].transcript
            if not sentence:
                return

            if message.is_final:
                transcript_parts.append(sentence)
                print(f"  ✅ {sentence}")
            else:
                print(f"  ⏳ {sentence}", end="\r")

        ws.on(EventType.OPEN, on_open)
        ws.on(EventType.CLOSE, on_close)
        ws.on(EventType.ERROR, on_error)
        ws.on(EventType.MESSAGE, on_message)

        # ── Listen in background thread ──
        listener_thread = threading.Thread(target=ws.start_listening, daemon=True)
        listener_thread.start()

        # ── Stream mic audio ──
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )

        try:
            while True:
                data = stream.read(CHUNK, exception_on_overflow=False)
                ws.send_media(data)
        except KeyboardInterrupt:
            print("\n\n⏹️  Recording stopped.")
        finally:
            stream.stop_stream()
            stream.close()
            audio.terminate()
            ws.send_close_stream()
            listener_thread.join(timeout=3)

    full_text = " ".join(transcript_parts).strip()
    return full_text


def synthesize_speech(text: str) -> str:
    print(f"\n🔊 Converting to speech: \"{text[:80]}{'...' if len(text) > 80 else ''}\"")

    client = DeepgramClient(api_key=API_KEY)

    response = client.speak.v1.audio.generate(
        text=text,
        model=VOICE_MODEL,
        encoding="linear16",
        container="wav",
    )

    with open(OUTPUT_FILE, "wb") as audio_file:
        for chunk in response:
            if chunk:
                audio_file.write(chunk)

    print(f"✅ Audio saved to: {OUTPUT_FILE}")
    return OUTPUT_FILE


def main():
    if sys.platform == "win32":
        signal.signal(signal.SIGINT, signal.SIG_DFL)

    print("=" * 55)
    print("  🎤 Deepgram Voice Pipeline: STT → TTS")
    print("=" * 55)
    
    print("\n📌 STEP 1: Speech-to-Text")
    print("   Speak into your microphone. Press Ctrl+C to finish.\n")

    transcribed_text = capture_speech()
    if not transcribed_text:
        print("\n⚠️  No speech was detected. Exiting.")
        return
    print(f"\n📄 Full transcription:\n   \"{transcribed_text}\"\n")


    print("📌 STEP 2: Text-to-Speech")
    filepath = synthesize_speech(transcribed_text)

    print("\n▶️  Playing generated audio...")
    play_audio(filepath)
    print("\n✨ Pipeline complete!")


if __name__ == "__main__":
    main()
