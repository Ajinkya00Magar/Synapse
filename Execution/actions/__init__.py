"""
Action handlers module.
Exports high-performance, low-latency adapters for OS, GUI, Window, and Web control.
"""

from .system_actions import (
    launch_application,
    execute_shell_command,
    control_system_volume,
    control_system_brightness,
)
from .web_actions import (
    open_browser_url,
    search_web_engine,
)
from .gui_actions import (
    scroll_page,
    press_key_or_shortcut,
    type_keyboard_text,
    click_on_screen,
    click_button_by_name,
)
from .window_actions import (
    manage_active_window,
)

__all__ = [
    "launch_application",
    "execute_shell_command",
    "control_system_volume",
    "control_system_brightness",
    "open_browser_url",
    "search_web_engine",
    "scroll_page",
    "press_key_or_shortcut",
    "type_keyboard_text",
    "click_on_screen",
    "click_button_by_name",
    "manage_active_window",
]
