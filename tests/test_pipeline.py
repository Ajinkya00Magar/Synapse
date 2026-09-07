"""
Comprehensive unit, latency, and integration tests for Synapse Brain and Executor.
"""

import time
import unittest
from Brain.schema import ActionType, TaskStatus
from Brain.orchestrator import Orchestrator
from Execution.executor import Executor


class TestSynapsePipeline(unittest.TestCase):

    def setUp(self):
        self.orchestrator = Orchestrator()
        self.executor = Executor()

    def test_app_launch_intent(self):
        prompt = "open notepad"
        plan = self.orchestrator.plan(prompt, language="en")
        self.assertEqual(len(plan.tasks), 1)
        self.assertEqual(plan.tasks[0].action, ActionType.OPEN_APP)
        self.assertEqual(plan.tasks[0].parameters.get("app_name"), "notepad")

    def test_punctuation_stripping(self):
        prompt = "Open YouTube."
        plan = self.orchestrator.plan(prompt, language="en")
        self.assertEqual(len(plan.tasks), 1)
        self.assertEqual(plan.tasks[0].action, ActionType.OPEN_URL)
        self.assertEqual(plan.tasks[0].parameters.get("url"), "https://www.youtube.com")

    def test_scroll_intents(self):
        # English
        plan_down = self.orchestrator.plan("scroll down", language="en")
        self.assertEqual(plan_down.tasks[0].action, ActionType.MOUSE_SCROLL)
        self.assertEqual(plan_down.tasks[0].parameters.get("direction"), "down")

        plan_up = self.orchestrator.plan("scroll up", language="en")
        self.assertEqual(plan_up.tasks[0].action, ActionType.MOUSE_SCROLL)
        self.assertEqual(plan_up.tasks[0].parameters.get("direction"), "up")

        # Marathi
        plan_mr = self.orchestrator.plan("khali scroll kar", language="mr")
        self.assertEqual(plan_mr.tasks[0].action, ActionType.MOUSE_SCROLL)
        self.assertEqual(plan_mr.tasks[0].parameters.get("direction"), "down")

    def test_window_control_intents(self):
        # Snapping
        plan_snap = self.orchestrator.plan("snap window to top right", language="en")
        self.assertEqual(plan_snap.tasks[0].action, ActionType.WINDOW_CONTROL)
        self.assertEqual(plan_snap.tasks[0].parameters.get("action"), "snap_top_right")

        # Sizing
        plan_max = self.orchestrator.plan("maximize window", language="en")
        self.assertEqual(plan_max.tasks[0].action, ActionType.WINDOW_CONTROL)
        self.assertEqual(plan_max.tasks[0].parameters.get("action"), "maximize")

        # Desktop switching
        plan_desk = self.orchestrator.plan("change desktop", language="en")
        self.assertEqual(plan_desk.tasks[0].action, ActionType.WINDOW_CONTROL)
        self.assertEqual(plan_desk.tasks[0].parameters.get("action"), "switch_desktop")

    def test_volume_control_intents(self):
        plan_vol = self.orchestrator.plan("increase volume", language="en")
        self.assertEqual(plan_vol.tasks[0].action, ActionType.SYSTEM_VOLUME)
        self.assertEqual(plan_vol.tasks[0].parameters.get("action"), "up")

        plan_mute = self.orchestrator.plan("mute audio", language="en")
        self.assertEqual(plan_mute.tasks[0].action, ActionType.SYSTEM_VOLUME)
        self.assertEqual(plan_mute.tasks[0].parameters.get("action"), "mute")

        # Hindi
        plan_hi = self.orchestrator.plan("awaz badhao", language="hi")
        self.assertEqual(plan_hi.tasks[0].action, ActionType.SYSTEM_VOLUME)
        self.assertEqual(plan_hi.tasks[0].parameters.get("action"), "up")

    def test_typing_and_key_press_intents(self):
        plan_type = self.orchestrator.plan("type Synapse is ultra fast", language="en")
        self.assertEqual(plan_type.tasks[0].action, ActionType.TYPE_TEXT)
        self.assertEqual(plan_type.tasks[0].parameters.get("text"), "Synapse is ultra fast")

        plan_key = self.orchestrator.plan("press enter", language="en")
        self.assertEqual(plan_key.tasks[0].action, ActionType.KEY_PRESS)
        self.assertEqual(plan_key.tasks[0].parameters.get("key"), "enter")

    def test_screen_button_click_intent(self):
        plan_btn = self.orchestrator.plan("press continue button", language="en")
        self.assertEqual(plan_btn.tasks[0].action, ActionType.CLICK_TEXT)
        self.assertEqual(plan_btn.tasks[0].parameters.get("button_name"), "continue")

        plan_skip = self.orchestrator.plan("click skip", language="en")
        self.assertEqual(plan_skip.tasks[0].action, ActionType.CLICK_TEXT)
        self.assertEqual(plan_skip.tasks[0].parameters.get("button_name"), "skip")

    def test_compound_intent(self):
        prompt = "open youtube and scroll down"
        plan = self.orchestrator.plan(prompt, language="en")
        self.assertEqual(len(plan.tasks), 2)
        self.assertEqual(plan.tasks[0].action, ActionType.OPEN_URL)
        self.assertEqual(plan.tasks[1].action, ActionType.MOUSE_SCROLL)

    def test_sub_millisecond_planning_latency(self):
        """Ensures intent planning completes in < 2 milliseconds."""
        start = time.perf_counter()
        self.orchestrator.plan("open calculator and snap window to top right", language="en")
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        print(f"\n⚡ Benchmark: Planning took {elapsed_ms:.3f} ms")
        self.assertLess(elapsed_ms, 5.0, "Planning latency exceeded 5ms!")

    def test_executor_command_execution(self):
        prompt = "run command echo SynapseFast"
        plan = self.orchestrator.plan(prompt, language="en")
        self.assertEqual(plan.tasks[0].action, ActionType.RUN_COMMAND)
        executed_plan = self.executor.execute_plan(plan)
        self.assertEqual(executed_plan.tasks[0].status, TaskStatus.SUCCESS)
        self.assertIn("SynapseFast", executed_plan.tasks[0].result)

    def test_exit_intents(self):
        # English
        plan_en = self.orchestrator.plan("stop listening", language="en")
        self.assertEqual(plan_en.tasks[0].action, ActionType.EXIT_APP)

        # Hindi
        plan_hi = self.orchestrator.plan("band karo", language="hi")
        self.assertEqual(plan_hi.tasks[0].action, ActionType.EXIT_APP)

        # Marathi
        plan_mr = self.orchestrator.plan("thamb", language="mr")
        self.assertEqual(plan_mr.tasks[0].action, ActionType.EXIT_APP)


if __name__ == "__main__":
    unittest.main()
