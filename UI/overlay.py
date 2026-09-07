"""
Floating HUD Status Overlay for Synapse.

A lightweight, borderless, semi-transparent status pill that hovers at the top
of the screen to show that Synapse hands-free voice automation is actively running.

Engineered with Windows WS_EX_NOACTIVATE so it NEVER steals keyboard or mouse focus
from whatever application, browser, or game the user is currently using.
"""

import sys
import time
import queue
import ctypes
import threading
import tkinter as tk

# Win32 Constants for non-activating window
GWL_EXSTYLE = -20
WS_EX_NOACTIVATE = 0x08000000
WS_EX_TOPMOST = 0x00000008
WS_EX_TOOLWINDOW = 0x00000080
user32 = ctypes.windll.user32 if sys.platform == "win32" else None


class FloatingOverlay:
    """Floating on-screen HUD indicator that hovers over Windows non-intrusively."""

    def __init__(self):
        self._queue = queue.Queue()
        self._thread = None
        self._root = None
        self._is_running = False
        self._lbl_dot = None
        self._lbl_text = None

        # Color themes for states
        self._themes = {
            "listening": {
                "dot_color": "#06b6d4",    # Cyan
                "dot_symbol": "●",
                "default_msg": "Synapse: Listening...",
            },
            "analyzing": {
                "dot_color": "#a855f7",    # Purple
                "dot_symbol": "●",
                "default_msg": "Thinking...",
            },
            "executing": {
                "dot_color": "#10b981",    # Emerald Green
                "dot_symbol": "⚡",
                "default_msg": "Executing...",
            },
            "stopped": {
                "dot_color": "#ef4444",    # Red
                "dot_symbol": "■",
                "default_msg": "Synapse: Stopped",
            },
            "idle": {
                "dot_color": "#64748b",    # Slate
                "dot_symbol": "○",
                "default_msg": "Synapse: Ready",
            },
        }

    def start(self):
        """Starts the floating overlay in a dedicated background daemon thread."""
        if self._is_running:
            return

        self._is_running = True
        self._thread = threading.Thread(target=self._run_gui, daemon=True)
        self._thread.start()

    def set_status(self, state: str = "listening", message: str = None):
        """
        Thread-safe status updater.
        
        Args:
            state: 'listening', 'analyzing', 'executing', 'stopped', 'idle'
            message: Custom message text (e.g. 'Opening YouTube')
        """
        if not self._is_running:
            return
        self._queue.put((state.lower(), message))

    def stop(self):
        """Stops and destroys the overlay window."""
        self._is_running = False
        if self._root:
            try:
                self._root.after(0, self._root.destroy)
            except Exception:
                pass

    def _run_gui(self):
        """Internal Tkinter event loop running on daemon thread."""
        self._root = tk.Tk()
        self._root.title("Synapse HUD")

        # 1. Geometry & Screen Positioning (Top-Center of Display)
        self._root.overrideredirect(True)          # Remove OS window border and title bar
        self._root.attributes("-topmost", True)    # Always stay above other windows
        try:
            self._root.attributes("-alpha", 0.92)  # Semi-transparent dark glass
        except Exception:
            pass

        screen_w = self._root.winfo_screenwidth()
        pill_width = 290
        pill_height = 38
        x = (screen_w - pill_width) // 2
        y = 12  # 12px from the top edge

        self._root.geometry(f"{pill_width}x{pill_height}+{x}+{y}")
        self._root.configure(bg="#0f172a")        # Dark slate background

        # 2. Prevent Stealing Focus on Windows (WS_EX_NOACTIVATE)
        if user32:
            self._root.update_idletasks()
            hwnd = self._root.winfo_id()
            parent = user32.GetParent(hwnd)
            target_hwnd = parent if parent else hwnd
            style = user32.GetWindowLongW(target_hwnd, GWL_EXSTYLE)
            user32.SetWindowLongW(target_hwnd, GWL_EXSTYLE, style | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW | WS_EX_TOPMOST)

        # 3. Outer Container Pill
        container = tk.Frame(self._root, bg="#1e293b", bd=1, relief="solid")
        container.pack(fill="both", expand=True, padx=2, pady=2)

        # 4. Status Dot Indicator
        self._lbl_dot = tk.Label(
            container,
            text="●",
            font=("Segoe UI", 12, "bold"),
            bg="#1e293b",
            fg="#06b6d4",
        )
        self._lbl_dot.pack(side="left", padx=(12, 6))

        # 5. Status Text Label
        self._lbl_text = tk.Label(
            container,
            text="Synapse: Listening...",
            font=("Segoe UI", 9, "bold"),
            bg="#1e293b",
            fg="#f8fafc",
            anchor="w",
        )
        self._lbl_text.pack(side="left", fill="x", expand=True)

        # 6. Periodic Queue Consumer (Every 30ms)
        self._root.after(30, self._process_queue)

        try:
            self._root.mainloop()
        except Exception:
            pass

    def _process_queue(self):
        """Processes pending status updates from background threads safely."""
        if not self._is_running:
            return

        try:
            while not self._queue.empty():
                state, msg = self._queue.get_nowait()
                theme = self._themes.get(state, self._themes["listening"])
                display_text = msg if msg else theme["default_msg"]

                # Truncate long text so it fits the pill gracefully
                if len(display_text) > 28:
                    display_text = display_text[:25] + "..."

                if self._lbl_dot and self._lbl_text:
                    self._lbl_dot.config(fg=theme["dot_color"], text=theme["dot_symbol"])
                    self._lbl_text.config(text=display_text)
        except Exception:
            pass

        if self._root and self._is_running:
            self._root.after(30, self._process_queue)
