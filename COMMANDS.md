# ⚡ Synapse Voice Commands Reference Manual

A complete cheat-sheet of all voice commands, actions, and features supported by Synapse. Every command executes with **sub-millisecond latency (< 1ms)** using direct Windows Win32 C APIs.

---

## 🚀 Quick Start Running Modes

| Mode | Command | Description |
| :--- | :--- | :--- |
| **Live Voice Mode** | `python main.py en` | Listens to your microphone in English |
| **Hindi Voice Mode** | `python main.py hi` | Listens to your microphone in Hindi |
| **Marathi Voice Mode**| `python main.py mr` | Listens to your microphone in Marathi |
| **Interactive Text Mode** | `python main.py --text` | Type commands in terminal without microphone |

---

## 🪟 1. Window & Desktop Management

| Capability | Example Voice Commands | Action Performed |
| :--- | :--- | :--- |
| **Snap Top-Right** | *"snap window to top right"*, *"set window at top right corner"*, *"top right corner"* | Instantly moves and resizes window to top-right quadrant |
| **Snap Top-Left** | *"snap window to top left"*, *"top left corner"* | Moves and resizes window to top-left quadrant |
| **Snap Left / Right** | *"snap window to left"*, *"snap window to right"* | Snaps window to left or right half of screen |
| **Maximize** | *"maximize window"*, *"fullscreen this window"* | Enters fullscreen maximize state |
| **Minimize** | *"minimize window"*, *"hide window"* | Minimizes active window |
| **Restore** | *"restore window"*, *"normal window size"* | Restores window to default floating size |
| **Close Window** | *"close window"*, *"exit window"* | Closes the currently active window |
| **Switch Window** | *"switch window"*, *"next window"*, *"alt tab"* | Cycles to the next open application (Alt+Tab) |
| **Change Desktop** | *"change desktop"*, *"switch desktop"*, *"next desktop"* | Switches to next virtual desktop (Ctrl+Win+Right) |
| **Show Desktop** | *"show desktop"*, *"go to desktop"* | Minimizes all windows to reveal desktop (Win+D) |

---

## 📜 2. Mouse & Page Scrolling

| Capability | Example Voice Commands | Action Performed |
| :--- | :--- | :--- |
| **Scroll Down** | *"scroll down"*, *"scroll downwards"*, *"scroll a bit down"* | Scrolls down 6 wheel clicks (< 0.1ms) |
| **Scroll Up** | *"scroll up"*, *"scroll upwards"*, *"scroll to top"* | Scrolls up 6 wheel clicks (< 0.1ms) |
| **Hindi Scrolling** | *"niche scroll karo"*, *"upar scroll karo"* | Native Hindi scrolling commands |
| **Marathi Scrolling**| *"khali scroll kar"*, *"var scroll kar"* | Native Marathi scrolling commands |

---

## 🔊 3. Hardware, Volume & Brightness

| Capability | Example Voice Commands | Action Performed |
| :--- | :--- | :--- |
| **Volume Up** | *"increase volume"*, *"volume up"*, *"louder"* | Raises Windows master volume by 8% |
| **Volume Down** | *"decrease volume"*, *"volume down"*, *"quieter"* | Lowers Windows master volume by 8% |
| **Mute / Unmute** | *"mute audio"*, *"unmute volume"*, *"silence"* | Toggles master audio mute |
| **Brightness Up** | *"increase brightness"*, *"brightness up"* | Increases screen brightness by 15% |
| **Brightness Down** | *"decrease brightness"*, *"brightness down"* | Decreases screen brightness by 15% |
| **Hindi Volume** | *"awaz badhao"*, *"awaz kam karo"*, *"awaz band karo"* | Native Hindi volume control |
| **Marathi Volume**| *"awaz vadhav"*, *"awaz kami kar"* | Native Marathi volume control |

---

## ⌨️ 4. Keyboard, Typing & Keystrokes

| Capability | Example Voice Commands | Action Performed |
| :--- | :--- | :--- |
| **Type Text** | *"type Hello World"*, *"write Synapse is fast"* | Instantly types characters into active text box |
| **Press Enter** | *"press enter"*, *"hit enter"* | Sends Enter keypress |
| **Press Space** | *"press space"*, *"hit spacebar"* | Sends Space keypress |
| **Press Escape** | *"press escape"*, *"press esc"* | Sends Esc keypress |
| **Press Tab** | *"press tab"* | Advances focus to next field |
| **Press Backspace** | *"press backspace"* | Deletes previous character |
| **Shortcuts / Hotkeys**| *"press ctrl c"*, *"press ctrl v"*, *"press alt f4"* | Executes multi-key combinations |

---

## 🔘 5. On-Screen Buttons & Dialog Interaction

| Capability | Example Voice Commands | Action Performed |
| :--- | :--- | :--- |
| **Confirm / Continue** | *"press continue button"*, *"click continue"*, *"press submit"*, *"click ok"* | Activates primary action button in active dialog |
| **Dismiss / Skip** | *"click skip"*, *"press skip button"*, *"press cancel"*, *"click dismiss"* | Dismisses dialog / skips prompt |

---

## 🌐 6. Web Browsing & Search

| Capability | Example Voice Commands | Action Performed |
| :--- | :--- | :--- |
| **Google Search** | *"search artificial intelligence on google"*, *"google latest tech news"* | Opens Google search in default browser |
| **YouTube Search** | *"search python tutorials on youtube"*, *"search lofi music on youtube"* | Opens YouTube search results |
| **Open Websites** | *"open youtube"*, *"open github"*, *"open reddit"*, *"open chatgpt"*, *"open whatsapp"* | Launches URL directly from shortcuts |
| **Direct URL** | *"open google.com"*, *"visit python.org"* | Opens any arbitrary domain |

---

## 💻 7. Application Launching & Terminal Commands

| Capability | Example Voice Commands | Action Performed |
| :--- | :--- | :--- |
| **Launch Apps** | *"open notepad"*, *"open calculator"*, *"open paint"*, *"open settings"*, *"open chrome"*, *"open terminal"* | Spawns Windows application asynchronously |
| **Hindi Launch** | *"notepad kholo"*, *"calculator chalu kara"* | Launches app using Hindi imperative |
| **Marathi Launch**| *"notepad ughad"*, *"calculator suru kara"* | Launches app using Marathi imperative |
| **Shell Commands** | *"run command echo Hello"*, *"execute command dir"*, *"run command ipconfig"* | Executes terminal command and returns stdout |

---

## 🔗 8. Multi-Step Compound Commands

You can chain multiple commands together in a single natural sentence using conjunctions like **"and"**, **"then"**, **"aur"** (Hindi), or **"ani"** (Marathi):

* *"Open YouTube and scroll down"*
* *"Open Notepad and type Hello Synapse"*
* *"Open Calculator and snap window to top right"*
* *"Increase volume and search lofi beats on youtube"*
* *"Open Settings and search bluetooth"*

---

## 🛑 9. Hands-Free Stopping & Assistant Shutdown

Synapse runs continuously in the background so you can browse, type, and multitask without touching the assistant. To stop it at any time, speak any of these exit phrases:

| Capability | Example Voice Commands | Action Performed |
| :--- | :--- | :--- |
| **English Stop** | *"stop listening"*, *"exit synapse"*, *"quit synapse"*, *"bye synapse"*, *"stop"* | Closes the floating HUD and cleanly terminates the pipeline |
| **Hindi Stop** | *"band karo"*, *"ruk jao"* | Native Hindi stop command |
| **Marathi Stop** | *"thamb"*, *"band kar"* | Native Marathi stop command |
| **Keyboard Interrupt**| Press `Ctrl + C` in PowerShell | Immediate emergency stop |
