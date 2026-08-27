import os
import asyncio
import socket
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from config import BASE_DIR, TEMP_AUDIO_DIR, JARVIS_VOICE, JARVIS_SPEECH_RATE, JARVIS_PITCH
from core.sys_info import get_system_diagnostics
from core.brain import jarvis_brain
from core.voice import jarvis_voice

app = FastAPI(title="JARVIS Mobile Gateway")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WEB_DIR = BASE_DIR / "web"

class CommandRequest(BaseModel):
    command: str

@app.get("/")
async def serve_index():
    index_file = WEB_DIR / "index.html"
    return FileResponse(str(index_file))

@app.get("/manifest.json")
async def serve_manifest():
    manifest_file = WEB_DIR / "manifest.json"
    return FileResponse(str(manifest_file))

@app.get("/api/status")
async def get_status():
    return get_system_diagnostics()

@app.post("/api/command")
async def execute_command(req: CommandRequest):
    action_log = []
    
    def on_action(act_str):
        action_log.append(act_str)
        
    reply = jarvis_brain.process_command(req.command, on_action_callback=on_action)
    
    return {
        "reply": reply,
        "action": action_log[0] if action_log else None,
        "status": "success"
    }

@app.get("/api/speak")
async def generate_speech_stream(text: str):
    """Generates Edge-TTS audio stream on the fly and sends mp3 to mobile browser."""
    if not text:
        return Response(status_code=400)
        
    import edge_tts
    communicate = edge_tts.Communicate(text, JARVIS_VOICE, rate=JARVIS_SPEECH_RATE, pitch=JARVIS_PITCH)
    
    audio_bytes = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_bytes += chunk["data"]
            
    return Response(content=audio_bytes, media_type="audio/mpeg")

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def start_mobile_server(port: int = 5000):
    """Runs uvicorn in a background thread."""
    import uvicorn
    import threading
    
    ip = get_local_ip()
    print(f"\n[MOBILE LINK] JARVIS Mobile Server starting at: http://{ip}:{port}")
    
    config = uvicorn.Config(app=app, host="0.0.0.0", port=port, log_level="warning")
    server = uvicorn.Server(config)
    
    t = threading.Thread(target=server.run, daemon=True)
    t.start()
    return f"http://{ip}:{port}"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
