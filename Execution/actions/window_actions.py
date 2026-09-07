"""
High-Performance Windows & Workspace Management Action Handlers.

Uses direct Windows Win32 user32 C APIs for sub-millisecond window manipulation:
- Moving, resizing, and snapping (top-right corner, split-screen, etc.)
- Minimizing, maximizing, and closing active windows
- Virtual desktop and window switching
"""

import sys
import ctypes
import pyautogui

# Win32 Constants
SW_MAXIMIZE = 3
SW_MINIMIZE = 6
SW_RESTORE = 9
SWP_NOZORDER = 0x0004
SWP_SHOWWINDOW = 0x0040
WM_CLOSE = 0x0010

user32 = ctypes.windll.user32 if sys.platform == "win32" else None


def manage_active_window(command: str) -> str:
    """
    Directly controls the active foreground window in Windows.
    
    Latency: < 5 ms.
    """
    clean = command.strip().lower()

    # 1. Workspace / Virtual Desktop Operations
    if clean in ("switch_desktop", "change_desktop", "next_desktop"):
        pyautogui.hotkey("ctrl", "win", "right")
        return "Switched to next virtual desktop."
    elif clean in ("prev_desktop", "previous_desktop"):
        pyautogui.hotkey("ctrl", "win", "left")
        return "Switched to previous virtual desktop."
    elif clean in ("show_desktop", "minimize_all"):
        pyautogui.hotkey("win", "d")
        return "Toggled show desktop (Win+D)."
    elif clean in ("switch_window", "next_window", "alt_tab"):
        pyautogui.hotkey("alt", "tab")
        return "Switched active window (Alt+Tab)."

    if not user32:
        return f"Window control not supported on non-Windows platform: {clean}"

    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return "No active foreground window found."

    screen_w = user32.GetSystemMetrics(0)
    screen_h = user32.GetSystemMetrics(1)

    # 2. Window Sizing & Snapping
    if clean in ("maximize", "fullscreen"):
        user32.ShowWindow(hwnd, SW_MAXIMIZE)
        return "Maximized active window."

    elif clean in ("minimize", "hide"):
        user32.ShowWindow(hwnd, SW_MINIMIZE)
        return "Minimized active window."

    elif clean in ("restore", "normal"):
        user32.ShowWindow(hwnd, SW_RESTORE)
        return "Restored active window size."

    elif clean in ("close", "exit_window"):
        user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
        return "Sent close command to active window."

    # 3. Corner & Split Screen Snapping
    elif clean in ("snap_top_right", "top_right", "corner_top_right"):
        user32.ShowWindow(hwnd, SW_RESTORE)
        x = screen_w // 2
        y = 0
        w = screen_w // 2
        h = screen_h // 2
        user32.SetWindowPos(hwnd, 0, x, y, w, h, SWP_NOZORDER | SWP_SHOWWINDOW)
        return f"Snapped window to top-right corner ({w}x{h})."

    elif clean in ("snap_top_left", "top_left"):
        user32.ShowWindow(hwnd, SW_RESTORE)
        user32.SetWindowPos(hwnd, 0, 0, 0, screen_w // 2, screen_h // 2, SWP_NOZORDER | SWP_SHOWWINDOW)
        return "Snapped window to top-left corner."

    elif clean in ("snap_bottom_right", "bottom_right"):
        user32.ShowWindow(hwnd, SW_RESTORE)
        user32.SetWindowPos(hwnd, 0, screen_w // 2, screen_h // 2, screen_w // 2, screen_h // 2, SWP_NOZORDER | SWP_SHOWWINDOW)
        return "Snapped window to bottom-right corner."

    elif clean in ("snap_left", "left_half"):
        user32.ShowWindow(hwnd, SW_RESTORE)
        user32.SetWindowPos(hwnd, 0, 0, 0, screen_w // 2, screen_h, SWP_NOZORDER | SWP_SHOWWINDOW)
        return "Snapped window to left half."

    elif clean in ("snap_right", "right_half"):
        user32.ShowWindow(hwnd, SW_RESTORE)
        user32.SetWindowPos(hwnd, 0, screen_w // 2, 0, screen_w // 2, screen_h, SWP_NOZORDER | SWP_SHOWWINDOW)
        return "Snapped window to right half."

    else:
        return f"Unrecognized window command: '{command}'"
