"""
Synapse - Voice-Driven AI Assistant & Automation Engine

Coordinates the full pipeline in a continuous hands-free loop:
  Voice Input (Ear) → Brain (Orchestrator) → Executor (Hands)
  with a non-intrusive floating screen HUD indicator.

Usage:
    python main.py [language_code]
    Example: python main.py hi       (Continuous listen in Hindi)
    Example: python main.py en       (Continuous listen in English, default)
    Example: python main.py --text   (Interactive text prompt mode for testing)
"""

import sys
import time
import signal
from Input.voice_input import capture_speech, SUPPORTED_LANGUAGES
from Brain.schema import ActionType
from Brain.orchestrator import Orchestrator
from Execution.executor import Executor
from UI.overlay import FloatingOverlay

# Ensure Windows terminal supports UTF-8, emojis, and Indic scripts
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def print_banner(mode: str, language: str):
    lang_name = SUPPORTED_LANGUAGES.get(language, language)
    print("\n" + "=" * 65)
    print("  ⚡ SYNAPSE: Voice & Automation Pipeline (Hands-Free)")
    print(f"  Mode: {mode} | Language: {lang_name} ('{language}')")
    print("  To stop: Say 'stop listening' or press Ctrl+C")
    print("=" * 65 + "\n")


def run_pipeline(prompt: str, language: str, orchestrator: Orchestrator, executor: Executor, overlay: FloatingOverlay = None) -> bool:
    """
    Runs a single pass through the Brain and Executor.
    
    Returns:
        bool: False if the user commanded to exit/stop Synapse, True to keep running.
    """
    if not prompt or not prompt.strip():
        return True

    # 1. Orchestration Phase (Brain)
    if overlay:
        overlay.set_status("analyzing", "Thinking...")

    plan = orchestrator.plan(prompt, language=language)

    # 2. Check for Exit / Stop Commands
    for task in plan.tasks:
        if task.action == ActionType.EXIT_APP:
            print("\n👋 [Synapse] Stop command received. Shutting down gracefully...")
            if overlay:
                overlay.set_status("stopped", "Synapse: Goodbye!")
                time.sleep(1.2)
            return False

    # 3. Execution Phase (Hands)
    if overlay and plan.tasks:
        first_desc = plan.tasks[0].description
        overlay.set_status("executing", first_desc)

    executor.execute_plan(plan)
    return True


def main():
    orchestrator = Orchestrator()
    executor = Executor()
    overlay = FloatingOverlay()

    # Start the floating non-activating HUD
    overlay.start()

    # Interactive Text Mode
    is_text_mode = False
    text_lang = "en"
    if len(sys.argv) > 1:
        first_arg = sys.argv[1].lower()
        if first_arg in ("--text", "-t", "text", "--interactive", "-i"):
            is_text_mode = True
            if len(sys.argv) > 2:
                text_lang = sys.argv[2].lower()

    if is_text_mode:
        print_banner("Interactive Text Mode", text_lang)
        overlay.set_status("idle", f"Synapse: Text Mode ({text_lang.upper()})")
        print("Type a command (or 'exit' / 'stop' to quit):\n")
        try:
            while True:
                user_cmd = input("💬 User > ").strip()
                if not user_cmd:
                    continue
                if user_cmd.lower() in ("exit", "quit", "stop", "q"):
                    print("\n👋 Exiting text mode.")
                    break
                should_continue = run_pipeline(user_cmd, text_lang, orchestrator, executor, overlay)
                if not should_continue:
                    break
                overlay.set_status("idle", "Synapse: Ready")
                print("\n" + "-" * 50)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting text mode.")
        finally:
            overlay.stop()
        return

    # Continuous Voice Loop Mode
    lang = sys.argv[1].lower() if len(sys.argv) > 1 else "en"
    print_banner("Continuous Live Voice Mode", lang)

    try:
        while True:
            # 1. Update HUD to listening state
            overlay.set_status("listening", f"Synapse: Listening ({lang.upper()})...")

            # 2. Capture voice input (auto-completes after speaking)
            transcribed_text = capture_speech(language=lang)

            if not transcribed_text:
                continue

            print(f"\n🗣️  Transcribed Speech: \"{transcribed_text}\"")

            # 3. Process the command through the pipeline
            should_continue = run_pipeline(transcribed_text, lang, orchestrator, executor, overlay)
            if not should_continue:
                break

            print("\n" + "-" * 50)
            print("🎙️  Ready for next command...")

    except KeyboardInterrupt:
        print("\n\n⏹️  Synapse stopped via KeyboardInterrupt.")
    finally:
        overlay.stop()
        print("⚡ Synapse has shut down cleanly.\n")


if __name__ == "__main__":
    main()
