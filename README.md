# ⚡ J.A.R.V.I.S. (Just A Rather Very Intelligent System)

A **Cloud-Brain + Local-Hands Voice AI Assistant** designed for Windows, inspired by Iron Man's JARVIS.

Runs smoothly with **0% GPU load on your PC** by offloading intelligent reasoning and tool selection to high-speed Cloud AI (Google Gemini 2.0 Flash) while performing full system automation on your local machine.

---

## 🚀 Key Features

- ☁️ **Cloud Brain Intelligence**: Instant sub-second reasoning, function calling, and real-time internet knowledge powered by Google Gemini.
- 🎙️ **Cinematic British Neural Voice**: Authentic British butler voice powered by Microsoft Edge Neural TTS (`en-GB-RyanNeural`).
- 💻 **Complete Device Automation ("The Hands")**:
  - **App Launcher**: Open/Close any app (*"Jarvis, open VS Code"*, *"Jarvis, open Spotify"*).
  - **System Control**: Adjust volume, mute, take screenshots, lock PC, empty recycle bin.
  - **Media & Web**: Search Google, play songs directly on YouTube (*"Jarvis, play AC/DC on YouTube"*), open any URL.
  - **Hardware Diagnostics**: Real-time CPU, RAM, Battery health, storage, and uptime monitoring (*"Jarvis, report system status"*).
  - **Notes & Reminders**: Quick voice note taking saved directly to text files.
- 🖥️ **Futuristic Arc Reactor HUD**: Iron Man Dark & Cyan interface with live animated Arc Reactor, live system metrics ticker, and cyber console.

---

## 🛠️ Quick Setup

### 1. Get a Free Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Click **Create API key** (it is 100% free with generous rate limits).
3. Open [.env](file:///d:/MY%20project/JARVIS/.env) and paste your key:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```
   *(Or click the ⚙️ Settings button inside the JARVIS HUD to paste it directly!)*

### 2. Launch JARVIS
Run the startup script:
```bash
python run_jarvis.py
```
Or double-click [start_jarvis.bat](file:///d:/MY%20project/JARVIS/start_jarvis.bat).

---

## 🗣️ Sample Commands to Try

| Category | Example Voice / Text Commands |
| :--- | :--- |
| **System Diagnostics** | *"Jarvis, report system status"*, *"Check my battery and CPU usage"* |
| **App Control** | *"Open Calculator"*, *"Launch Chrome"*, *"Open VS Code"*, *"Close Notepad"* |
| **Media & Music** | *"Play Iron Man theme song on YouTube"*, *"Search Google for latest tech news"* |
| **Audio & Screen** | *"Volume up"*, *"Mute audio"*, *"Take a screenshot"*, *"Lock workstation"* |
| **Productivity** | *"Take a note: Meeting scheduled for tomorrow at 10 AM"* |
| **Conversational** | *"Who was the architect behind the Eiffel Tower?"*, *"Explain how quantum computing works"* |

---

## 📁 Project Structure

```
JARVIS/
├── .env                  # API Key & Voice Configuration
├── run_jarvis.py         # Main launcher
├── start_jarvis.bat      # 1-Click Windows Launcher
├── config.py             # System & TTS settings
├── core/
│   ├── brain.py          # Cloud AI Agent with Tool / Function Calling
│   ├── voice.py          # High-fidelity Edge Neural TTS & Speech Recognition
│   ├── tools.py          # Windows OS, AppOpener, PyAutoGUI, & Web tools
│   └── sys_info.py       # Live Hardware & Diagnostic metrics
├── ui/
│   └── hud.py            # Iron Man Arc Reactor CustomTkinter Interface
└── data/
    ├── notes/            # Saved text notes
    ├── screenshots/      # Saved full-screen captures
    └── temp/             # Transient audio buffers
```
