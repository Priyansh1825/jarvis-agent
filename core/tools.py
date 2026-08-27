import os
import sys
import time
import subprocess
import webbrowser
import urllib.parse
import datetime
from pathlib import Path
import pyautogui
from config import SCREENSHOTS_DIR, NOTES_DIR
from core.sys_info import format_system_report, get_system_diagnostics

# Try importing AppOpener for fuzzy app opening
try:
    from AppOpener import open as app_open, close as app_close
    HAS_APP_OPENER = True
except ImportError:
    HAS_APP_OPENER = False

# Mapping for common shortcuts and system utilities
SYSTEM_APPS = {
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "notepad": "notepad.exe",
    "paint": "mspaint.exe",
    "cmd": "cmd.exe",
    "terminal": "wt.exe",
    "task manager": "taskmgr.exe",
    "settings": "start ms-settings:",
    "control panel": "control.exe",
    "explorer": "explorer.exe",
    "file explorer": "explorer.exe",
    "chrome": "start chrome",
    "browser": "start chrome",
    "edge": "start msedge",
    "spotify": "start spotify",
    "vs code": "code",
    "vscode": "code"
}

def open_application(app_name: str) -> str:
    """
    Opens an application, tool, or software on the user's computer.
    Example: 'calculator', 'chrome', 'spotify', 'notepad', 'vs code'.
    """
    clean_name = app_name.strip().lower()
    
    # 1. Check known system apps table
    if clean_name in SYSTEM_APPS:
        cmd = SYSTEM_APPS[clean_name]
        try:
            if cmd.startswith("start "):
                os.system(cmd)
            else:
                subprocess.Popen(cmd, shell=True)
            return f"Opened {app_name} successfully."
        except Exception as e:
            return f"Attempted to open {app_name}, encountered: {str(e)}"
            
    # 2. Try AppOpener for fuzzy discovery of installed apps
    if HAS_APP_OPENER:
        try:
            app_open(app_name, match_closest=True, throw_error=True)
            return f"Launched {app_name}."
        except Exception:
            pass

    # 3. Fallback to Windows 'start'
    try:
        os.system(f'start "" "{app_name}"')
        return f"Dispatched launch command for {app_name}."
    except Exception as e:
        return f"Unable to launch {app_name}: {str(e)}"

def close_application(app_name: str) -> str:
    """
    Closes or terminates a running application on the computer.
    """
    clean_name = app_name.strip().lower()
    
    if HAS_APP_OPENER:
        try:
            app_close(clean_name, match_closest=True, throw_error=True)
            return f"Closed {app_name}."
        except Exception:
            pass
            
    # Fallback to taskkill
    try:
        proc_name = clean_name.replace(" ", "")
        if not proc_name.endswith(".exe"):
            proc_name += ".exe"
        subprocess.run(f"taskkill /f /im {proc_name}", shell=True, capture_output=True)
        return f"Closed {app_name}."
    except Exception as e:
        return f"Error attempting to close {app_name}: {str(e)}"

def get_system_health() -> str:
    """
    Returns live hardware status including CPU usage, RAM utilization, battery level, storage, and uptime.
    """
    return format_system_report()

def volume_control(action: str) -> str:
    """
    Controls system audio volume.
    Actions: 'up' (increases volume), 'down' (decreases volume), 'mute' (toggles mute), 'max' (sets to max).
    """
    act = action.lower()
    if "up" in act or "increase" in act or "raise" in act:
        for _ in range(5):
            pyautogui.press("volumeup")
        return "Increased system volume."
    elif "down" in act or "decrease" in act or "lower" in act:
        for _ in range(5):
            pyautogui.press("volumedown")
        return "Decreased system volume."
    elif "mute" in act or "unmute" in act:
        pyautogui.press("volumemute")
        return "Toggled mute status."
    elif "max" in act or "100" in act:
        for _ in range(50):
            pyautogui.press("volumeup")
        return "Volume set to maximum."
    else:
        pyautogui.press("volumeup")
        return f"Adjusted volume ({action})."

def take_screenshot() -> str:
    """
    Captures a full-screen screenshot of the desktop and saves it.
    """
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = SCREENSHOTS_DIR / f"screenshot_{timestamp}.png"
        screenshot = pyautogui.screenshot()
        screenshot.save(str(filepath))
        return f"Screenshot captured and saved to {filepath.name}."
    except Exception as e:
        return f"Unable to capture screenshot (screen may be locked or display inactive): {str(e)}"


def play_on_youtube(query: str) -> str:
    """
    Searches for and opens a video or song directly on YouTube in the browser.
    """
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://www.youtube.com/results?search_query={encoded_query}"
    webbrowser.open(url)
    return f"Playing '{query}' on YouTube."

def search_google(query: str) -> str:
    """
    Performs a Google search in the default web browser.
    """
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://www.google.com/search?q={encoded_query}"
    webbrowser.open(url)
    return f"Searching Google for: {query}"

def open_url(url: str) -> str:
    """
    Opens any website URL in the default web browser.
    """
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    webbrowser.open(url)
    return f"Opening {url}."

def save_note(note_text: str, title: str = "Quick Note") -> str:
    """
    Saves a text note or reminder into the notes repository.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    clean_title = "".join(c for c in title if c.isalnum() or c in (' ', '_', '-')).strip()
    if not clean_title:
        clean_title = "note"
    filename = f"{clean_title}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    filepath = NOTES_DIR / filename
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"Timestamp: {timestamp}\nTitle: {title}\n\n{note_text}\n")
        
    return f"Note titled '{title}' saved successfully."

def lock_screen() -> str:
    """
    Locks the Windows computer workstation immediately.
    """
    subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True)
    return "Workstation locked."

def empty_recycle_bin() -> str:
    """
    Empties the Windows Recycle Bin.
    """
    try:
        subprocess.run(
            'powershell.exe -Command "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"',
            shell=True,
            capture_output=True
        )
        return "Recycle Bin emptied."
    except Exception as e:
        return f"Failed to empty Recycle Bin: {str(e)}"

# Register all tool functions with their schemas for Gemini Function Calling
JARVIS_TOOL_FUNCTIONS = {
    "open_application": open_application,
    "close_application": close_application,
    "get_system_health": get_system_health,
    "volume_control": volume_control,
    "take_screenshot": take_screenshot,
    "play_on_youtube": play_on_youtube,
    "search_google": search_google,
    "open_url": open_url,
    "save_note": save_note,
    "lock_screen": lock_screen,
    "empty_recycle_bin": empty_recycle_bin
}

JARVIS_TOOL_DECLARATIONS = [
    {
        "name": "open_application",
        "description": "Opens an application or software program on the computer (e.g. calculator, chrome, spotify, notepad, vscode).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "app_name": {
                    "type": "STRING",
                    "description": "The name of the application to open."
                }
            },
            "required": ["app_name"]
        }
    },
    {
        "name": "close_application",
        "description": "Closes or kills a running application on the computer.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "app_name": {
                    "type": "STRING",
                    "description": "The name of the application to close."
                }
            },
            "required": ["app_name"]
        }
    },
    {
        "name": "get_system_health",
        "description": "Checks and reports hardware diagnostics: CPU usage, RAM utilization, battery level, storage, and system uptime.",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    },
    {
        "name": "volume_control",
        "description": "Controls audio volume on the computer (up, down, mute, max).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {
                    "type": "STRING",
                    "description": "The volume action: 'up', 'down', 'mute', or 'max'."
                }
            },
            "required": ["action"]
        }
    },
    {
        "name": "take_screenshot",
        "description": "Captures a full screenshot of the screen and saves it.",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    },
    {
        "name": "play_on_youtube",
        "description": "Searches for and opens a music video, song, or video on YouTube.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {
                    "type": "STRING",
                    "description": "The name of the song, artist, or video to play."
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "search_google",
        "description": "Searches Google in the web browser for the requested information.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {
                    "type": "STRING",
                    "description": "The search query."
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "open_url",
        "description": "Opens a website URL in the web browser.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "url": {
                    "type": "STRING",
                    "description": "The website URL to open (e.g. github.com, reddit.com)."
                }
            },
            "required": ["url"]
        }
    },
    {
        "name": "save_note",
        "description": "Saves a quick note or reminder to a text file.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "note_text": {
                    "type": "STRING",
                    "description": "The content of the note."
                },
                "title": {
                    "type": "STRING",
                    "description": "Optional title for the note."
                }
            },
            "required": ["note_text"]
        }
    },
    {
        "name": "lock_screen",
        "description": "Locks the computer workstation immediately.",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    },
    {
        "name": "empty_recycle_bin",
        "description": "Empties the Windows Recycle Bin.",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    }
]
