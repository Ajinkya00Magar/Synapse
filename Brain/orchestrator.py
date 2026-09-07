"""
Brain (Orchestrator) component of the Synapse pipeline.

Responsible for receiving raw user speech/text input, analyzing intent,
and structuring it into an actionable, low-latency ExecutionPlan.
"""

import os
import re
import sys
import uuid
from typing import List
from .schema import ActionType, ExecutionPlan, Task, TaskStatus

# Ensure Windows terminal supports UTF-8, emojis, and Indic scripts
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class Orchestrator:
    """High-speed in-memory intent parser and workflow orchestrator."""

    def __init__(self):
        # Common website shortcuts
        self._url_shortcuts = {
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com",
            "github": "https://www.github.com",
            "reddit": "https://www.reddit.com",
            "twitter": "https://twitter.com",
            "x": "https://x.com",
            "linkedin": "https://www.linkedin.com",
            "chatgpt": "https://chatgpt.com",
            "whatsapp": "https://web.whatsapp.com",
            "gmail": "https://mail.google.com",
        }

    def plan(self, prompt: str, language: str = "en") -> ExecutionPlan:
        """
        Translates a natural language user prompt into an ordered ExecutionPlan.
        Latency: < 0.1 ms in-memory.
        """
        clean_prompt = prompt.strip()
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"

        print(f"\n🧠 [Brain] Analyzing prompt: \"{clean_prompt}\" (Language: {language})")

        # Split complex sentences joined by 'and', 'then', 'ani', 'aur'
        sub_intents = self._split_compound_sentences(clean_prompt)
        tasks: List[Task] = []

        for idx, intent_text in enumerate(sub_intents, start=1):
            task = self._parse_single_intent(intent_text, task_index=idx)
            if task:
                tasks.append(task)

        if not tasks:
            tasks.append(
                Task(
                    id="task_1",
                    action=ActionType.UNKNOWN,
                    description=f"Could not determine intent for: '{clean_prompt}'",
                    parameters={"raw_prompt": clean_prompt},
                    status=TaskStatus.FAILED,
                    error="Unrecognized command format.",
                )
            )

        execution_plan = ExecutionPlan(
            plan_id=plan_id,
            user_prompt=clean_prompt,
            language=language,
            tasks=tasks,
        )

        print(f"📋 [Brain] Generated {len(tasks)} tasks for Plan {plan_id}:")
        for t in tasks:
            print(f"   • [{t.action.value.upper()}] {t.description} -> {t.parameters}")

        return execution_plan

    def _split_compound_sentences(self, prompt: str) -> List[str]:
        """Splits multi-step commands connected by conjunctions (and, then, aur, ani)."""
        delimiters = r"\b(?:and then|and|then|aur|phir|ani|mag)\b"
        parts = re.split(delimiters, prompt, flags=re.IGNORECASE)
        return [p.strip() for p in parts if p.strip()]

    def _clean_punctuation(self, text: str) -> str:
        """Strips speech-to-text punctuation like trailing periods, question marks, commas."""
        return re.sub(r"[.,?!;]+$", "", text).strip()

    def _parse_single_intent(self, raw_intent: str, task_index: int) -> Task:
        """
        Analyzes a single clause and maps it to an atomic Task.
        Evaluates fast-path rules in priority order.
        """
        intent = self._clean_punctuation(raw_intent)
        lower = intent.lower()
        task_id = f"task_{task_index}"

        # ── 0. Stop / Exit Synapse Intent ──
        # Matches: "stop listening", "exit synapse", "quit", "shutdown synapse", "band karo", "thamb"
        if re.search(r"^(?:stop listening|exit synapse|quit synapse|close synapse|shutdown synapse|exit|quit|bye synapse)$", lower) or \
           re.search(r"^(?:band karo|ruk jao|thamb|band kar)$", lower):
            return Task(
                id=task_id,
                action=ActionType.EXIT_APP,
                description="Stop Synapse and exit listening mode",
                parameters={},
            )

        # ── 1. Scrolling Intent ──
        # Matches: "scroll down", "scroll up", "scroll until...", "khali scroll kar", "niche scroll karo"
        if re.search(r"\bscroll\s+(?:down|downwards|a bit down|until|bottom)\b", lower) or \
           re.search(r"\b(?:khali|niche)\s+scroll\b", lower):
            return Task(
                id=task_id,
                action=ActionType.MOUSE_SCROLL,
                description="Scroll down page",
                parameters={"direction": "down", "intensity": 6},
            )
        if re.search(r"\bscroll\s+(?:up|upwards|a bit up|top)\b", lower) or \
           re.search(r"\b(?:var|upar)\s+scroll\b", lower):
            return Task(
                id=task_id,
                action=ActionType.MOUSE_SCROLL,
                description="Scroll up page",
                parameters={"direction": "up", "intensity": 6},
            )

        # ── 2. Volume & Brightness Control ──
        # Matches: "increase volume", "volume up", "awaz vadhav", "awaz badhao"
        if re.search(r"\b(?:increase|raise|turn up|higher)\s+(?:the\s+)?volume\b", lower) or \
           re.search(r"\bvolume\s+up\b", lower) or \
           re.search(r"\b(?:awaz|aawaz)\s+(?:vadhav|badhao|badha do)\b", lower):
            return Task(
                id=task_id,
                action=ActionType.SYSTEM_VOLUME,
                description="Increase master volume",
                parameters={"action": "up", "steps": 4},
            )

        if re.search(r"\b(?:decrease|lower|turn down|reduce)\s+(?:the\s+)?volume\b", lower) or \
           re.search(r"\bvolume\s+down\b", lower) or \
           re.search(r"\b(?:awaz|aawaz)\s+(?:kami kar|kam karo|kam kar do)\b", lower):
            return Task(
                id=task_id,
                action=ActionType.SYSTEM_VOLUME,
                description="Decrease master volume",
                parameters={"action": "down", "steps": 4},
            )

        if re.search(r"\b(?:mute|unmute|silence)\s*(?:the\s+)?(?:audio|volume|sound)?\b", lower):
            return Task(
                id=task_id,
                action=ActionType.SYSTEM_VOLUME,
                description="Toggle mute master volume",
                parameters={"action": "mute"},
            )

        if re.search(r"\b(?:increase|raise)\s+(?:the\s+)?brightness\b", lower):
            return Task(
                id=task_id,
                action=ActionType.SYSTEM_BRIGHTNESS,
                description="Increase screen brightness",
                parameters={"action": "up", "step": 15},
            )
        if re.search(r"\b(?:decrease|lower|reduce)\s+(?:the\s+)?brightness\b", lower):
            return Task(
                id=task_id,
                action=ActionType.SYSTEM_BRIGHTNESS,
                description="Decrease screen brightness",
                parameters={"action": "down", "step": 15},
            )

        # ── 3. Window & Desktop Management ──
        # Snapping: "snap window to top right", "set window at top right corner", "top right corner"
        if re.search(r"\b(?:snap|set|move|place|put)\b.*\btop\s*right\b", lower) or "top right corner" in lower:
            return Task(
                id=task_id,
                action=ActionType.WINDOW_CONTROL,
                description="Snap active window to top-right corner",
                parameters={"action": "snap_top_right"},
            )
        if re.search(r"\b(?:snap|set|move|place|put)\b.*\btop\s*left\b", lower) or "top left corner" in lower:
            return Task(
                id=task_id,
                action=ActionType.WINDOW_CONTROL,
                description="Snap active window to top-left corner",
                parameters={"action": "snap_top_left"},
            )
        if re.search(r"\b(?:snap|move|set)\b.*\b(?:to\s+)?left\s*(?:half|side)?\b", lower):
            return Task(
                id=task_id,
                action=ActionType.WINDOW_CONTROL,
                description="Snap active window to left half",
                parameters={"action": "snap_left"},
            )
        if re.search(r"\b(?:snap|move|set)\b.*\b(?:to\s+)?right\s*(?:half|side)?\b", lower):
            return Task(
                id=task_id,
                action=ActionType.WINDOW_CONTROL,
                description="Snap active window to right half",
                parameters={"action": "snap_right"},
            )

        # Sizing: Maximize, Minimize, Close
        if re.search(r"\b(?:maximize|fullscreen)(?:\s+(?:this|the)?\s+window)?\b", lower):
            return Task(
                id=task_id,
                action=ActionType.WINDOW_CONTROL,
                description="Maximize active window",
                parameters={"action": "maximize"},
            )
        if re.search(r"\b(?:minimize)(?:\s+(?:this|the)?\s+window)?\b", lower):
            return Task(
                id=task_id,
                action=ActionType.WINDOW_CONTROL,
                description="Minimize active window",
                parameters={"action": "minimize"},
            )
        if re.search(r"\b(?:close|exit)(?:\s+(?:this|the)?\s+window)?\b", lower):
            return Task(
                id=task_id,
                action=ActionType.WINDOW_CONTROL,
                description="Close active window",
                parameters={"action": "close"},
            )

        # Switching Desktops & Windows: "change desktop", "switch window", "alt tab"
        if re.search(r"\b(?:change|switch|next)\s+desktop\b", lower):
            return Task(
                id=task_id,
                action=ActionType.WINDOW_CONTROL,
                description="Switch to next virtual desktop",
                parameters={"action": "switch_desktop"},
            )
        if re.search(r"\b(?:switch|next|change)\s+window\b", lower) or "alt tab" in lower:
            return Task(
                id=task_id,
                action=ActionType.WINDOW_CONTROL,
                description="Switch active window (Alt+Tab)",
                parameters={"action": "switch_window"},
            )
        if re.search(r"\b(?:show|go to)\s+desktop\b", lower):
            return Task(
                id=task_id,
                action=ActionType.WINDOW_CONTROL,
                description="Show desktop",
                parameters={"action": "show_desktop"},
            )

        # ── 4. On-Screen Button & Text Clicking ──
        # Matches: "press continue button", "click skip", "press continue", "press submit button"
        button_match = re.search(r"(?:press|click)\s+(?:the\s+)?([a-zA-Z0-9\s]+?)\s+(?:button|option|link)$", intent, flags=re.IGNORECASE)
        quick_button = re.search(r"^(?:press|click)\s+(continue|skip|submit|ok|cancel|confirm|yes|no)$", intent, flags=re.IGNORECASE)

        if button_match:
            btn = button_match.group(1).strip()
            return Task(
                id=task_id,
                action=ActionType.CLICK_TEXT,
                description=f"Click on-screen button '{btn}'",
                parameters={"button_name": btn},
            )
        elif quick_button:
            btn = quick_button.group(1).strip()
            return Task(
                id=task_id,
                action=ActionType.CLICK_TEXT,
                description=f"Click on-screen button '{btn}'",
                parameters={"button_name": btn},
            )

        # ── 5. Typing and Keystrokes ──
        # Matches: "type hello world", "write this is awesome"
        type_match = re.search(r"^(?:type|write|enter text)\s+(.+)$", intent, flags=re.IGNORECASE)
        if type_match:
            text_to_type = type_match.group(1).strip()
            return Task(
                id=task_id,
                action=ActionType.TYPE_TEXT,
                description=f"Type text: \"{text_to_type}\"",
                parameters={"text": text_to_type},
            )

        # Matches: "press enter", "press space", "press escape", "press ctrl c"
        key_match = re.search(r"^(?:press|hit)\s+(enter|space|spacebar|esc|escape|tab|backspace|delete|ctrl\+[a-z]|alt\+[a-z0-9]|win\+[a-z])$", lower)
        if key_match:
            k = key_match.group(1).strip()
            return Task(
                id=task_id,
                action=ActionType.KEY_PRESS,
                description=f"Press key '{k}'",
                parameters={"key": k},
            )

        # ── 6. Search Web Intent ──
        # Matches: "search python tutorials on youtube", "search AI on google"
        search_match = re.search(r"(?:search|google|find)\s+(?:for\s+)?(.+?)(?:\s+on\s+(youtube|google))?$", intent, flags=re.IGNORECASE)
        if search_match:
            query = search_match.group(1).strip()
            engine_str = search_match.group(2)
            engine = engine_str.lower() if engine_str else ("youtube" if "youtube" in query.lower() else "google")
            query = re.sub(r"\s+on\s+(?:youtube|google)$", "", query, flags=re.IGNORECASE).strip()
            query = self._clean_punctuation(query)
            return Task(
                id=task_id,
                action=ActionType.SEARCH_WEB,
                description=f"Search {engine.capitalize()} for '{query}'",
                parameters={"query": query, "engine": engine},
            )

        # ── 7. Open Website / URL Intent ──
        # Matches: "open youtube", "go to github.com", "open reddit"
        url_match = re.search(r"(?:open|go to|visit)\s+([a-zA-Z0-9\.\-\_]+(?:\.[a-zA-Z]{2,})?)$", intent, flags=re.IGNORECASE)
        if url_match:
            target = self._clean_punctuation(url_match.group(1).strip())
            target_lower = target.lower()
            if target_lower in self._url_shortcuts:
                return Task(
                    id=task_id,
                    action=ActionType.OPEN_URL,
                    description=f"Open website {target.capitalize()}",
                    parameters={"url": self._url_shortcuts[target_lower]},
                )
            elif "." in target and not target_lower.endswith((".exe", ".cmd", ".bat")):
                return Task(
                    id=task_id,
                    action=ActionType.OPEN_URL,
                    description=f"Open URL '{target}'",
                    parameters={"url": f"https://{target}"},
                )

        # ── 8. Terminal Command Intent ──
        # Matches: "run command echo hello", "execute ipconfig"
        cmd_match = re.search(r"(?:run command|execute command|exec|run terminal|terminal)\s+(.+)$", intent, flags=re.IGNORECASE)
        if cmd_match:
            cmd = cmd_match.group(1).strip()
            return Task(
                id=task_id,
                action=ActionType.RUN_COMMAND,
                description=f"Execute command: '{cmd}'",
                parameters={"command": cmd},
            )

        # ── 9. Launch Desktop Application ──
        # Matches: "open notepad", "launch calculator", "notepad ughad"
        app_match = re.search(r"(?:open|launch|start)\s+(?:app\s+|application\s+)?([a-zA-Z0-9\s]+)$", intent, flags=re.IGNORECASE)
        indic_app_match = re.search(r"^([a-zA-Z0-9\s]+)\s+(?:kholo|chalu kara|suru kara|ughad|open kara)$", intent, flags=re.IGNORECASE)

        target_app = None
        if app_match:
            target_app = self._clean_punctuation(app_match.group(1).strip())
        elif indic_app_match:
            target_app = self._clean_punctuation(indic_app_match.group(1).strip())

        if target_app:
            target_lower = target_app.lower()
            if target_lower in self._url_shortcuts:
                return Task(
                    id=task_id,
                    action=ActionType.OPEN_URL,
                    description=f"Open website {target_app.capitalize()}",
                    parameters={"url": self._url_shortcuts[target_lower]},
                )
            return Task(
                id=task_id,
                action=ActionType.OPEN_APP,
                description=f"Launch application '{target_app}'",
                parameters={"app_name": target_lower},
            )

        # ── 10. Fallback ──
        return Task(
            id=task_id,
            action=ActionType.UNKNOWN,
            description=f"Unrecognized intent for: '{intent}'",
            parameters={"raw_clause": intent},
            status=TaskStatus.FAILED,
            error="No matching rule found.",
        )
