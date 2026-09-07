"""
Comprehensive unit tests for the expanded Synapse Brain schema.

Validates:
1. Enumeration completeness (Categories A-Z, Universal actions, and legacy compatibility)
2. Target & Locator models
3. Parameter models validation (bounds, defaults, and typed conversions)
4. Task lifecycle, security metadata, dependencies, and retry policies
5. ExecutionResult & telemetry structured reporting
6. SystemContext snapshot modeling
7. ExecutionPlan graph validation (uniqueness, dependencies, cycle detection, confirmation bubbling)
8. Five complex real-world voice command execution plans requested in specification.
"""

import json
import unittest
from datetime import datetime, timedelta
from pydantic import ValidationError

from Brain.schema import (
    ActionType,
    TaskStatus,
    PlanStatus,
    RiskLevel,
    ErrorCode,
    InputSource,
    CoordinateSpace,
    MouseButton,
    StandardLocation,
    ConditionType,
    ComparisonOperator,
    BoundingBox,
    Target,
    Condition,
    RetryPolicy,
    RollbackSpec,
    BaseActionParameters,
    OpenAppParameters,
    CloseAppParameters,
    WindowControlParameters,
    MouseClickParameters,
    MouseMoveParameters,
    MouseDragParameters,
    MouseScrollParameters,
    KeyPressParameters,
    HotkeyParameters,
    TypeTextParameters,
    ClipboardParameters,
    SystemControlParameters,
    AudioControlParameters,
    DisplayControlParameters,
    NetworkControlParameters,
    BluetoothControlParameters,
    FileOperationParameters,
    FileSearchParameters,
    BrowserControlParameters,
    UIAutomationParameters,
    VisionParameters,
    SettingsParameters,
    PowerParameters,
    CommandExecutionParameters,
    ProcessControlParameters,
    ExplorerParameters,
    NotificationParameters,
    VirtualDesktopParameters,
    ScreenshotParameters,
    AccessibilityParameters,
    WaitParameters,
    UserInteractionParameters,
    TaskTelemetry,
    ExecutionResult,
    Task,
    WindowInfo,
    DisplayInfo,
    AudioDeviceInfo,
    NetworkInfo,
    SystemContext,
    ExecutionPlan,
    ACTION_PARAM_REGISTRY,
)


class TestSchemaComprehensive(unittest.TestCase):

    # ──────────────────────────────────────────────────────────────────────────
    # 1. ENUMS & REGISTRY
    # ──────────────────────────────────────────────────────────────────────────

    def test_enums_completeness(self):
        """Verify presence of key action types across major categories."""
        # Category A: App
        self.assertEqual(ActionType.OPEN_APP.value, "open_app")
        self.assertEqual(ActionType.CLOSE_APP.value, "close_app")
        self.assertEqual(ActionType.KILL_APP.value, "kill_app")

        # Category B: Window
        self.assertEqual(ActionType.WINDOW_MAXIMIZE.value, "window_maximize")
        self.assertEqual(ActionType.WINDOW_SNAP_TOP_RIGHT.value, "window_snap_top_right")

        # Category C: Mouse
        self.assertEqual(ActionType.MOUSE_CLICK.value, "mouse_click")
        self.assertEqual(ActionType.MOUSE_DRAG.value, "mouse_drag")

        # Category D: Keyboard
        self.assertEqual(ActionType.KEY_PRESS.value, "key_press")
        self.assertEqual(ActionType.HOTKEY.value, "hotkey")

        # Category E & F: Text & Clipboard
        self.assertEqual(ActionType.TYPE_TEXT.value, "type_text")
        self.assertEqual(ActionType.CLIPBOARD_READ.value, "clipboard_read")

        # Category G: System
        self.assertEqual(ActionType.SYSTEM_SHUTDOWN.value, "system_shutdown")
        self.assertEqual(ActionType.SYSTEM_LOCK.value, "system_lock")

        # Category H & I: Audio & Display
        self.assertEqual(ActionType.VOLUME_SET.value, "volume_set")
        self.assertEqual(ActionType.BRIGHTNESS_SET.value, "brightness_set")

        # Category J: Network
        self.assertEqual(ActionType.WIFI_CONNECT.value, "wifi_connect")
        self.assertEqual(ActionType.BLUETOOTH_CONNECT.value, "bluetooth_connect")

        # Category K & L: File System & Search
        self.assertEqual(ActionType.FILE_CREATE.value, "file_create")
        self.assertEqual(ActionType.SEARCH_FILES.value, "search_files")

        # Category M: Browser
        self.assertEqual(ActionType.BROWSER_GO_TO_URL.value, "browser_go_to_url")

        # Category N: UI Automation
        self.assertEqual(ActionType.UI_CLICK_ELEMENT.value, "ui_click_element")
        self.assertEqual(ActionType.UI_FIND_ELEMENT.value, "ui_find_element")

        # Universal Actions
        self.assertEqual(ActionType.WAIT.value, "wait")
        self.assertEqual(ActionType.CONFIRM_ACTION.value, "confirm_action")
        self.assertEqual(ActionType.ASK_USER.value, "ask_user")

    def test_action_param_registry(self):
        """Ensure action parameter models are mapped in ACTION_PARAM_REGISTRY."""
        self.assertIn(ActionType.OPEN_APP, ACTION_PARAM_REGISTRY)
        self.assertEqual(ACTION_PARAM_REGISTRY[ActionType.OPEN_APP], OpenAppParameters)
        self.assertEqual(ACTION_PARAM_REGISTRY[ActionType.VOLUME_SET], AudioControlParameters)
        self.assertEqual(ACTION_PARAM_REGISTRY[ActionType.SEARCH_FILES], FileSearchParameters)

    # ──────────────────────────────────────────────────────────────────────────
    # 2. TARGET & LOCATOR MODELS
    # ──────────────────────────────────────────────────────────────────────────

    def test_target_creation(self):
        """Test Target model with semantic UI properties."""
        target = Target(
            text="Continue",
            control_type="Button",
            application="chrome",
            coordinate_space=CoordinateSpace.UI_ELEMENT,
        )
        self.assertEqual(target.text, "Continue")
        self.assertEqual(target.control_type, "Button")
        self.assertEqual(target.coordinate_space, CoordinateSpace.UI_ELEMENT)

    def test_bounding_box_validation(self):
        """Bounding box width/height must be non-negative."""
        box = BoundingBox(x=100, y=200, width=50, height=30)
        self.assertEqual(box.width, 50)
        with self.assertRaises(ValidationError):
            BoundingBox(x=100, y=200, width=-10, height=30)

    # ──────────────────────────────────────────────────────────────────────────
    # 3. PARAMETER MODELS & VALIDATION
    # ──────────────────────────────────────────────────────────────────────────

    def test_audio_parameters_validation(self):
        """Volume must be clamped between 0 and 100."""
        valid_audio = AudioControlParameters(action="set", volume=60)
        self.assertEqual(valid_audio.volume, 60)

        with self.assertRaises(ValidationError):
            AudioControlParameters(action="set", volume=150)

        with self.assertRaises(ValidationError):
            AudioControlParameters(action="set", volume=-5)

    def test_display_parameters_validation(self):
        """Brightness must be between 0 and 100."""
        valid_display = DisplayControlParameters(action="set", brightness=40)
        self.assertEqual(valid_display.brightness, 40)

        with self.assertRaises(ValidationError):
            DisplayControlParameters(action="set", brightness=101)

    def test_file_search_parameters(self):
        """File search parameter verification."""
        params = FileSearchParameters(
            path="C:\\Users\\User\\Downloads",
            extension=".pdf",
            limit=50,
            sort_by="modified",
            sort_order="desc",
        )
        self.assertEqual(params.extension, ".pdf")
        self.assertEqual(params.limit, 50)

    # ──────────────────────────────────────────────────────────────────────────
    # 4. TASK MODEL, SECURITY & CONTROL FLOW
    # ──────────────────────────────────────────────────────────────────────────

    def test_task_creation_with_dict(self):
        """Task accepts raw dictionary parameters."""
        task = Task(
            id="task_1",
            action=ActionType.OPEN_APP,
            description="Launch Notepad",
            parameters={"app_name": "notepad"},
        )
        self.assertEqual(task.parameters.get("app_name"), "notepad")
        typed = task.get_typed_parameters()
        self.assertIsInstance(typed, OpenAppParameters)
        self.assertEqual(typed.app_name, "notepad")

    def test_task_creation_with_typed_params(self):
        """Task accepts typed BaseActionParameters instance and converts to dict."""
        typed_params = OpenAppParameters(app_name="chrome", timeout_seconds=15.0)
        task = Task(
            id="task_chrome",
            action=ActionType.OPEN_APP,
            description="Launch Chrome",
            parameters=typed_params,
        )
        self.assertIsInstance(task.parameters, dict)
        self.assertEqual(task.parameters["app_name"], "chrome")
        self.assertEqual(task.parameters["timeout_seconds"], 15.0)

    def test_task_security_metadata(self):
        """Tasks can declare high risk, confirmation, and irreversibility."""
        task = Task(
            id="task_shutdown",
            action=ActionType.SYSTEM_SHUTDOWN,
            description="Shutdown computer",
            risk_level=RiskLevel.HIGH,
            requires_confirmation=True,
            confirmation_message="Are you sure you want to shut down your PC?",
            is_destructive=True,
            is_irreversible=True,
        )
        self.assertEqual(task.risk_level, RiskLevel.HIGH)
        self.assertTrue(task.requires_confirmation)
        self.assertTrue(task.is_irreversible)

    def test_task_empty_id_rejected(self):
        """Empty task IDs must be rejected."""
        with self.assertRaises(ValidationError):
            Task(id="", action=ActionType.NO_OP, description="Empty ID")

    # ──────────────────────────────────────────────────────────────────────────
    # 5. EXECUTION RESULT & TELEMETRY
    # ──────────────────────────────────────────────────────────────────────────

    def test_execution_result_structure(self):
        """ExecutionResult supports rich structured data and error codes."""
        result = ExecutionResult(
            success=True,
            message="Found 3 matching files",
            data={"files": ["report.pdf", "invoice.pdf", "notes.pdf"]},
            duration_ms=42.5,
            artifacts=["C:\\Downloads\\report.pdf"],
        )
        self.assertTrue(result.success)
        self.assertEqual(len(result.data["files"]), 3)
        self.assertEqual(result.duration_ms, 42.5)

    def test_execution_result_failure(self):
        """ExecutionResult failure captures standardized error code."""
        result = ExecutionResult(
            success=False,
            error_code=ErrorCode.APPLICATION_NOT_FOUND,
            error_message="Could not find executable for 'photoshop'",
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error_code, ErrorCode.APPLICATION_NOT_FOUND)

    # ──────────────────────────────────────────────────────────────────────────
    # 6. SYSTEM CONTEXT
    # ──────────────────────────────────────────────────────────────────────────

    def test_system_context_modeling(self):
        """SystemContext captures active app, window, display, and audio devices."""
        context = SystemContext(
            active_application="chrome",
            active_window=WindowInfo(title="Google Chrome - Work", application="chrome", is_active=True),
            clipboard_text="Copied text snippet",
            open_applications=["chrome", "spotify", "code"],
            displays=[DisplayInfo(index=0, name="Primary Monitor", resolution="2560x1440", is_primary=True)],
            audio_devices=[AudioDeviceInfo(name="Headphones (Bluetooth)", id="dev_1", is_default=True, volume_percent=55)],
        )
        self.assertEqual(context.active_application, "chrome")
        self.assertEqual(len(context.displays), 1)
        self.assertEqual(context.audio_devices[0].volume_percent, 55)

    # ──────────────────────────────────────────────────────────────────────────
    # 7. EXECUTION PLAN VALIDATION & INTEGRITY
    # ──────────────────────────────────────────────────────────────────────────

    def test_execution_plan_duplicate_task_id(self):
        """Duplicate task IDs must raise a ValidationError."""
        t1 = Task(id="t1", action=ActionType.OPEN_APP, description="Open Chrome")
        t2 = Task(id="t1", action=ActionType.KEY_PRESS, description="Press Enter")

        with self.assertRaises(ValidationError):
            ExecutionPlan(plan_id="p1", user_prompt="test", tasks=[t1, t2])

    def test_execution_plan_invalid_dependency(self):
        """A task depending on a non-existent task must fail validation."""
        t1 = Task(id="t1", action=ActionType.OPEN_APP, description="Open Chrome")
        t2 = Task(id="t2", action=ActionType.KEY_PRESS, description="Press Enter", depends_on=["non_existent_task"])

        with self.assertRaises(ValidationError):
            ExecutionPlan(plan_id="p1", user_prompt="test", tasks=[t1, t2])

    def test_execution_plan_self_dependency(self):
        """A task cannot depend on itself."""
        t1 = Task(id="t1", action=ActionType.OPEN_APP, description="Open Chrome", depends_on=["t1"])

        with self.assertRaises(ValidationError):
            ExecutionPlan(plan_id="p1", user_prompt="test", tasks=[t1])

    def test_execution_plan_confirmation_bubbling(self):
        """If any task requires confirmation, the plan's requires_confirmation becomes True."""
        t1 = Task(id="t1", action=ActionType.OPEN_APP, description="Open Notepad")
        t2 = Task(id="t2", action=ActionType.SYSTEM_SHUTDOWN, description="Shutdown", requires_confirmation=True)

        plan = ExecutionPlan(plan_id="p1", user_prompt="shutdown", tasks=[t1, t2])
        self.assertTrue(plan.requires_confirmation)

    def test_execution_plan_json_roundtrip(self):
        """ExecutionPlan serializes cleanly to JSON and deserializes back."""
        plan = ExecutionPlan(
            plan_id="plan_roundtrip",
            user_prompt="open notepad and type hello",
            language="en",
            priority=75,
            tasks=[
                Task(id="task_1", action=ActionType.OPEN_APP, description="Open Notepad", parameters={"app_name": "notepad"}),
                Task(id="task_2", action=ActionType.TYPE_TEXT, description="Type text", parameters={"text": "hello"}, depends_on=["task_1"]),
            ],
        )

        json_str = plan.model_dump_json()
        self.assertIn("plan_roundtrip", json_str)
        self.assertIn("open_app", json_str)

        restored_plan = ExecutionPlan.model_validate_json(json_str)
        self.assertEqual(restored_plan.plan_id, "plan_roundtrip")
        self.assertEqual(len(restored_plan.tasks), 2)
        self.assertEqual(restored_plan.tasks[1].depends_on, ["task_1"])

    # ──────────────────────────────────────────────────────────────────────────
    # 8. SPECIFICATION: 5 REALISTIC VOICE COMMAND EXECUTION PLANS
    # ──────────────────────────────────────────────────────────────────────────

    def test_scenario_1_youtube_and_volume(self):
        """
        Command:
        'Open Chrome, go to YouTube, search for Python tutorials,
        open the first result, maximize the window, and increase the volume to 60%.'
        """
        plan = ExecutionPlan(
            plan_id="plan_yt_py",
            user_prompt="Open Chrome, go to YouTube, search for Python tutorials, open the first result, maximize the window, and increase the volume to 60%.",
            source=InputSource.VOICE,
            language="en",
            tasks=[
                Task(
                    id="task_1",
                    action=ActionType.OPEN_APP,
                    description="Launch Google Chrome",
                    parameters=OpenAppParameters(app_name="chrome"),
                ),
                Task(
                    id="task_2",
                    action=ActionType.BROWSER_GO_TO_URL,
                    description="Navigate to YouTube",
                    parameters=BrowserControlParameters(url="https://www.youtube.com"),
                    depends_on=["task_1"],
                ),
                Task(
                    id="task_3",
                    action=ActionType.BROWSER_SEARCH,
                    description="Search for 'Python tutorials' on YouTube",
                    parameters=BrowserControlParameters(query="Python tutorials", engine="youtube"),
                    depends_on=["task_2"],
                ),
                Task(
                    id="task_4",
                    action=ActionType.UI_CLICK_ELEMENT,
                    description="Click first search result video",
                    parameters=UIAutomationParameters(
                        target=Target(control_type="Hyperlink", index=0, application="chrome")
                    ),
                    depends_on=["task_3"],
                ),
                Task(
                    id="task_5",
                    action=ActionType.WINDOW_MAXIMIZE,
                    description="Maximize Chrome window",
                    parameters=WindowControlParameters(title="YouTube"),
                    depends_on=["task_4"],
                ),
                Task(
                    id="task_6",
                    action=ActionType.VOLUME_SET,
                    description="Set system volume to 60%",
                    parameters=AudioControlParameters(action="set", volume=60),
                    idempotent=True,
                ),
            ],
        )
        self.assertEqual(len(plan.tasks), 6)
        self.assertEqual(plan.tasks[5].action, ActionType.VOLUME_SET)
        self.assertEqual(plan.tasks[5].parameters["volume"], 60)

    def test_scenario_2_create_folder_and_meeting_notes(self):
        """
        Command:
        'Create a folder called Projects on my desktop, open it,
        create a text file called notes.txt, type today's meeting notes, save it, and close Notepad.'
        """
        plan = ExecutionPlan(
            plan_id="plan_notes",
            user_prompt="Create a folder called Projects on my desktop, open it, create a text file called notes.txt, type today's meeting notes, save it, and close Notepad.",
            source=InputSource.VOICE,
            language="en",
            tasks=[
                Task(
                    id="task_1",
                    action=ActionType.FOLDER_CREATE,
                    description="Create Projects folder on Desktop",
                    parameters=FileOperationParameters(
                        standard_location=StandardLocation.DESKTOP,
                        file_name="Projects",
                    ),
                ),
                Task(
                    id="task_2",
                    action=ActionType.EXPLORER_OPEN,
                    description="Open Projects folder in Explorer",
                    parameters=ExplorerParameters(path="%USERPROFILE%\\Desktop\\Projects"),
                    depends_on=["task_1"],
                ),
                Task(
                    id="task_3",
                    action=ActionType.FILE_CREATE,
                    description="Create text file notes.txt",
                    parameters=FileOperationParameters(
                        target_path="%USERPROFILE%\\Desktop\\Projects\\notes.txt",
                        content="Meeting Notes - " + datetime.now().strftime("%Y-%m-%d"),
                    ),
                    depends_on=["task_1"],
                ),
                Task(
                    id="task_4",
                    action=ActionType.OPEN_FILE_WITH_APP,
                    description="Open notes.txt in Notepad",
                    parameters=OpenAppParameters(
                        app_name="notepad",
                        arguments=["%USERPROFILE%\\Desktop\\Projects\\notes.txt"],
                    ),
                    depends_on=["task_3"],
                ),
                Task(
                    id="task_5",
                    action=ActionType.TYPE_TEXT,
                    description="Type meeting notes content",
                    parameters=TypeTextParameters(
                        text="\n1. Discussed architecture\n2. Approved schema redesign.",
                        human_like=False,
                    ),
                    depends_on=["task_4"],
                ),
                Task(
                    id="task_6",
                    action=ActionType.HOTKEY,
                    description="Save file with Ctrl+S",
                    parameters=HotkeyParameters(keys=["ctrl", "s"]),
                    depends_on=["task_5"],
                ),
                Task(
                    id="task_7",
                    action=ActionType.CLOSE_APP,
                    description="Close Notepad",
                    parameters=CloseAppParameters(app_name="notepad"),
                    depends_on=["task_6"],
                ),
            ],
        )
        self.assertEqual(len(plan.tasks), 7)
        self.assertEqual(plan.tasks[6].action, ActionType.CLOSE_APP)

    def test_scenario_3_bluetooth_headphones(self):
        """
        Command:
        'Open Settings, go to Bluetooth, turn Bluetooth on, and connect to my headphones.'
        """
        plan = ExecutionPlan(
            plan_id="plan_bluetooth",
            user_prompt="Open Settings, go to Bluetooth, turn Bluetooth on, and connect to my headphones.",
            source=InputSource.VOICE,
            language="en",
            tasks=[
                Task(
                    id="task_1",
                    action=ActionType.SETTINGS_OPEN_PAGE,
                    description="Open Windows Settings Bluetooth page",
                    parameters=SettingsParameters(page="bluetooth"),
                ),
                Task(
                    id="task_2",
                    action=ActionType.BLUETOOTH_ON,
                    description="Turn Bluetooth on if off",
                    parameters=BluetoothControlParameters(action="on"),
                    depends_on=["task_1"],
                    idempotent=True,
                ),
                Task(
                    id="task_3",
                    action=ActionType.BLUETOOTH_CONNECT,
                    description="Connect to headphones device",
                    parameters=BluetoothControlParameters(
                        action="connect",
                        device_name="Headphones",
                    ),
                    depends_on=["task_2"],
                    retry_policy=RetryPolicy(max_retries=3, retry_delay_ms=1000.0),
                ),
            ],
        )
        self.assertEqual(len(plan.tasks), 3)
        self.assertEqual(plan.tasks[2].action, ActionType.BLUETOOTH_CONNECT)
        self.assertEqual(plan.tasks[2].retry_policy.max_retries, 3)

    def test_scenario_4_search_newest_pdf_in_downloads(self):
        """
        Command:
        'Find all PDF files in Downloads modified this week and open the newest one.'
        """
        week_ago = datetime.now() - timedelta(days=7)
        plan = ExecutionPlan(
            plan_id="plan_pdf_search",
            user_prompt="Find all PDF files in Downloads modified this week and open the newest one.",
            source=InputSource.VOICE,
            language="en",
            tasks=[
                Task(
                    id="task_1",
                    action=ActionType.SEARCH_FILES,
                    description="Search Downloads for PDFs modified in the last 7 days",
                    parameters=FileSearchParameters(
                        path="%USERPROFILE%\\Downloads",
                        extension=".pdf",
                        modified_after=week_ago,
                        sort_by="modified",
                        sort_order="desc",
                        limit=10,
                    ),
                ),
                Task(
                    id="task_2",
                    action=ActionType.FILE_OPEN,
                    description="Open the newest discovered PDF",
                    parameters=FileOperationParameters(
                        action="open",
                        target_path="{task_1.data.files[0]}",
                    ),
                    depends_on=["task_1"],
                ),
            ],
        )
        self.assertEqual(len(plan.tasks), 2)
        self.assertEqual(plan.tasks[0].action, ActionType.SEARCH_FILES)

    def test_scenario_5_gmail_attachment_and_lock(self):
        """
        Command:
        'Open Chrome, go to Gmail, maximize the window, click Compose, type an email,
        attach the newest PDF from Downloads, send it, close the browser, turn on Do Not Disturb,
        reduce the volume to 30%, and lock the computer.'
        """
        plan = ExecutionPlan(
            plan_id="plan_gmail_workflow",
            user_prompt="Open Chrome, go to Gmail, maximize the window, click Compose, type an email, attach the newest PDF from Downloads, send it, close the browser, turn on Do Not Disturb, reduce the volume to 30%, and lock the computer.",
            source=InputSource.VOICE,
            language="en",
            tasks=[
                Task(
                    id="task_1",
                    action=ActionType.OPEN_APP,
                    description="Launch Chrome",
                    parameters=OpenAppParameters(app_name="chrome"),
                ),
                Task(
                    id="task_2",
                    action=ActionType.BROWSER_GO_TO_URL,
                    description="Navigate to Gmail",
                    parameters=BrowserControlParameters(url="https://mail.google.com"),
                    depends_on=["task_1"],
                ),
                Task(
                    id="task_3",
                    action=ActionType.WINDOW_MAXIMIZE,
                    description="Maximize Chrome window",
                    parameters=WindowControlParameters(title="Gmail"),
                    depends_on=["task_2"],
                ),
                Task(
                    id="task_4",
                    action=ActionType.UI_CLICK_ELEMENT,
                    description="Click 'Compose' button",
                    parameters=UIAutomationParameters(target=Target(text="Compose", control_type="Button")),
                    depends_on=["task_3"],
                ),
                Task(
                    id="task_5",
                    action=ActionType.TYPE_TEXT,
                    description="Type email message body",
                    parameters=TypeTextParameters(text="Hello, please find the latest weekly report attached.\n\nBest regards,"),
                    depends_on=["task_4"],
                ),
                Task(
                    id="task_6",
                    action=ActionType.SEARCH_FILES,
                    description="Locate newest PDF in Downloads folder",
                    parameters=FileSearchParameters(
                        path="%USERPROFILE%\\Downloads",
                        extension=".pdf",
                        sort_by="modified",
                        sort_order="desc",
                        limit=1,
                    ),
                ),
                Task(
                    id="task_7",
                    action=ActionType.UI_CLICK_ELEMENT,
                    description="Click 'Attach files' and attach PDF",
                    parameters=UIAutomationParameters(target=Target(text="Attach files")),
                    depends_on=["task_5", "task_6"],
                ),
                Task(
                    id="task_8",
                    action=ActionType.HOTKEY,
                    description="Send email with Ctrl+Enter shortcut",
                    parameters=HotkeyParameters(keys=["ctrl", "enter"]),
                    depends_on=["task_7"],
                ),
                Task(
                    id="task_9",
                    action=ActionType.CLOSE_APP,
                    description="Close Chrome",
                    parameters=CloseAppParameters(app_name="chrome"),
                    depends_on=["task_8"],
                ),
                Task(
                    id="task_10",
                    action=ActionType.NOTIFICATIONS_DO_NOT_DISTURB_ON,
                    description="Turn on Windows Do Not Disturb (Focus Assist)",
                    parameters=NotificationParameters(mode="priority_only"),
                    idempotent=True,
                ),
                Task(
                    id="task_11",
                    action=ActionType.VOLUME_SET,
                    description="Reduce master volume to 30%",
                    parameters=AudioControlParameters(volume=30),
                    idempotent=True,
                ),
                Task(
                    id="task_12",
                    action=ActionType.SYSTEM_LOCK,
                    description="Lock Windows PC workstation",
                    parameters=SystemControlParameters(action="lock"),
                    risk_level=RiskLevel.MEDIUM,
                    depends_on=["task_9", "task_10", "task_11"],
                ),
            ],
        )

        self.assertEqual(len(plan.tasks), 12)
        self.assertEqual(plan.tasks[11].action, ActionType.SYSTEM_LOCK)
        self.assertEqual(plan.tasks[11].depends_on, ["task_9", "task_10", "task_11"])


if __name__ == "__main__":
    unittest.main()
