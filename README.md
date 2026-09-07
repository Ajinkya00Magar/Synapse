# ⚡ Synapse

Control your Windows PC completely hands-free using your voice.

Synapse listens to your microphone, understands your commands in English, Hindi, or Marathi, and executes them instantly.

---

## 🚀 Quick Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Add your Deepgram API Key
Create a `.env` file in the project root:
```env
DEEPGRAM_API_KEY=your_api_key_here
```
*(Get a free key at [deepgram.com](https://deepgram.com))*

---

## ▶️ How to Run

| Command | Mode |
| :--- | :--- |
| `python main.py` | Live voice control in **English** |
| `python main.py hi` | Live voice control in **Hindi** |
| `python main.py mr` | Live voice control in **Marathi** |
| `python main.py --text` | Interactive text mode (test without microphone) |

---

## 🗣️ Example Voice Commands

- **Apps & Websites:** *"Open Chrome"*, *"Launch Calculator"*, *"Open YouTube"*
- **Volume & Screen:** *"Increase volume"*, *"Mute audio"*, *"Decrease brightness"*
- **Window Management:** *"Maximize window"*, *"Snap window to right"*, *"Switch window"*
- **Mouse & Scroll:** *"Scroll down"*, *"Scroll up"*
- **Typing & Keys:** *"Type Hello World"*, *"Press enter"*, *"Press Ctrl C"*
- **Multi-step actions:** *"Open YouTube and scroll down"*

**To stop:** Say *"stop listening"* (or *"band karo"* / *"thamb"*), or press `Ctrl + C`.

---

📖 For all supported commands and shortcuts, see **[COMMANDS.md](COMMANDS.md)**.
