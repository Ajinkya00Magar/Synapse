"""
Data contracts for Synapse Brain (Orchestrator) and Executor.

Defines the structure of Actions, Tasks, Execution Plans, Target Locators,
Parameter Models, Execution Results, Security Policies, and System Context
using Pydantic v2 for high-performance validation and serialization.

Single source of truth between:
Voice Input → Speech-to-Text → Brain/Orchestrator → ExecutionPlan → Executor → Windows UI
"""

from __future__ import annotations

import sys
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Type, Union
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# ==============================================================================
# 1. CORE ENUMERATIONS
# ==============================================================================

class ActionType(str, Enum):
    """
    Comprehensive action taxonomy for Windows PC control.
    
    Covers Category A through Z plus Universal workflow actions and legacy aliases
    to ensure 100% backward compatibility with existing Synapse handlers.
    """

    # ── Category A: Application Control ──
    OPEN_APP = "open_app"
    CLOSE_APP = "close_app"
    RESTART_APP = "restart_app"
    FOCUS_APP = "focus_app"
    MINIMIZE_APP = "minimize_app"
    MAXIMIZE_APP = "maximize_app"
    RESTORE_APP = "restore_app"
    SWITCH_APP = "switch_app"
    KILL_APP = "kill_app"
    LAUNCH_WITH_ARGUMENTS = "launch_with_arguments"
    OPEN_FILE_WITH_APP = "open_file_with_app"
    OPEN_FOLDER_WITH_APP = "open_folder_with_app"

    # ── Category B: Window Management ──
    WINDOW_CONTROL = "window_control"  # Legacy general window control
    WINDOW_FOCUS = "window_focus"
    WINDOW_MINIMIZE = "window_minimize"
    WINDOW_MAXIMIZE = "window_maximize"
    WINDOW_RESTORE = "window_restore"
    WINDOW_CLOSE = "window_close"
    WINDOW_MOVE = "window_move"
    WINDOW_RESIZE = "window_resize"
    WINDOW_CENTER = "window_center"
    WINDOW_SNAP_LEFT = "window_snap_left"
    WINDOW_SNAP_RIGHT = "window_snap_right"
    WINDOW_SNAP_TOP = "window_snap_top"
    WINDOW_SNAP_BOTTOM = "window_snap_bottom"
    WINDOW_SNAP_TOP_LEFT = "window_snap_top_left"
    WINDOW_SNAP_TOP_RIGHT = "window_snap_top_right"
    WINDOW_SNAP_BOTTOM_LEFT = "window_snap_bottom_left"
    WINDOW_SNAP_BOTTOM_RIGHT = "window_snap_bottom_right"
    WINDOW_MOVE_TO_MONITOR = "window_move_to_monitor"
    WINDOW_RESIZE_TO_PRESET = "window_resize_to_preset"
    WINDOW_ALWAYS_ON_TOP = "window_always_on_top"
    WINDOW_FULLSCREEN = "window_fullscreen"
    WINDOW_EXIT_FULLSCREEN = "window_exit_fullscreen"
    WINDOW_SWITCH_NEXT = "window_switch_next"
    WINDOW_SWITCH_PREVIOUS = "window_switch_previous"
    ALT_TAB = "alt_tab"
    WIN_TAB = "win_tab"
    WINDOW_LIST = "window_list"
    WINDOW_FIND = "window_find"

    # ── Category C: Mouse Control ──
    MOUSE_MOVE = "mouse_move"
    MOUSE_CLICK = "mouse_click"
    MOUSE_DOUBLE_CLICK = "mouse_double_click"
    MOUSE_TRIPLE_CLICK = "mouse_triple_click"
    MOUSE_RIGHT_CLICK = "mouse_right_click"
    MOUSE_MIDDLE_CLICK = "mouse_middle_click"
    MOUSE_DRAG = "mouse_drag"
    MOUSE_DROP = "mouse_drop"
    MOUSE_DOWN = "mouse_down"
    MOUSE_UP = "mouse_up"
    MOUSE_SCROLL = "mouse_scroll"
    MOUSE_HORIZONTAL_SCROLL = "mouse_horizontal_scroll"
    MOUSE_MOVE_RELATIVE = "mouse_move_relative"
    MOUSE_CLICK_CURRENT = "mouse_click_current"
    MOUSE_DRAG_FROM_TO = "mouse_drag_from_to"
    MOUSE_LOCATE = "mouse_locate"
    MOUSE_POSITION = "mouse_position"

    # ── Category D: Keyboard Control ──
    KEY_PRESS = "key_press"
    KEY_RELEASE = "key_release"
    KEY_DOWN = "key_down"
    KEY_UP = "key_up"
    HOTKEY = "hotkey"
    TYPE_TEXT_SLOW = "type_text_slow"
    TYPE_TEXT_FAST = "type_text_fast"
    PASTE_TEXT = "paste_text"
    COPY = "copy"
    CUT = "cut"
    SELECT_ALL = "select_all"
    UNDO = "undo"
    REDO = "redo"
    BACKSPACE = "backspace"
    DELETE = "delete"
    ENTER = "enter"
    ESCAPE = "escape"
    TAB = "tab"
    SHIFT_TAB = "shift_tab"
    SPACE = "space"
    ARROW_UP = "arrow_up"
    ARROW_DOWN = "arrow_down"
    ARROW_LEFT = "arrow_left"
    ARROW_RIGHT = "arrow_right"
    HOME = "home"
    END = "end"
    PAGE_UP = "page_up"
    PAGE_DOWN = "page_down"
    INSERT = "insert"
    PRINT_SCREEN = "print_screen"
    CAPS_LOCK = "caps_lock"
    NUM_LOCK = "num_lock"
    SCROLL_LOCK = "scroll_lock"
    FUNCTION_KEY = "function_key"
    WINDOWS_KEY = "windows_key"
    ALT_KEY = "alt_key"
    CONTROL_KEY = "control_key"
    SHIFT_KEY = "shift_key"

    # ── Category E: Text / Input Control ──
    TYPE_TEXT = "type_text"
    TYPE_MULTILINE_TEXT = "type_multiline_text"
    TYPE_PASSWORD = "type_password"
    CLEAR_FIELD = "clear_field"
    SELECT_TEXT = "select_text"
    SELECT_WORD = "select_word"
    SELECT_LINE = "select_line"
    SELECT_ALL_TEXT = "select_all_text"
    REPLACE_SELECTION = "replace_selection"
    APPEND_TEXT = "append_text"
    PREPEND_TEXT = "prepend_text"
    PASTE_CLIPBOARD = "paste_clipboard"
    COPY_SELECTION = "copy_selection"
    CUT_SELECTION = "cut_selection"

    # ── Category F: Clipboard Control ──
    CLIPBOARD_READ = "clipboard_read"
    CLIPBOARD_SET = "clipboard_set"
    CLIPBOARD_CLEAR = "clipboard_clear"
    CLIPBOARD_COPY = "clipboard_copy"
    CLIPBOARD_CUT = "clipboard_cut"
    CLIPBOARD_PASTE = "clipboard_paste"
    CLIPBOARD_HISTORY = "clipboard_history"
    CLIPBOARD_SELECT_ITEM = "clipboard_select_item"

    # ── Category G: Windows System Control ──
    SYSTEM_SHUTDOWN = "system_shutdown"
    SYSTEM_RESTART = "system_restart"
    SYSTEM_SLEEP = "system_sleep"
    SYSTEM_HIBERNATE = "system_hibernate"
    SYSTEM_LOCK = "system_lock"
    SYSTEM_LOGOUT = "system_logout"
    SYSTEM_SIGN_OUT = "system_sign_out"
    SYSTEM_CANCEL_SHUTDOWN = "system_cancel_shutdown"
    SYSTEM_SCREEN_OFF = "system_screen_off"
    SYSTEM_WAKE = "system_wake"
    SYSTEM_REBOOT = "system_reboot"
    SYSTEM_STARTUP_APPS = "system_startup_apps"
    SYSTEM_TASK_MANAGER = "system_task_manager"

    # ── Category H: Volume / Audio Control ──
    SYSTEM_VOLUME = "system_volume"  # Legacy volume control
    VOLUME_GET = "volume_get"
    VOLUME_SET = "volume_set"
    VOLUME_UP = "volume_up"
    VOLUME_DOWN = "volume_down"
    VOLUME_MUTE = "volume_mute"
    VOLUME_UNMUTE = "volume_unmute"
    VOLUME_TOGGLE_MUTE = "volume_toggle_mute"
    MEDIA_PLAY = "media_play"
    MEDIA_PAUSE = "media_pause"
    MEDIA_PLAY_PAUSE = "media_play_pause"
    MEDIA_NEXT = "media_next"
    MEDIA_PREVIOUS = "media_previous"
    MEDIA_STOP = "media_stop"
    MEDIA_FAST_FORWARD = "media_fast_forward"
    MEDIA_REWIND = "media_rewind"
    AUDIO_OUTPUT_GET = "audio_output_get"
    AUDIO_OUTPUT_SET = "audio_output_set"
    AUDIO_DEVICE_LIST = "audio_device_list"
    MICROPHONE_MUTE = "microphone_mute"
    MICROPHONE_UNMUTE = "microphone_unmute"
    MICROPHONE_TOGGLE = "microphone_toggle"
    MICROPHONE_VOLUME_SET = "microphone_volume_set"
    MICROPHONE_VOLUME_UP = "microphone_volume_up"
    MICROPHONE_VOLUME_DOWN = "microphone_volume_down"

    # ── Category I: Display / Monitor Control ──
    SYSTEM_BRIGHTNESS = "system_brightness"  # Legacy brightness control
    BRIGHTNESS_GET = "brightness_get"
    BRIGHTNESS_SET = "brightness_set"
    BRIGHTNESS_UP = "brightness_up"
    BRIGHTNESS_DOWN = "brightness_down"
    DISPLAY_LIST = "display_list"
    DISPLAY_SWITCH = "display_switch"
    DISPLAY_PRIMARY_SET = "display_primary_set"
    DISPLAY_RESOLUTION_SET = "display_resolution_set"
    DISPLAY_ORIENTATION_SET = "display_orientation_set"
    DISPLAY_SCALE_SET = "display_scale_set"
    DISPLAY_DUPLICATE = "display_duplicate"
    DISPLAY_EXTEND = "display_extend"
    DISPLAY_SECOND_SCREEN_ONLY = "display_second_screen_only"
    DISPLAY_PC_SCREEN_ONLY = "display_pc_screen_only"
    NIGHT_LIGHT_ON = "night_light_on"
    NIGHT_LIGHT_OFF = "night_light_off"
    NIGHT_LIGHT_TOGGLE = "night_light_toggle"
    HDR_ON = "hdr_on"
    HDR_OFF = "hdr_off"
    COLOR_PROFILE_SET = "color_profile_set"

    # ── Category J: Network Control ──
    WIFI_GET_STATUS = "wifi_get_status"
    WIFI_ON = "wifi_on"
    WIFI_OFF = "wifi_off"
    WIFI_TOGGLE = "wifi_toggle"
    WIFI_LIST_NETWORKS = "wifi_list_networks"
    WIFI_SCAN = "wifi_scan"
    WIFI_CONNECT = "wifi_connect"
    WIFI_DISCONNECT = "wifi_disconnect"
    WIFI_FORGET = "wifi_forget"
    WIFI_RECONNECT = "wifi_reconnect"
    BLUETOOTH_GET_STATUS = "bluetooth_get_status"
    BLUETOOTH_ON = "bluetooth_on"
    BLUETOOTH_OFF = "bluetooth_off"
    BLUETOOTH_TOGGLE = "bluetooth_toggle"
    BLUETOOTH_SCAN = "bluetooth_scan"
    BLUETOOTH_LIST_DEVICES = "bluetooth_list_devices"
    BLUETOOTH_PAIR = "bluetooth_pair"
    BLUETOOTH_CONNECT = "bluetooth_connect"
    BLUETOOTH_DISCONNECT = "bluetooth_disconnect"
    BLUETOOTH_REMOVE_DEVICE = "bluetooth_remove_device"
    AIRPLANE_MODE_ON = "airplane_mode_on"
    AIRPLANE_MODE_OFF = "airplane_mode_off"
    AIRPLANE_MODE_TOGGLE = "airplane_mode_toggle"
    NETWORK_ADAPTER_ENABLE = "network_adapter_enable"
    NETWORK_ADAPTER_DISABLE = "network_adapter_disable"
    NETWORK_ADAPTER_RESTART = "network_adapter_restart"
    NETWORK_STATUS = "network_status"

    # ── Category K: File System Control ──
    FILE_CREATE = "file_create"
    FILE_DELETE = "file_delete"
    FILE_RENAME = "file_rename"
    FILE_COPY = "file_copy"
    FILE_MOVE = "file_move"
    FILE_DUPLICATE = "file_duplicate"
    FILE_OPEN = "file_open"
    FILE_CLOSE = "file_close"
    FILE_SAVE = "file_save"
    FILE_SAVE_AS = "file_save_as"
    FILE_PRINT = "file_print"
    FILE_PROPERTIES = "file_properties"
    FILE_SEARCH = "file_search"
    FILE_FIND = "file_find"
    FILE_SELECT = "file_select"
    FILE_MULTI_SELECT = "file_multi_select"
    FOLDER_CREATE = "folder_create"
    FOLDER_DELETE = "folder_delete"
    FOLDER_RENAME = "folder_rename"
    FOLDER_COPY = "folder_copy"
    FOLDER_MOVE = "folder_move"
    FOLDER_OPEN = "folder_open"
    FOLDER_CLOSE = "folder_close"
    FOLDER_SEARCH = "folder_search"
    FOLDER_PROPERTIES = "folder_properties"
    PATH_NAVIGATE = "path_navigate"
    PATH_GO_BACK = "path_go_back"
    PATH_GO_FORWARD = "path_go_forward"
    PATH_GO_UP = "path_go_up"
    PATH_OPEN = "path_open"
    PATH_COPY = "path_copy"
    PATH_OPEN_TERMINAL = "path_open_terminal"
    ARCHIVE_CREATE = "archive_create"
    ARCHIVE_EXTRACT = "archive_extract"
    ARCHIVE_LIST = "archive_list"
    RECYCLE_BIN_OPEN = "recycle_bin_open"
    RECYCLE_BIN_EMPTY = "recycle_bin_empty"
    RECYCLE_BIN_RESTORE = "recycle_bin_restore"
    RECYCLE_BIN_DELETE_PERMANENTLY = "recycle_bin_delete_permanently"

    # ── Category L: File Search / Discovery ──
    SEARCH_FILES = "search_files"
    SEARCH_FOLDERS = "search_folders"
    SEARCH_BY_NAME = "search_by_name"
    SEARCH_BY_EXTENSION = "search_by_extension"
    SEARCH_BY_SIZE = "search_by_size"
    SEARCH_BY_DATE = "search_by_date"
    SEARCH_BY_CONTENT = "search_by_content"
    SEARCH_BY_LOCATION = "search_by_location"
    SEARCH_COMBINED = "search_combined"

    # ── Category M: Browser Control ──
    OPEN_URL = "open_url"              # Legacy browser URL open
    SEARCH_WEB = "search_web"          # Legacy search engine query
    BROWSER_OPEN = "browser_open"
    BROWSER_CLOSE = "browser_close"
    BROWSER_NEW_TAB = "browser_new_tab"
    BROWSER_CLOSE_TAB = "browser_close_tab"
    BROWSER_REOPEN_TAB = "browser_reopen_tab"
    BROWSER_SWITCH_TAB = "browser_switch_tab"
    BROWSER_NEXT_TAB = "browser_next_tab"
    BROWSER_PREVIOUS_TAB = "browser_previous_tab"
    BROWSER_DUPLICATE_TAB = "browser_duplicate_tab"
    BROWSER_REFRESH = "browser_refresh"
    BROWSER_HARD_REFRESH = "browser_hard_refresh"
    BROWSER_BACK = "browser_back"
    BROWSER_FORWARD = "browser_forward"
    BROWSER_HOME = "browser_home"
    BROWSER_GO_TO_URL = "browser_go_to_url"
    BROWSER_SEARCH = "browser_search"
    BROWSER_FIND_TEXT = "browser_find_text"
    BROWSER_ZOOM_IN = "browser_zoom_in"
    BROWSER_ZOOM_OUT = "browser_zoom_out"
    BROWSER_ZOOM_RESET = "browser_zoom_reset"
    BROWSER_FULLSCREEN = "browser_fullscreen"
    BROWSER_EXIT_FULLSCREEN = "browser_exit_fullscreen"
    BROWSER_BOOKMARK = "browser_bookmark"
    BROWSER_OPEN_BOOKMARKS = "browser_open_bookmarks"
    BROWSER_OPEN_HISTORY = "browser_open_history"
    BROWSER_CLEAR_HISTORY = "browser_clear_history"
    BROWSER_DOWNLOAD = "browser_download"
    BROWSER_CANCEL_DOWNLOAD = "browser_cancel_download"
    BROWSER_OPEN_DOWNLOADS = "browser_open_downloads"
    BROWSER_SAVE_PAGE = "browser_save_page"
    BROWSER_PRINT_PAGE = "browser_print_page"
    BROWSER_COPY_LINK = "browser_copy_link"
    BROWSER_OPEN_LINK = "browser_open_link"
    BROWSER_OPEN_LINK_NEW_TAB = "browser_open_link_new_tab"
    BROWSER_SCROLL = "browser_scroll"
    BROWSER_CLICK_TEXT = "browser_click_text"
    BROWSER_CLICK_ELEMENT = "browser_click_element"
    BROWSER_SELECT_ELEMENT = "browser_select_element"
    BROWSER_TYPE = "browser_type"
    BROWSER_SUBMIT_FORM = "browser_submit_form"

    # ── Category N: UI Automation ──
    CLICK_TEXT = "click_text"          # Legacy on-screen button/text click
    UI_FIND_ELEMENT = "ui_find_element"
    UI_CLICK_ELEMENT = "ui_click_element"
    UI_DOUBLE_CLICK_ELEMENT = "ui_double_click_element"
    UI_RIGHT_CLICK_ELEMENT = "ui_right_click_element"
    UI_HOVER_ELEMENT = "ui_hover_element"
    UI_FOCUS_ELEMENT = "ui_focus_element"
    UI_TYPE_ELEMENT = "ui_type_element"
    UI_CLEAR_ELEMENT = "ui_clear_element"
    UI_SELECT_ELEMENT = "ui_select_element"
    UI_TOGGLE_ELEMENT = "ui_toggle_element"
    UI_CHECK_ELEMENT = "ui_check_element"
    UI_UNCHECK_ELEMENT = "ui_uncheck_element"
    UI_EXPAND_ELEMENT = "ui_expand_element"
    UI_COLLAPSE_ELEMENT = "ui_collapse_element"
    UI_SCROLL_TO_ELEMENT = "ui_scroll_to_element"
    UI_DRAG_ELEMENT = "ui_drag_element"
    UI_DROP_ELEMENT = "ui_drop_element"
    UI_GET_TEXT = "ui_get_text"
    UI_GET_VALUE = "ui_get_value"
    UI_GET_STATE = "ui_get_state"
    UI_WAIT_FOR_ELEMENT = "ui_wait_for_element"
    UI_WAIT_FOR_TEXT = "ui_wait_for_text"
    UI_WAIT_FOR_WINDOW = "ui_wait_for_window"
    UI_WAIT_FOR_PROCESS = "ui_wait_for_process"

    # ── Category O: Screen / Vision Control ──
    SCREENSHOT = "screenshot"
    SCREENSHOT_REGION = "screenshot_region"
    SCREEN_RECORD_START = "screen_record_start"
    SCREEN_RECORD_STOP = "screen_record_stop"
    SCREEN_READ_TEXT = "screen_read_text"
    SCREEN_FIND_TEXT = "screen_find_text"
    SCREEN_FIND_ELEMENT = "screen_find_element"
    SCREEN_GET_PIXEL = "screen_get_pixel"
    SCREEN_ANALYZE = "screen_analyze"
    SCREEN_WAIT_FOR_CHANGE = "screen_wait_for_change"
    SCREEN_WAIT_FOR_MATCH = "screen_wait_for_match"

    # ── Category P: Windows Settings ──
    SETTINGS_OPEN = "settings_open"
    SETTINGS_SEARCH = "settings_search"
    SETTINGS_OPEN_PAGE = "settings_open_page"
    SETTINGS_TOGGLE_SETTING = "settings_toggle_setting"
    SETTINGS_SET_VALUE = "settings_set_value"

    # ── Category Q: Power / Battery ──
    BATTERY_GET = "battery_get"
    POWER_PLAN_GET = "power_plan_get"
    POWER_PLAN_SET = "power_plan_set"
    BATTERY_SAVER_ON = "battery_saver_on"
    BATTERY_SAVER_OFF = "battery_saver_off"
    BATTERY_SAVER_TOGGLE = "battery_saver_toggle"
    SCREEN_TIMEOUT_SET = "screen_timeout_set"
    SLEEP_TIMEOUT_SET = "sleep_timeout_set"

    # ── Category R: Printer / Device Control ──
    PRINTER_LIST = "printer_list"
    PRINTER_SELECT = "printer_select"
    PRINTER_DEFAULT_SET = "printer_default_set"
    PRINT_DOCUMENT = "print_document"
    PRINT_CANCEL = "print_cancel"
    PRINT_QUEUE = "print_queue"
    PRINT_PAUSE = "print_pause"
    PRINT_RESUME = "print_resume"
    PRINTER_REMOVE = "printer_remove"
    DEVICE_LIST = "device_list"
    DEVICE_CONNECT = "device_connect"
    DEVICE_DISCONNECT = "device_disconnect"
    DEVICE_ENABLE = "device_enable"
    DEVICE_DISABLE = "device_disable"
    DEVICE_PROPERTIES = "device_properties"

    # ── Category S: Application-Specific Generic Control ──
    APP_ACTION = "app_action"

    # ── Category T: Terminal / Command Execution ──
    RUN_COMMAND = "run_command"
    RUN_POWERSHELL = "run_powershell"
    RUN_CMD = "run_cmd"
    RUN_PYTHON = "run_python"
    RUN_SCRIPT = "run_script"
    RUN_BATCH = "run_batch"
    RUN_PROGRAM = "run_program"
    OPEN_TERMINAL = "open_terminal"
    OPEN_POWERSHELL = "open_powershell"
    OPEN_CMD = "open_cmd"
    EXECUTE_SEQUENCE = "execute_sequence"

    # ── Category U: Process / Task Control ──
    PROCESS_LIST = "process_list"
    PROCESS_FIND = "process_find"
    PROCESS_START = "process_start"
    PROCESS_STOP = "process_stop"
    PROCESS_RESTART = "process_restart"
    PROCESS_SUSPEND = "process_suspend"
    PROCESS_RESUME = "process_resume"
    PROCESS_PRIORITY_SET = "process_priority_set"
    PROCESS_DETAILS = "process_details"
    TASK_MANAGER_OPEN = "task_manager_open"

    # ── Category V: Windows Explorer Control ──
    EXPLORER_OPEN = "explorer_open"
    EXPLORER_NEW_WINDOW = "explorer_new_window"
    EXPLORER_CLOSE = "explorer_close"
    EXPLORER_NAVIGATE = "explorer_navigate"
    EXPLORER_GO_BACK = "explorer_go_back"
    EXPLORER_GO_FORWARD = "explorer_go_forward"
    EXPLORER_GO_UP = "explorer_go_up"
    EXPLORER_SEARCH = "explorer_search"
    EXPLORER_SORT = "explorer_sort"
    EXPLORER_GROUP = "explorer_group"
    EXPLORER_VIEW_SET = "explorer_view_set"
    EXPLORER_SELECT = "explorer_select"
    EXPLORER_SELECT_ALL = "explorer_select_all"
    EXPLORER_COPY = "explorer_copy"
    EXPLORER_CUT = "explorer_cut"
    EXPLORER_PASTE = "explorer_paste"
    EXPLORER_RENAME = "explorer_rename"
    EXPLORER_DELETE = "explorer_delete"
    EXPLORER_PROPERTIES = "explorer_properties"

    # ── Category W: Notifications ──
    NOTIFICATIONS_OPEN = "notifications_open"
    NOTIFICATIONS_CLEAR = "notifications_clear"
    NOTIFICATIONS_DISMISS = "notifications_dismiss"
    NOTIFICATIONS_FOCUS_ASSIST_ON = "notifications_focus_assist_on"
    NOTIFICATIONS_FOCUS_ASSIST_OFF = "notifications_focus_assist_off"
    NOTIFICATIONS_DO_NOT_DISTURB_ON = "notifications_do_not_disturb_on"
    NOTIFICATIONS_DO_NOT_DISTURB_OFF = "notifications_do_not_disturb_off"

    # ── Category X: Virtual Desktops ──
    DESKTOP_CREATE = "desktop_create"
    DESKTOP_DELETE = "desktop_delete"
    DESKTOP_SWITCH = "desktop_switch"
    DESKTOP_NEXT = "desktop_next"
    DESKTOP_PREVIOUS = "desktop_previous"
    DESKTOP_MOVE_WINDOW = "desktop_move_window"
    DESKTOP_LIST = "desktop_list"

    # ── Category Y: Screenshot / Recording ──
    SCREENSHOT_FULL = "screenshot_full"
    SCREENSHOT_WINDOW = "screenshot_window"
    SCREENSHOT_SAVE = "screenshot_save"
    SCREENSHOT_COPY = "screenshot_copy"

    # ── Category Z: Accessibility ──
    ACCESSIBILITY_OPEN = "accessibility_open"
    NARRATOR_ON = "narrator_on"
    NARRATOR_OFF = "narrator_off"
    MAGNIFIER_ON = "magnifier_on"
    MAGNIFIER_OFF = "magnifier_off"
    MAGNIFIER_ZOOM_IN = "magnifier_zoom_in"
    MAGNIFIER_ZOOM_OUT = "magnifier_zoom_out"
    HIGH_CONTRAST_ON = "high_contrast_on"
    HIGH_CONTRAST_OFF = "high_contrast_off"
    STICKY_KEYS_ON = "sticky_keys_on"
    STICKY_KEYS_OFF = "sticky_keys_off"
    FILTER_KEYS_ON = "filter_keys_on"
    FILTER_KEYS_OFF = "filter_keys_off"
    TOGGLE_KEYS_ON = "toggle_keys_on"
    TOGGLE_KEYS_OFF = "toggle_keys_off"

    # ── Category Universal: Workflow & Flow Control ──
    WAIT = "wait"
    WAIT_FOR = "wait_for"
    CONDITION_CHECK = "condition_check"
    RETRY = "retry"
    REPEAT = "repeat"
    LOOP = "loop"
    IF_CONDITION = "if_condition"
    ELSE = "else"
    ABORT_PLAN = "abort_plan"
    PAUSE_PLAN = "pause_plan"
    RESUME_PLAN = "resume_plan"
    ASK_USER = "ask_user"
    CONFIRM_ACTION = "confirm_action"
    NOTIFY_USER = "notify_user"
    SPEAK = "speak"
    LOG = "log"
    NO_OP = "no_op"

    # ── Assistant Lifecycle & Legacy ──
    EXIT_APP = "exit_app"
    TTS_SPEAK = "tts_speak"
    UNKNOWN = "unknown"


class TaskStatus(str, Enum):
    """Lifecycle state of an individual task."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"
    PAUSED = "paused"
    WAITING_CONFIRMATION = "waiting_confirmation"


class PlanStatus(str, Enum):
    """Overall execution lifecycle of an ExecutionPlan."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    WAITING_CONFIRMATION = "waiting_confirmation"


class RiskLevel(str, Enum):
    """Security classification for actions executed on the OS."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCode(str, Enum):
    """Standardized error codes returned by the Executor to the Brain."""
    INVALID_PARAMETERS = "invalid_parameters"
    ACTION_NOT_SUPPORTED = "action_not_supported"
    APPLICATION_NOT_FOUND = "application_not_found"
    WINDOW_NOT_FOUND = "window_not_found"
    ELEMENT_NOT_FOUND = "element_not_found"
    FILE_NOT_FOUND = "file_not_found"
    PERMISSION_DENIED = "permission_denied"
    TIMEOUT = "timeout"
    NETWORK_ERROR = "network_error"
    UI_CHANGED = "ui_changed"
    EXECUTION_ERROR = "execution_error"
    PROCESS_NOT_FOUND = "process_not_found"
    DEVICE_NOT_FOUND = "device_not_found"
    USER_CANCELLED = "user_cancelled"
    CONFIRMATION_REQUIRED = "confirmation_required"
    DEPENDENCY_FAILED = "dependency_failed"
    UNKNOWN_ERROR = "unknown_error"


class InputSource(str, Enum):
    """Origin modality of the command/request."""
    VOICE = "voice"
    TEXT = "text"
    VISION = "vision"
    KEYBOARD = "keyboard"
    API = "api"
    AUTOMATION = "automation"
    INTERNAL = "internal"


class ExecutionMode(str, Enum):
    """Execution strategy for plan tasks."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"


class CoordinateSpace(str, Enum):
    """Reference coordinate frame for screen interactions."""
    SCREEN = "screen"
    WINDOW = "window"
    ACTIVE_WINDOW = "active_window"
    RELATIVE = "relative"
    UI_ELEMENT = "ui_element"


class MouseButton(str, Enum):
    """Hardware mouse button identifiers."""
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"


class StandardLocation(str, Enum):
    """Known Windows folder locations."""
    DESKTOP = "Desktop"
    DOCUMENTS = "Documents"
    DOWNLOADS = "Downloads"
    PICTURES = "Pictures"
    VIDEOS = "Videos"
    MUSIC = "Music"
    ONEDRIVE = "OneDrive"
    HOME = "Home"
    THIS_PC = "This PC"
    NETWORK = "Network"
    RECYCLE_BIN = "Recycle Bin"


class ConditionType(str, Enum):
    """Types of system states that can be evaluated conditionally."""
    WINDOW_EXISTS = "window_exists"
    WINDOW_FOCUSED = "window_focused"
    ELEMENT_EXISTS = "element_exists"
    ELEMENT_VISIBLE = "element_visible"
    PROCESS_RUNNING = "process_running"
    FILE_EXISTS = "file_exists"
    VARIABLE_EQUALS = "variable_equals"
    CLIPBOARD_CONTAINS = "clipboard_contains"
    CUSTOM = "custom"


class ComparisonOperator(str, Enum):
    """Evaluation operator for conditions."""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    MATCHES_REGEX = "matches_regex"
    EXISTS = "exists"


# ==============================================================================
# 2. TARGET & LOCATOR MODELS
# ==============================================================================

class BoundingBox(BaseModel):
    """Rectangular bounding area on a screen or inside a window."""
    model_config = ConfigDict(extra="ignore")

    x: int = Field(description="Top-left X coordinate in pixels")
    y: int = Field(description="Top-left Y coordinate in pixels")
    width: int = Field(ge=0, description="Width in pixels")
    height: int = Field(ge=0, description="Height in pixels")


class Target(BaseModel):
    """
    Unified locator model for targeting applications, windows, UI elements, or coordinates.
    
    Enables semantic referencing (e.g. 'Click Continue in Chrome') without requiring
    brittle hard-coded pixel coordinates.
    """
    model_config = ConfigDict(extra="allow")

    text: Optional[str] = Field(default=None, description="Visible text or label on element")
    title: Optional[str] = Field(default=None, description="Full or partial window title")
    application: Optional[str] = Field(default=None, description="Application name (e.g., 'chrome')")
    process: Optional[str] = Field(default=None, description="Process name or executable (e.g., 'chrome.exe')")
    window: Optional[str] = Field(default=None, description="Window descriptor or handle")
    automation_id: Optional[str] = Field(default=None, description="Windows UI Automation ID")
    control_type: Optional[str] = Field(default=None, description="UI Control type (e.g., 'Button', 'Edit', 'Hyperlink')")
    class_name: Optional[str] = Field(default=None, description="Win32 or WPF class name")
    role: Optional[str] = Field(default=None, description="Accessibility role")
    index: Optional[int] = Field(default=None, ge=0, description="0-indexed occurrence when multiple match")
    x: Optional[int] = Field(default=None, description="X coordinate")
    y: Optional[int] = Field(default=None, description="Y coordinate")
    relative_x: Optional[int] = Field(default=None, description="Offset X from target anchor")
    relative_y: Optional[int] = Field(default=None, description="Offset Y from target anchor")
    coordinate_space: CoordinateSpace = Field(default=CoordinateSpace.SCREEN, description="Reference coordinate frame")
    bounding_box: Optional[BoundingBox] = Field(default=None, description="Expected bounding region")
    regex: Optional[str] = Field(default=None, description="Regex pattern for text or title matching")
    match_mode: str = Field(default="exact", description="'exact', 'contains', or 'regex'")


# ==============================================================================
# 3. FLOW CONTROL, CONDITIONS & RESILIENCE MODELS
# ==============================================================================

class Condition(BaseModel):
    """A conditional predicate evaluated by the Executor prior to task execution."""
    model_config = ConfigDict(extra="allow")

    type: ConditionType = Field(description="System state property to evaluate")
    operator: ComparisonOperator = Field(default=ComparisonOperator.EXISTS, description="Comparison method")
    target: Optional[Target] = Field(default=None, description="Target window/element/file to inspect")
    value: Optional[Any] = Field(default=None, description="Value to test against")
    timeout_ms: float = Field(default=2000.0, ge=0.0, description="Max time to wait for condition to become true")
    invert: bool = Field(default=False, description="If True, negates the condition result")


class RetryPolicy(BaseModel):
    """Specification for handling transient failures in UI and system interactions."""
    model_config = ConfigDict(extra="allow")

    max_retries: int = Field(default=0, ge=0, description="Maximum number of retry attempts")
    retry_delay_ms: float = Field(default=500.0, ge=0.0, description="Initial delay between attempts in milliseconds")
    backoff_factor: float = Field(default=1.0, ge=1.0, description="Exponential backoff multiplier")
    retry_on: List[ErrorCode] = Field(default_factory=list, description="Specific error codes that trigger retry")


class RollbackSpec(BaseModel):
    """Specification for reversing an action if subsequent tasks fail."""
    model_config = ConfigDict(extra="allow")

    action: ActionType = Field(description="Action to perform to undo")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters for the rollback action")
    description: Optional[str] = Field(default=None, description="Explanation of the reversal")


# ==============================================================================
# 4. ACTION PARAMETER MODELS
# ==============================================================================

class BaseActionParameters(BaseModel):
    """Base model for all action parameters. Allows extra fields for future-proofing."""
    model_config = ConfigDict(extra="allow")


# --- Category A: Application Control Parameters ---
class OpenAppParameters(BaseActionParameters):
    app_name: Optional[str] = Field(default=None, description="Name of application to launch")
    executable: Optional[str] = Field(default=None, description="Full path to executable or command")
    arguments: Optional[Union[str, List[str]]] = Field(default=None, description="Command-line arguments")
    working_directory: Optional[str] = Field(default=None, description="Working directory path")
    window_title: Optional[str] = Field(default=None, description="Expected window title")
    process_name: Optional[str] = Field(default=None, description="Expected process name")
    wait_for_window: bool = Field(default=True, description="Wait until the application window renders")
    timeout_seconds: float = Field(default=10.0, ge=0.0, description="Max seconds to wait for launch")


class CloseAppParameters(BaseActionParameters):
    app_name: Optional[str] = Field(default=None, description="Application name")
    process_name: Optional[str] = Field(default=None, description="Process name")
    window_title: Optional[str] = Field(default=None, description="Window title")
    force: bool = Field(default=False, description="Force terminate (kill) without saving")
    save_prompt: str = Field(default="discard", description="Action if prompt appears: 'save', 'discard', 'cancel'")


# --- Category B: Window Management Parameters ---
class WindowControlParameters(BaseActionParameters):
    action: Optional[str] = Field(default=None, description="Operation e.g. maximize, minimize, snap_left")
    window: Optional[Target] = Field(default=None, description="Window identifier target")
    title: Optional[str] = Field(default=None, description="Full or partial window title")
    monitor_index: Optional[int] = Field(default=None, ge=0, description="Target monitor index")
    preset: Optional[str] = Field(default=None, description="Preset dimension or snap region")
    width: Optional[int] = Field(default=None, ge=0, description="Target width in pixels")
    height: Optional[int] = Field(default=None, ge=0, description="Target height in pixels")
    x: Optional[int] = Field(default=None, description="Target X coordinate")
    y: Optional[int] = Field(default=None, description="Target Y coordinate")
    always_on_top: Optional[bool] = Field(default=None, description="Toggle or set top-most flag")


# --- Category C: Mouse Control Parameters ---
class MouseClickParameters(BaseActionParameters):
    x: Optional[int] = Field(default=None, description="Screen/window X coordinate")
    y: Optional[int] = Field(default=None, description="Screen/window Y coordinate")
    relative_x: Optional[int] = Field(default=0, description="Relative X offset")
    relative_y: Optional[int] = Field(default=0, description="Relative Y offset")
    button: MouseButton = Field(default=MouseButton.LEFT, description="Mouse button to click")
    click_count: int = Field(default=1, ge=1, le=5, description="Number of clicks (1=single, 2=double, 3=triple)")
    duration: float = Field(default=0.0, ge=0.0, description="Mouse movement duration in seconds")
    coordinate_space: CoordinateSpace = Field(default=CoordinateSpace.SCREEN, description="Coordinate system")
    target: Optional[Target] = Field(default=None, description="Semantic UI element or window to click")


class MouseMoveParameters(BaseActionParameters):
    x: Optional[int] = Field(default=None, description="Target X")
    y: Optional[int] = Field(default=None, description="Target Y")
    relative_x: Optional[int] = Field(default=0, description="Relative delta X")
    relative_y: Optional[int] = Field(default=0, description="Relative delta Y")
    duration: float = Field(default=0.0, ge=0.0, description="Duration in seconds")
    smooth: bool = Field(default=False, description="Use human-like smooth curved movement")
    coordinate_space: CoordinateSpace = Field(default=CoordinateSpace.SCREEN, description="Coordinate system")
    target: Optional[Target] = Field(default=None, description="Target anchor")


class MouseDragParameters(BaseActionParameters):
    start_x: Optional[int] = Field(default=None, description="Drag start X")
    start_y: Optional[int] = Field(default=None, description="Drag start Y")
    end_x: int = Field(description="Drop end X")
    end_y: int = Field(description="Drop end Y")
    button: MouseButton = Field(default=MouseButton.LEFT, description="Button held during drag")
    duration: float = Field(default=0.5, ge=0.0, description="Drag duration in seconds")
    coordinate_space: CoordinateSpace = Field(default=CoordinateSpace.SCREEN, description="Coordinate system")
    start_target: Optional[Target] = Field(default=None, description="Element to drag from")
    end_target: Optional[Target] = Field(default=None, description="Element to drop onto")


class MouseScrollParameters(BaseActionParameters):
    direction: str = Field(default="down", description="'up', 'down', 'left', or 'right'")
    intensity: int = Field(default=5, ge=1, description="Number of wheel clicks / steps")
    horizontal: bool = Field(default=False, description="Scroll horizontally if supported")
    smooth: bool = Field(default=False, description="Smooth animated scroll")
    target: Optional[Target] = Field(default=None, description="UI element to scroll within")


# --- Category D: Keyboard Control Parameters ---
class KeyPressParameters(BaseActionParameters):
    key: str = Field(description="Key name (e.g., 'enter', 'esc', 'tab', 'a')")
    modifiers: List[str] = Field(default_factory=list, description="Modifier keys (e.g., ['ctrl', 'shift'])")
    repeat: int = Field(default=1, ge=1, description="Number of times to press")
    delay_ms: float = Field(default=0.0, ge=0.0, description="Delay between presses in milliseconds")


class HotkeyParameters(BaseActionParameters):
    keys: Union[str, List[str]] = Field(description="Hotkey string (e.g. 'Ctrl+Shift+Esc') or list (['ctrl', 'c'])")
    delay_ms: float = Field(default=50.0, ge=0.0, description="Holding duration in milliseconds")


# --- Category E: Text / Input Control Parameters ---
class TypeTextParameters(BaseActionParameters):
    text: str = Field(default="", description="Text to type into active control")
    interval: float = Field(default=0.0, ge=0.0, description="Interval between keystrokes in seconds")
    human_like: bool = Field(default=False, description="Vary keystroke timing to mimic human typing")
    replace_existing: bool = Field(default=False, description="Clear existing field content before typing")
    press_enter_after: bool = Field(default=False, description="Send Enter key after typing completes")
    encoding: str = Field(default="utf-8", description="Character encoding")
    password: bool = Field(default=False, description="Obfuscate parameter text in telemetry logs")


# --- Category F: Clipboard Control Parameters ---
class ClipboardParameters(BaseActionParameters):
    action: Optional[str] = Field(default=None, description="'read', 'set', 'clear', 'history'")
    text: Optional[str] = Field(default=None, description="Text to write to clipboard")
    history_index: Optional[int] = Field(default=None, ge=0, description="Index in Windows clipboard history (Win+V)")
    format: str = Field(default="text", description="'text', 'image', or 'files'")


# --- Category G: Windows System Control Parameters ---
class SystemControlParameters(BaseActionParameters):
    action: Optional[str] = Field(default=None, description="shutdown, restart, sleep, hibernate, lock")
    timeout_seconds: int = Field(default=0, ge=0, description="Delay before shutdown/restart")
    force: bool = Field(default=False, description="Force close running applications without prompting")
    reason: Optional[str] = Field(default=None, description="Optional system shutdown comment")


# --- Category H: Volume / Audio Control Parameters ---
class AudioControlParameters(BaseActionParameters):
    action: Optional[str] = Field(default=None, description="'up', 'down', 'set', 'mute', 'unmute', 'toggle'")
    volume: Optional[int] = Field(default=None, ge=0, le=100, description="Target volume percentage (0-100)")
    steps: Optional[int] = Field(default=None, ge=1, description="Number of volume increment/decrement steps")
    delta: Optional[int] = Field(default=None, description="Relative percentage adjustment (+15, -10)")
    device_name: Optional[str] = Field(default=None, description="Target audio device name")
    device_id: Optional[str] = Field(default=None, description="Specific audio endpoint ID")
    app_name: Optional[str] = Field(default=None, description="Application name for per-app volume mixer")


# --- Category I: Display / Monitor Control Parameters ---
class DisplayControlParameters(BaseActionParameters):
    action: Optional[str] = Field(default=None, description="'up', 'down', 'set', 'list', 'extend', 'duplicate'")
    brightness: Optional[int] = Field(default=None, ge=0, le=100, description="Brightness percentage (0-100)")
    step: Optional[int] = Field(default=None, ge=1, le=100, description="Step increment/decrement")
    delta: Optional[int] = Field(default=None, description="Relative brightness adjustment")
    monitor_index: Optional[int] = Field(default=None, ge=0, description="Monitor index (0=primary)")
    resolution: Optional[str] = Field(default=None, description="Display resolution (e.g. '1920x1080')")
    scale: Optional[int] = Field(default=None, ge=100, le=500, description="DPI scale percentage")


# --- Category J: Network & Connectivity Parameters ---
class NetworkControlParameters(BaseActionParameters):
    action: Optional[str] = Field(default=None, description="'on', 'off', 'toggle', 'connect', 'scan', 'list'")
    adapter_name: Optional[str] = Field(default=None, description="Network adapter identifier")
    ssid: Optional[str] = Field(default=None, description="Wi-Fi network SSID")
    password: Optional[str] = Field(default=None, description="Wi-Fi security key")


class BluetoothControlParameters(BaseActionParameters):
    action: Optional[str] = Field(default=None, description="'on', 'off', 'toggle', 'scan', 'connect', 'pair'")
    device_name: Optional[str] = Field(default=None, description="Bluetooth device friendly name")
    device_address: Optional[str] = Field(default=None, description="Bluetooth MAC address")


# --- Category K & L: File System & Discovery Parameters ---
class FileOperationParameters(BaseActionParameters):
    action: Optional[str] = Field(default=None, description="'create', 'delete', 'rename', 'copy', 'move', 'open'")
    source_path: Optional[str] = Field(default=None, description="Source file or folder path")
    target_path: Optional[str] = Field(default=None, description="Destination file or folder path")
    destination_path: Optional[str] = Field(default=None, description="Alias for target_path")
    file_name: Optional[str] = Field(default=None, description="Name of file or directory")
    content: Optional[str] = Field(default=None, description="Text content to write")
    append: bool = Field(default=False, description="Append content instead of overwriting")
    encoding: str = Field(default="utf-8", description="File text encoding")
    overwrite: bool = Field(default=False, description="Allow overwriting existing files")
    recursive: bool = Field(default=False, description="Recursive deletion or copying")
    standard_location: Optional[StandardLocation] = Field(default=None, description="Standard Windows directory")


class FileSearchParameters(BaseActionParameters):
    query: Optional[str] = Field(default=None, description="Search term or file glob")
    path: Optional[str] = Field(default=None, description="Root directory to search within")
    extension: Optional[str] = Field(default=None, description="File extension filter (e.g. '.pdf', '.py')")
    min_size_bytes: Optional[int] = Field(default=None, ge=0, description="Minimum size in bytes")
    max_size_bytes: Optional[int] = Field(default=None, ge=0, description="Maximum size in bytes")
    modified_after: Optional[datetime] = Field(default=None, description="Earliest modified timestamp")
    modified_before: Optional[datetime] = Field(default=None, description="Latest modified timestamp")
    recursive: bool = Field(default=True, description="Search subdirectories recursively")
    limit: int = Field(default=20, ge=1, le=1000, description="Maximum search results to return")
    sort_by: str = Field(default="modified", description="'name', 'size', 'modified', 'created'")
    sort_order: str = Field(default="desc", description="'asc' or 'desc'")


class ArchiveParameters(BaseActionParameters):
    action: Optional[str] = Field(default=None, description="'create', 'extract', 'list'")
    archive_path: str = Field(description="Path to zip/rar/7z archive")
    destination_path: Optional[str] = Field(default=None, description="Extraction destination folder")
    files: List[str] = Field(default_factory=list, description="Files to compress")


# --- Category M: Browser Control Parameters ---
class BrowserControlParameters(BaseActionParameters):
    action: Optional[str] = Field(default=None, description="open, navigate, new_tab, search, click")
    url: Optional[str] = Field(default=None, description="Web page URL")
    query: Optional[str] = Field(default=None, description="Search term")
    engine: str = Field(default="google", description="Search provider: 'google', 'youtube', 'bing', 'duckduckgo'")
    tab_index: Optional[int] = Field(default=None, ge=0, description="0-indexed browser tab")
    selector: Optional[str] = Field(default=None, description="CSS or XPath element selector")
    text: Optional[str] = Field(default=None, description="Visible text to click or verify")
    new_tab: bool = Field(default=False, description="Open URL in new tab")
    credentials_id: Optional[str] = Field(default=None, description="Secure vault credential identifier")


# --- Category N: UI Automation Parameters ---
class UIAutomationParameters(BaseActionParameters):
    action: Optional[str] = Field(default=None, description="'click', 'hover', 'type', 'find', 'wait'")
    target: Optional[Target] = Field(default=None, description="Semantic UI element locator")
    button_name: Optional[str] = Field(default=None, description="Legacy button name parameter")
    text: Optional[str] = Field(default=None, description="Text value to enter or verify")
    value: Optional[str] = Field(default=None, description="Property value")
    wait_timeout_seconds: float = Field(default=5.0, ge=0.0, description="Max seconds to wait for element")


# --- Category O: Screen & Vision Parameters ---
class VisionParameters(BaseActionParameters):
    action: Optional[str] = Field(default=None, description="'screenshot', 'find_element', 'read_text', 'analyze'")
    target_description: Optional[str] = Field(default=None, description="Natural language description of UI element")
    region: Optional[BoundingBox] = Field(default=None, description="Sub-screen region")
    text_to_find: Optional[str] = Field(default=None, description="OCR text search target")
    confidence_threshold: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence threshold (0.0 - 1.0)")
    timeout_seconds: float = Field(default=5.0, ge=0.0, description="Max seconds to wait for visual match")
    save_path: Optional[str] = Field(default=None, description="Path to save captured image")


# --- Category P: Windows Settings Parameters ---
class SettingsParameters(BaseActionParameters):
    action: Optional[str] = Field(default=None, description="'open', 'search', 'open_page', 'toggle'")
    page: Optional[str] = Field(default=None, description="Settings page (e.g., 'bluetooth', 'display', 'sound')")
    category: Optional[str] = Field(default=None, description="Settings category")
    setting_name: Optional[str] = Field(default=None, description="Specific setting identifier")
    value: Optional[Any] = Field(default=None, description="Value to apply")


# --- Category Q: Power & Battery Parameters ---
class PowerParameters(BaseActionParameters):
    action: Optional[str] = Field(default=None, description="'get_battery', 'set_plan', 'battery_saver'")
    power_plan: Optional[str] = Field(default=None, description="Power plan ('balanced', 'high_performance')")
    timeout_minutes: Optional[int] = Field(default=None, ge=0, description="Sleep or screen timeout in minutes")


# --- Category R: Printer & Device Parameters ---
class PrinterParameters(BaseActionParameters):
    action: Optional[str] = Field(default=None, description="'list', 'print', 'cancel', 'queue'")
    printer_name: Optional[str] = Field(default=None, description="Target printer device name")
    document_path: Optional[str] = Field(default=None, description="File path to print")
    copies: int = Field(default=1, ge=1, description="Number of copies")
    orientation: str = Field(default="portrait", description="'portrait' or 'landscape'")


class DeviceParameters(BaseActionParameters):
    action: Optional[str] = Field(default=None, description="'list', 'connect', 'disconnect', 'properties'")
    device_name: Optional[str] = Field(default=None, description="Hardware device name")
    device_id: Optional[str] = Field(default=None, description="Device instance path or ID")


# --- Category S: Application-Specific Generic Parameters ---
class AppActionParameters(BaseActionParameters):
    application: str = Field(description="Target application (e.g., 'excel', 'vscode', 'spotify')")
    command: str = Field(description="Application-specific command or action identifier")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Command arguments")
    target: Optional[Target] = Field(default=None, description="Target entity inside application")
    data: Optional[Any] = Field(default=None, description="Arbitrary payload for the app command")


# --- Category T: Terminal & Shell Command Parameters ---
class CommandExecutionParameters(BaseActionParameters):
    command: str = Field(description="Command string to execute")
    arguments: List[str] = Field(default_factory=list, description="Optional command argument list")
    shell: str = Field(default="powershell", description="'powershell', 'cmd', 'bash', or 'python'")
    working_directory: Optional[str] = Field(default=None, description="Working directory")
    environment: Dict[str, str] = Field(default_factory=dict, description="Custom environment variables")
    timeout_seconds: float = Field(default=30.0, ge=0.0, description="Execution timeout in seconds")
    capture_output: bool = Field(default=True, description="Capture stdout and stderr")
    elevated: bool = Field(default=False, description="Request elevated administrator privileges")
    stdin: Optional[str] = Field(default=None, description="Input string piped into stdin")


# --- Category U: Process Control Parameters ---
class ProcessControlParameters(BaseActionParameters):
    action: Optional[str] = Field(default=None, description="'list', 'start', 'stop', 'restart', 'priority'")
    pid: Optional[int] = Field(default=None, ge=0, description="Process ID")
    process_name: Optional[str] = Field(default=None, description="Process executable name")
    priority: Optional[str] = Field(default=None, description="'idle', 'normal', 'high', 'realtime'")


# --- Category V: Windows Explorer Parameters ---
class ExplorerParameters(BaseActionParameters):
    action: Optional[str] = Field(default=None, description="'open', 'navigate', 'view_set', 'select'")
    path: Optional[str] = Field(default=None, description="Folder path to browse")
    view_mode: Optional[str] = Field(default=None, description="'details', 'large_icons', 'list', 'tiles'")
    sort_by: Optional[str] = Field(default=None, description="'name', 'date', 'type', 'size'")


# --- Category W: Notification Parameters ---
class NotificationParameters(BaseActionParameters):
    action: Optional[str] = Field(default=None, description="'open', 'clear', 'focus_assist', 'dnd'")
    title: Optional[str] = Field(default=None, description="Notification header text")
    message: Optional[str] = Field(default=None, description="Notification body text")
    mode: Optional[str] = Field(default=None, description="'priority_only', 'alarms_only', 'off'")


# --- Category X: Virtual Desktop Parameters ---
class VirtualDesktopParameters(BaseActionParameters):
    action: Optional[str] = Field(default=None, description="'create', 'switch', 'next', 'previous', 'move_window'")
    desktop_index: Optional[int] = Field(default=None, ge=0, description="0-indexed desktop number")
    desktop_name: Optional[str] = Field(default=None, description="Friendly desktop name")
    window_target: Optional[Target] = Field(default=None, description="Window to move between desktops")


# --- Category Y & Z: Screenshot & Accessibility Parameters ---
class ScreenshotParameters(BaseActionParameters):
    action: Optional[str] = Field(default=None, description="'full', 'window', 'region', 'save', 'copy'")
    save_path: Optional[str] = Field(default=None, description="File path for screenshot image")
    region: Optional[BoundingBox] = Field(default=None, description="Crop bounds")
    copy_to_clipboard: bool = Field(default=False, description="Copy image directly to clipboard")


class AccessibilityParameters(BaseActionParameters):
    action: Optional[str] = Field(default=None, description="'narrator', 'magnifier', 'high_contrast', 'sticky_keys'")
    state: Optional[bool] = Field(default=None, description="Enable (True) or disable (False)")
    zoom_level: Optional[int] = Field(default=None, ge=100, le=1600, description="Magnifier zoom percentage")


# --- Category Universal: Universal Flow Parameters ---
class WaitParameters(BaseActionParameters):
    duration_seconds: float = Field(default=1.0, ge=0.0, description="Time to pause execution in seconds")
    condition: Optional[Condition] = Field(default=None, description="Optional condition to wait for")
    timeout_seconds: float = Field(default=10.0, ge=0.0, description="Max time to wait if condition specified")


class UserInteractionParameters(BaseActionParameters):
    action: Optional[str] = Field(default=None, description="'ask', 'confirm', 'speak', 'notify'")
    message: str = Field(default="", description="Message text to display or speak to user")
    options: List[str] = Field(default_factory=list, description="Selectable options if prompting user")
    default_choice: Optional[str] = Field(default=None, description="Fallback choice on timeout")
    timeout_seconds: float = Field(default=30.0, ge=0.0, description="User response timeout in seconds")


# Registry mapping ActionType to its specialized Parameter model
ACTION_PARAM_REGISTRY: Dict[ActionType, Type[BaseActionParameters]] = {
    ActionType.OPEN_APP: OpenAppParameters,
    ActionType.CLOSE_APP: CloseAppParameters,
    ActionType.WINDOW_CONTROL: WindowControlParameters,
    ActionType.WINDOW_MOVE: WindowControlParameters,
    ActionType.WINDOW_RESIZE: WindowControlParameters,
    ActionType.WINDOW_SNAP_LEFT: WindowControlParameters,
    ActionType.WINDOW_SNAP_RIGHT: WindowControlParameters,
    ActionType.WINDOW_SNAP_TOP: WindowControlParameters,
    ActionType.WINDOW_SNAP_BOTTOM: WindowControlParameters,
    ActionType.WINDOW_SNAP_TOP_LEFT: WindowControlParameters,
    ActionType.WINDOW_SNAP_TOP_RIGHT: WindowControlParameters,
    ActionType.WINDOW_SNAP_BOTTOM_LEFT: WindowControlParameters,
    ActionType.WINDOW_SNAP_BOTTOM_RIGHT: WindowControlParameters,
    ActionType.MOUSE_CLICK: MouseClickParameters,
    ActionType.MOUSE_DOUBLE_CLICK: MouseClickParameters,
    ActionType.MOUSE_RIGHT_CLICK: MouseClickParameters,
    ActionType.MOUSE_MOVE: MouseMoveParameters,
    ActionType.MOUSE_DRAG: MouseDragParameters,
    ActionType.MOUSE_SCROLL: MouseScrollParameters,
    ActionType.KEY_PRESS: KeyPressParameters,
    ActionType.HOTKEY: HotkeyParameters,
    ActionType.TYPE_TEXT: TypeTextParameters,
    ActionType.CLIPBOARD_READ: ClipboardParameters,
    ActionType.CLIPBOARD_SET: ClipboardParameters,
    ActionType.CLIPBOARD_CLEAR: ClipboardParameters,
    ActionType.SYSTEM_SHUTDOWN: SystemControlParameters,
    ActionType.SYSTEM_RESTART: SystemControlParameters,
    ActionType.SYSTEM_SLEEP: SystemControlParameters,
    ActionType.SYSTEM_LOCK: SystemControlParameters,
    ActionType.SYSTEM_VOLUME: AudioControlParameters,
    ActionType.VOLUME_SET: AudioControlParameters,
    ActionType.VOLUME_UP: AudioControlParameters,
    ActionType.VOLUME_DOWN: AudioControlParameters,
    ActionType.VOLUME_MUTE: AudioControlParameters,
    ActionType.SYSTEM_BRIGHTNESS: DisplayControlParameters,
    ActionType.BRIGHTNESS_SET: DisplayControlParameters,
    ActionType.WIFI_CONNECT: NetworkControlParameters,
    ActionType.BLUETOOTH_CONNECT: BluetoothControlParameters,
    ActionType.FILE_CREATE: FileOperationParameters,
    ActionType.FILE_DELETE: FileOperationParameters,
    ActionType.FILE_COPY: FileOperationParameters,
    ActionType.FILE_MOVE: FileOperationParameters,
    ActionType.FILE_OPEN: FileOperationParameters,
    ActionType.SEARCH_FILES: FileSearchParameters,
    ActionType.OPEN_URL: BrowserControlParameters,
    ActionType.SEARCH_WEB: BrowserControlParameters,
    ActionType.BROWSER_OPEN: BrowserControlParameters,
    ActionType.BROWSER_GO_TO_URL: BrowserControlParameters,
    ActionType.CLICK_TEXT: UIAutomationParameters,
    ActionType.UI_CLICK_ELEMENT: UIAutomationParameters,
    ActionType.UI_FIND_ELEMENT: UIAutomationParameters,
    ActionType.SCREENSHOT: ScreenshotParameters,
    ActionType.SETTINGS_OPEN: SettingsParameters,
    ActionType.SETTINGS_OPEN_PAGE: SettingsParameters,
    ActionType.APP_ACTION: AppActionParameters,
    ActionType.RUN_COMMAND: CommandExecutionParameters,
    ActionType.RUN_POWERSHELL: CommandExecutionParameters,
    ActionType.PROCESS_START: ProcessControlParameters,
    ActionType.PROCESS_STOP: ProcessControlParameters,
    ActionType.EXPLORER_OPEN: ExplorerParameters,
    ActionType.NOTIFICATIONS_OPEN: NotificationParameters,
    ActionType.DESKTOP_SWITCH: VirtualDesktopParameters,
    ActionType.WAIT: WaitParameters,
    ActionType.ASK_USER: UserInteractionParameters,
    ActionType.CONFIRM_ACTION: UserInteractionParameters,
    ActionType.TTS_SPEAK: UserInteractionParameters,
}


# ==============================================================================
# 5. OBSERVABILITY & EXECUTION RESULT MODELS
# ==============================================================================

class TaskTelemetry(BaseModel):
    """Execution telemetry captured by the Executor for a Task."""
    model_config = ConfigDict(extra="allow")

    started_at: Optional[datetime] = Field(default=None, description="Task start timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="Task finish timestamp")
    duration_ms: float = Field(default=0.0, ge=0.0, description="Duration in milliseconds")
    executor_id: Optional[str] = Field(default=None, description="Identifier of the executing worker/thread")
    attempt_count: int = Field(default=1, ge=1, description="Number of execution attempts made")
    logs: List[str] = Field(default_factory=list, description="Real-time log entries emitted during execution")
    debug_data: Dict[str, Any] = Field(default_factory=dict, description="Low-level diagnostic metrics")


class ExecutionResult(BaseModel):
    """
    Standardized structured outcome produced by the Executor.
    
    Replaces brittle raw strings with a rich payload including status, structured data,
    standard error codes, process outputs, duration, and produced artifacts/screenshots.
    """
    model_config = ConfigDict(extra="allow")

    success: bool = Field(description="True if the action succeeded without errors")
    message: Optional[str] = Field(default=None, description="Human-readable outcome summary")
    data: Dict[str, Any] = Field(default_factory=dict, description="Structured returned data (e.g. search hits, text)")
    error_code: Optional[ErrorCode] = Field(default=None, description="Standardized error category on failure")
    error_message: Optional[str] = Field(default=None, description="Detailed diagnostic error message")
    stdout: Optional[str] = Field(default=None, description="Standard output captured from process/command")
    stderr: Optional[str] = Field(default=None, description="Standard error captured from process/command")
    duration_ms: float = Field(default=0.0, ge=0.0, description="Execution time in milliseconds")
    timestamp: datetime = Field(default_factory=datetime.now, description="Completion timestamp")
    artifacts: List[str] = Field(default_factory=list, description="File paths or URIs created by this task")
    screenshots: List[str] = Field(default_factory=list, description="File paths to screenshots captured for verification")


# ==============================================================================
# 6. TASK MODEL (ATOMIC UNIT OF WORK)
# ==============================================================================

class Task(BaseModel):
    """
    An atomic unit of work in an execution plan.
    
    Fully backward-compatible with original Synapse tasks (parameters dict access,
    result/error string fields) while providing enterprise capabilities:
    - Typed parameter validation & access
    - Dependency chaining (depends_on)
    - Pre-execution condition evaluation
    - Security & confirmation metadata
    - Reversibility and rollback actions
    - Retry policies and rich telemetry
    """
    model_config = ConfigDict(extra="allow")

    id: str = Field(description="Unique task identifier, e.g. 'task_1'")
    action: ActionType = Field(description="The type of action to execute")
    description: str = Field(description="Human-readable explanation of what this step does")
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters dictionary required by the action handler"
    )
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Current execution state")
    result: Optional[str] = Field(default=None, description="Legacy string summary produced upon completion")
    error: Optional[str] = Field(default=None, description="Legacy error message if task failed")
    execution_result: Optional[ExecutionResult] = Field(default=None, description="Structured outcome model")

    # Dependency & Control Flow
    depends_on: List[str] = Field(default_factory=list, description="IDs of tasks that must succeed before this runs")
    condition: Optional[Condition] = Field(default=None, description="Optional condition required before execution")

    # Security & Safety
    risk_level: RiskLevel = Field(default=RiskLevel.LOW, description="Safety and impact classification")
    requires_confirmation: bool = Field(default=False, description="Requires user consent before execution")
    confirmation_message: Optional[str] = Field(default=None, description="Prompt shown to user for confirmation")
    requires_elevation: bool = Field(default=False, description="Requires Windows Administrator privileges (UAC)")
    is_destructive: bool = Field(default=False, description="Deletes, overwrites, or permanently alters state")
    is_irreversible: bool = Field(default=False, description="Cannot be undone by normal automated methods")

    # Resilience & Rollback
    reversible: bool = Field(default=False, description="Indicates if this action supports rollback")
    rollback_action: Optional[Dict[str, Any]] = Field(default=None, description="Specification to undo this task")
    idempotent: bool = Field(default=False, description="Safe to execute repeatedly without changing outcome")
    retry_policy: Optional[RetryPolicy] = Field(default=None, description="Custom retry policy on failure")

    # Observability
    telemetry: Optional[TaskTelemetry] = Field(default=None, description="Execution performance telemetry")

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Task ID cannot be empty.")
        return v.strip()

    @field_validator("parameters", mode="before")
    @classmethod
    def convert_parameters(cls, v: Any) -> Dict[str, Any]:
        """Supports passing either a raw dict or a typed BaseActionParameters instance."""
        if isinstance(v, BaseModel):
            return v.model_dump(exclude_unset=False)
        if v is None:
            return {}
        if not isinstance(v, dict):
            raise ValueError("Task parameters must be a dictionary or ActionParameters model.")
        return v

    def get_typed_parameters(self) -> Optional[BaseActionParameters]:
        """
        Instantiates and validates the strongly-typed parameter model registered for this task's action.
        Returns None if no specialized parameter model is registered.
        """
        param_cls = ACTION_PARAM_REGISTRY.get(self.action)
        if param_cls:
            return param_cls(**self.parameters)
        return None


# ==============================================================================
# 7. SYSTEM CONTEXT MODELS
# ==============================================================================

class WindowInfo(BaseModel):
    """Information regarding a desktop window."""
    model_config = ConfigDict(extra="allow")

    handle: Optional[int] = Field(default=None, description="HWND window handle")
    title: str = Field(default="", description="Window title bar text")
    application: str = Field(default="", description="Parent application name")
    process_id: Optional[int] = Field(default=None, description="Process ID (PID)")
    bounds: Optional[BoundingBox] = Field(default=None, description="Window screen bounds")
    is_active: bool = Field(default=False, description="True if window currently has focus")
    is_minimized: bool = Field(default=False, description="True if window is minimized")
    is_maximized: bool = Field(default=False, description="True if window is maximized")


class DisplayInfo(BaseModel):
    """Information regarding a connected monitor/display."""
    model_config = ConfigDict(extra="allow")

    index: int = Field(ge=0, description="Display index (0 = primary)")
    name: str = Field(default="", description="Display device name")
    resolution: str = Field(default="1920x1080", description="Display resolution")
    is_primary: bool = Field(default=False, description="Is primary monitor")
    scale_factor: float = Field(default=1.0, ge=1.0, description="DPI scaling factor")
    bounds: Optional[BoundingBox] = Field(default=None, description="Monitor virtual desktop bounds")


class AudioDeviceInfo(BaseModel):
    """Information regarding an audio endpoint."""
    model_config = ConfigDict(extra="allow")

    name: str = Field(description="Device friendly name")
    id: str = Field(description="Audio endpoint device ID")
    is_default: bool = Field(default=False, description="Is default system device")
    is_muted: bool = Field(default=False, description="Is currently muted")
    volume_percent: int = Field(default=50, ge=0, le=100, description="Current volume (0-100)")
    is_input: bool = Field(default=False, description="True if microphone, False if speaker/headphones")


class NetworkInfo(BaseModel):
    """Current network connectivity status."""
    model_config = ConfigDict(extra="allow")

    is_connected: bool = Field(default=True, description="Internet or LAN connected")
    connection_type: str = Field(default="wifi", description="'wifi', 'ethernet', 'cellular', 'disconnected'")
    active_ssid: Optional[str] = Field(default=None, description="Connected Wi-Fi SSID")
    ip_address: Optional[str] = Field(default=None, description="Local IP address")


class SystemContext(BaseModel):
    """
    Snapshot of Windows operating environment when intent is analyzed or executed.
    
    Provides the Brain with situational awareness so conversational commands like:
    - 'Close this window'
    - 'Type it here'
    - 'Switch to the previous application'
    can be resolved deterministically without human coordinate entry.
    """
    model_config = ConfigDict(extra="allow")

    active_application: Optional[str] = Field(default=None, description="Currently active foreground application")
    active_window: Optional[WindowInfo] = Field(default=None, description="Currently focused window")
    mouse_position: Optional[Dict[str, int]] = Field(default=None, description="Current cursor coordinates {'x': x, 'y': y}")
    keyboard_focus: Optional[Target] = Field(default=None, description="UI element currently holding keyboard focus")
    clipboard_text: Optional[str] = Field(default=None, description="Current plain text in clipboard")
    open_applications: List[str] = Field(default_factory=list, description="Names of currently running user applications")
    open_windows: List[WindowInfo] = Field(default_factory=list, description="Visible desktop windows")
    displays: List[DisplayInfo] = Field(default_factory=list, description="Attached monitors")
    audio_devices: List[AudioDeviceInfo] = Field(default_factory=list, description="Configured audio playback/recording devices")
    network: Optional[NetworkInfo] = Field(default=None, description="Network status")
    bluetooth_devices: List[str] = Field(default_factory=list, description="Connected Bluetooth devices")
    current_directory: Optional[str] = Field(default=None, description="Active working directory or Explorer path")
    selected_file: Optional[str] = Field(default=None, description="Currently highlighted file in Explorer")
    selected_ui_element: Optional[Target] = Field(default=None, description="Currently selected UI element")
    captured_at: datetime = Field(default_factory=datetime.now, description="Timestamp when context was captured")


# ==============================================================================
# 8. EXECUTION PLAN MODEL
# ==============================================================================

class ExecutionPlan(BaseModel):
    """
    An ordered execution plan created by the Brain (Orchestrator) for the Executor.
    
    Contains the full graph of atomic tasks, execution mode, priority, safety metadata,
    and optional system context.
    """
    model_config = ConfigDict(extra="allow")

    plan_id: str = Field(description="Unique identifier for this plan")
    user_prompt: str = Field(description="Original transcribed speech or text input from user")
    language: str = Field(default="en", description="Language code of the original command (e.g. 'en', 'hi', 'mr')")
    created_at: datetime = Field(default_factory=datetime.now, description="Timestamp when plan was generated")
    tasks: List[Task] = Field(default_factory=list, description="Ordered sequence of tasks to execute")
    priority: int = Field(default=50, ge=1, le=100, description="Plan priority (1=lowest, 100=highest/emergency)")
    source: InputSource = Field(default=InputSource.VOICE, description="Input modality that triggered this plan")
    execution_mode: ExecutionMode = Field(default=ExecutionMode.SEQUENTIAL, description="Sequential, parallel, or conditional")
    requires_confirmation: bool = Field(default=False, description="True if any task in plan requires explicit confirmation")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Intent parsing confidence score (0.0 - 1.0)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary orchestrator metadata or state")
    context: Optional[SystemContext] = Field(default=None, description="System context snapshot at time of planning")
    timeout_seconds: Optional[float] = Field(default=None, ge=0.0, description="Total plan execution timeout in seconds")
    allow_parallel: bool = Field(default=False, description="Flag permitting parallel task execution where safe")
    rollback_enabled: bool = Field(default=False, description="Attempt automatic rollback of completed tasks if a task fails")
    status: PlanStatus = Field(default=PlanStatus.PENDING, description="Overall plan status")
    completed_at: Optional[datetime] = Field(default=None, description="Timestamp when plan execution completed")

    @field_validator("tasks")
    @classmethod
    def validate_tasks_integrity(cls, tasks: List[Task]) -> List[Task]:
        """Ensures all task IDs are unique and dependencies refer to existing preceding tasks."""
        seen_ids: Set[str] = set()
        for idx, task in enumerate(tasks):
            if task.id in seen_ids:
                raise ValueError(f"Duplicate task ID detected in plan: '{task.id}' at index {idx}.")
            seen_ids.add(task.id)

        # Validate that depends_on references exist in the plan
        for task in tasks:
            for dep_id in task.depends_on:
                if dep_id not in seen_ids:
                    raise ValueError(f"Task '{task.id}' depends on non-existent task '{dep_id}'.")
                if dep_id == task.id:
                    raise ValueError(f"Task '{task.id}' cannot depend on itself.")

        return tasks

    @model_validator(mode="after")
    def sync_confirmation_flags(self) -> ExecutionPlan:
        """Sets requires_confirmation on the plan if any task requires confirmation."""
        if any(t.requires_confirmation for t in self.tasks):
            self.requires_confirmation = True
        return self
