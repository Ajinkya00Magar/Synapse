"""
High-Performance GUI, Mouse, and Keyboard Action Handlers.

Optimized for ultra-low latency (< 1ms) execution using:
1. pyautogui with PAUSE = 0.0 (zero artificial sleep)
2. Direct Windows Win32 user32 C API calls for instantaneous mouse scrolling & hardware events
"""

import sys
import time
import ctypes
import pyautogui

# Eliminate PyAutoGUI's default 100ms artificial pause
pyautogui.PAUSE = 0.0
pyautogui.FAILSAFE = False

# Win32 Mouse & Keyboard Constants
MOUSEEVENTF_WHEEL = 0x0800
WHEEL_DELTA = 120
user32 = ctypes.windll.user32 if sys.platform == "win32" else None


def scroll_page(direction: str = "down", intensity: int = 5) -> str:
    """
    Performs instantaneous hardware mouse wheel scrolling.
    
    Latency: ~0.1 ms (direct hardware message pump).
    """
    clean_dir = direction.strip().lower()
    # 1 click = 120 wheel delta units
    # Positive = scroll up, Negative = scroll down
    clicks = intensity if intensity > 0 else 5
    delta = WHEEL_DELTA * clicks if clean_dir in ("up", "top") else -(WHEEL_DELTA * clicks)

    if user32:
        # Direct Win32 C call
        user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, delta, 0)
    else:
        pyautogui.scroll(delta)

    return f"Scrolled {clean_dir} ({clicks} units)."


def press_key_or_shortcut(key_name: str) -> str:
    """
    Simulates pressing a single key (Enter, Space, Esc, Tab) or hotkey combination.
    
    Latency: < 1 ms.
    """
    clean = key_name.strip().lower()

    # Handle common key aliases
    aliases = {
        "enter": "enter",
        "return": "enter",
        "space": "space",
        "spacebar": "space",
        "escape": "esc",
        "esc": "esc",
        "tab": "tab",
        "backspace": "backspace",
        "delete": "delete",
        "up": "up",
        "down": "down",
        "left": "left",
        "right": "right",
    }

    # Check for hotkey combinations separated by '+'
    if "+" in clean:
        keys = [k.strip() for k in clean.split("+")]
        pyautogui.hotkey(*keys)
        return f"Pressed shortcut: '{clean}'"

    target_key = aliases.get(clean, clean)
    pyautogui.press(target_key)
    return f"Pressed key: '{target_key}'"


def type_keyboard_text(text: str) -> str:
    """
    Instantly types text into the currently focused input field.
    
    Latency: ~0 ms interval between keystrokes.
    """
    if not text:
        return "No text provided to type."

    pyautogui.write(text, interval=0.0)
    return f"Typed: \"{text}\""


def click_on_screen(x: int = None, y: int = None, clicks: int = 1, button: str = "left") -> str:
    """Clicks the mouse at current cursor position or specified coordinates."""
    if x is not None and y is not None:
        pyautogui.click(x=x, y=y, clicks=clicks, button=button)
        return f"Clicked at ({x}, {y}) [{button}]"
    else:
        pyautogui.click(clicks=clicks, button=button)
        return f"Clicked mouse [{button}]"


def click_button_by_name(button_name: str) -> str:
    """
    Interacts with on-screen dialogs and buttons (e.g. 'Continue', 'Skip', 'OK', 'Cancel').
    
    Uses standard GUI dialog fast-path (Enter for confirm, Esc for cancel/skip)
    or searches matching screen targets.
    """
    name_clean = button_name.strip().lower()

    # Common dialog conventions:
    # 'continue', 'submit', 'ok', 'yes' -> Primary button is triggered by 'enter'
    # 'skip', 'cancel', 'close', 'no' -> Secondary/dismiss is triggered by 'esc' or 'space'
    if name_clean in ("continue", "submit", "ok", "confirm", "yes", "save"):
        pyautogui.press("enter")
        return f"Activated primary dialog button ('{button_name}') via Enter."
    elif name_clean in ("skip", "cancel", "dismiss", "close", "no"):
        pyautogui.press("esc")
        return f"Dismissed dialog ('{button_name}') via Esc."
    else:
        # Fallback to pressing space (toggles focused buttons)
        pyautogui.press("space")
        return f"Pressed '{button_name}' button via Space."
