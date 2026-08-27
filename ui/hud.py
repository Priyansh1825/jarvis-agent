import os
import math
import time
import random
import threading
import datetime
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw, ImageOps
from config import ASSISTANT_NAME, USER_NAME, GEMINI_API_KEY, BASE_DIR
from core.sys_info import get_system_diagnostics
from core.brain import jarvis_brain
from core.voice import jarvis_voice

# ====================================================================
# CINEMATIC CYBERPUNK / PHOTOREALISTIC AI PALETTE
# ====================================================================
THEME = {
    "bg": "#03060E",               # Deep Space Void
    "card_bg": "#080D1A",          # Hologram Glass Card
    "card_inner": "#040710",       # Deep Inset
    "card_border": "#132038",      # Cyber Border
    "cyan": "#00E5FF",             # Stark Cyan (Default)
    "arc_blue": "#0088FF",         # Quantum Core Blue
    "gold": "#FFB800",             # Listening / Wake Gold
    "green": "#00FF88",            # Speaking / Active Green
    "red": "#FF3366",              # Alert Red
    "purple": "#9D00FF",           # Neural Core Purple
    "text_main": "#E6EDF3",        # Crisp White-Blue
    "text_dim": "#717D96",         # Subdued Tech Gray
    "font_tech": "Consolas",
    "font_main": "Segoe UI"
}

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ASSETS_DIR = BASE_DIR / "assets"

class PhotorealisticHumanoidFace(tk.Canvas):
    """
    Photorealistic Humanoid AI Face:
    - High-definition portrait of British Butler AI (JARVIS)
    - State-responsive facial expressions (Idle, Listening, Speaking, Thinking)
    - Dynamic rotating holographic tech rings & targeting reticles
    - Live audio spectrum equalizer waves
    - Sweeping cyber scanline and particle aura
    """
    def __init__(self, master, size=240, **kwargs):
        super().__init__(
            master, 
            width=size, 
            height=size, 
            bg=THEME["card_bg"], 
            highlightthickness=0, 
            **kwargs
        )
        self.size = size
        self.cx = size // 2
        self.cy = size // 2
        
        # State
        self.state_color = THEME["cyan"]
        self.status_text = "ONLINE"
        self.current_state = "idle"  # "idle", "listening", "speaking", "thinking"
        
        # Load & Prep Photorealistic Face Images
        self.images = {}
        self._load_face_images()
        
        # Animation parameters
        self.angle_outer = 0
        self.angle_inner = 0
        self.pulse = 0.0
        self.pulse_dir = 1
        self.scanline_y = 0
        self.wave_amplitudes = [0.1] * 16
        
        self._running = True
        self.after(35, self._animate)

    def _load_face_images(self):
        """Loads and crops avatar portraits into circular holographic tokens."""
        img_size = int(self.size * 0.76)
        mask = Image.new("L", (img_size, img_size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, img_size, img_size), fill=255)

        image_files = {
            "idle": ASSETS_DIR / "jarvis_idle.jpg",
            "speaking": ASSETS_DIR / "jarvis_speaking.jpg",
            "listening": ASSETS_DIR / "jarvis_listening.jpg",
            "thinking": ASSETS_DIR / "jarvis_idle.jpg"
        }

        for state_key, path in image_files.items():
            if path.exists():
                try:
                    pil_img = Image.open(path).convert("RGBA")
                    pil_img = ImageOps.fit(pil_img, (img_size, img_size), centering=(0.5, 0.45))
                    pil_img.putalpha(mask)
                    self.images[state_key] = ImageTk.PhotoImage(pil_img)
                except Exception:
                    pass

    def set_state(self, status: str, color: str = THEME["cyan"]):
        self.status_text = status
        self.state_color = color
        if status == "SPEAKING":
            self.current_state = "speaking"
        elif status == "LISTENING" or status == "WAKING UP":
            self.current_state = "listening"
        elif status == "THINKING" or status == "EXECUTING":
            self.current_state = "thinking"
        else:
            self.current_state = "idle"

    def _animate(self):
        if not self._running:
            return
            
        self.delete("all")
        cx, cy = self.cx, self.cy
        
        # 1. Outer Pulse Atmosphere
        self.pulse += 0.07 * self.pulse_dir
        if self.pulse > 1.0:
            self.pulse_dir = -1
        elif self.pulse < 0.0:
            self.pulse_dir = 1
            
        glow_r = int(self.size * 0.46 + self.pulse * 4)
        self.create_oval(
            cx - glow_r, cy - glow_r, cx + glow_r, cy + glow_r, 
            outline=self.state_color, width=1.5
        )

        # 2. Draw the Photorealistic Human Face Image
        active_img = self.images.get(self.current_state) or self.images.get("idle")
        if active_img:
            self.create_image(cx, cy - 2, image=active_img)
        else:
            # Fallback circle if image is loading
            face_r = int(self.size * 0.38)
            self.create_oval(cx - face_r, cy - face_r, cx + face_r, cy + face_r, fill="#08101E", outline=self.state_color)

        # 3. Rotating Cybernetic Hologram Reticle (Clockwise)
        self.angle_outer = (self.angle_outer + 2) % 360
        r_outer = int(self.size * 0.41)
        for i in range(0, 360, 45):
            rad = math.radians(self.angle_outer + i)
            x1 = cx + math.cos(rad) * (r_outer - 8)
            y1 = cy + math.sin(rad) * (r_outer - 8)
            x2 = cx + math.cos(rad) * (r_outer + 4)
            y2 = cy + math.sin(rad) * (r_outer + 4)
            self.create_line(x1, y1, x2, y2, fill=self.state_color, width=2.5)

        # 4. Counter-Rotating Inner Reticle (Counter-Clockwise)
        self.angle_inner = (self.angle_inner - 3) % 360
        r_inner = int(self.size * 0.38)
        self.create_oval(cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner, outline=self.state_color, width=1.5)

        # 5. Dynamic Audio Equalizer Waveform Overlay (Beneath the portrait)
        num_bars = len(self.wave_amplitudes)
        total_w = self.size * 0.7
        bar_w = total_w / num_bars
        start_x = cx - (total_w / 2)
        wave_y = cy + int(self.size * 0.34)

        for i in range(num_bars):
            if self.current_state == "speaking":
                target = random.uniform(0.3, 1.0)
            elif self.current_state == "listening":
                target = random.uniform(0.15, 0.6)
            else:
                target = 0.08 + math.sin(time.time() * 3 + i * 0.4) * 0.05

            self.wave_amplitudes[i] += (target - self.wave_amplitudes[i]) * 0.4
            bar_h = self.wave_amplitudes[i] * 18
            bx = start_x + (i * bar_w)
            
            self.create_rectangle(
                bx + 1, wave_y - bar_h / 2, bx + bar_w - 1, wave_y + bar_h / 2,
                fill=self.state_color, outline=""
            )

        # 6. Sweeping Hologram Scanline
        self.scanline_y = (self.scanline_y + 2.5) % self.size
        self.create_line(
            cx - r_inner, self.scanline_y, cx + r_inner, self.scanline_y,
            fill=self.state_color, width=1, dash=(3, 5)
        )

        # 7. Holographic Status Badge
        self.create_text(
            cx, self.size - 12, 
            text=f"● HUMAN AI: {self.status_text} ●", 
            fill=self.state_color, 
            font=(THEME["font_tech"], 10, "bold")
        )

        self.after(35, self._animate)

    def stop(self):
        self._running = False


class JarvisHUD(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Futuristic Cyber Window Setup
        self.title("J.A.R.V.I.S. // STARK INDUSTRIES MARK VII - HUMAN AI")
        self.geometry("1040x730")
        self.minsize(880, 640)
        self.configure(fg_color=THEME["bg"])
        
        self.is_processing = False
        self.wake_listener_active = True
        self.stop_wake_event = threading.Event()
        
        # Build Interface
        self._build_top_hud_banner()
        self._build_main_grid()
        self._build_bottom_cyber_console()
        
        # Timers & Loops
        self.after(1000, self._update_system_metrics)
        self.after(500, self._boot_greeting)
        self._start_wake_word_thread()

    def _build_top_hud_banner(self):
        """Top Holographic Banner"""
        top_frame = ctk.CTkFrame(
            self, 
            fg_color=THEME["card_bg"], 
            corner_radius=12, 
            border_width=1, 
            border_color=THEME["card_border"]
        )
        top_frame.pack(fill="x", padx=16, pady=(14, 8))

        brand_box = ctk.CTkFrame(top_frame, fg_color="transparent")
        brand_box.pack(side="left", padx=18, pady=10)

        title_lbl = ctk.CTkLabel(
            brand_box, 
            text="J · A · R · V · I · S", 
            font=ctk.CTkFont(family="Orbitron", size=22, weight="bold"),
            text_color=THEME["cyan"]
        )
        title_lbl.pack(anchor="w")

        sub_lbl = ctk.CTkLabel(
            brand_box, 
            text="PHOTOREALISTIC HUMAN AI AVATAR · STARK MARK VII", 
            font=ctk.CTkFont(family=THEME["font_tech"], size=9, weight="bold"),
            text_color=THEME["text_dim"]
        )
        sub_lbl.pack(anchor="w")

        status_box = ctk.CTkFrame(top_frame, fg_color="transparent")
        status_box.pack(side="right", padx=18, pady=10)

        self.clock_lbl = ctk.CTkLabel(
            status_box, 
            text="00:00:00", 
            font=ctk.CTkFont(family=THEME["font_tech"], size=16, weight="bold"),
            text_color=THEME["text_main"]
        )
        self.clock_lbl.pack(anchor="e")

        api_status = "CLOUD CORE ONLINE" if jarvis_brain.is_configured() else "API KEY REQUIRED"
        api_color = THEME["green"] if jarvis_brain.is_configured() else THEME["gold"]
        
        self.cloud_badge = ctk.CTkLabel(
            status_box, 
            text=f"● {api_status}", 
            font=ctk.CTkFont(family=THEME["font_tech"], size=10, weight="bold"),
            text_color=api_color
        )
        self.cloud_badge.pack(anchor="e")

    def _build_main_grid(self):
        """Two-Column Cyber Layout: Left (Photorealistic Face + Gauges), Right (Log + Shortcuts)"""
        grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True, padx=16, pady=4)

        # -------------------------------------------------------------
        # LEFT COLUMN (Photorealistic Human Face + Hardware Telemetry)
        # -------------------------------------------------------------
        left_col = ctk.CTkFrame(grid_frame, width=340, fg_color="transparent")
        left_col.pack(side="left", fill="y", padx=(0, 10))

        # Face Card
        face_card = ctk.CTkFrame(
            left_col, 
            fg_color=THEME["card_bg"], 
            corner_radius=12, 
            border_width=1, 
            border_color=THEME["card_border"]
        )
        face_card.pack(fill="x", pady=(0, 8))

        core_lbl = ctk.CTkLabel(
            face_card, 
            text="HUMANOID AI AVATAR", 
            font=ctk.CTkFont(family=THEME["font_tech"], size=10, weight="bold"),
            text_color=THEME["text_dim"]
        )
        core_lbl.pack(pady=(10, 0))

        # Photorealistic Human AI Face
        self.ai_face = PhotorealisticHumanoidFace(face_card, size=230)
        self.ai_face.pack(pady=(6, 12))

        # Hardware Metrics Card
        metrics_card = ctk.CTkFrame(
            left_col, 
            fg_color=THEME["card_bg"], 
            corner_radius=12, 
            border_width=1, 
            border_color=THEME["card_border"]
        )
        metrics_card.pack(fill="both", expand=True)

        metric_header = ctk.CTkLabel(
            metrics_card, 
            text="HARDWARE DIAGNOSTICS", 
            font=ctk.CTkFont(family=THEME["font_tech"], size=10, weight="bold"),
            text_color=THEME["text_dim"]
        )
        metric_header.pack(anchor="w", padx=14, pady=(8, 4))

        # CPU Progress
        self.cpu_label = ctk.CTkLabel(metrics_card, text="CPU: 0%", font=ctk.CTkFont(family=THEME["font_tech"], size=11), text_color=THEME["text_main"])
        self.cpu_label.pack(anchor="w", padx=14)
        self.cpu_bar = ctk.CTkProgressBar(metrics_card, height=6, progress_color=THEME["cyan"], fg_color="#10192A")
        self.cpu_bar.pack(fill="x", padx=14, pady=(1, 6))
        self.cpu_bar.set(0.1)

        # RAM Progress
        self.ram_label = ctk.CTkLabel(metrics_card, text="RAM: 0.0 GB / 0.0 GB", font=ctk.CTkFont(family=THEME["font_tech"], size=11), text_color=THEME["text_main"])
        self.ram_label.pack(anchor="w", padx=14)
        self.ram_bar = ctk.CTkProgressBar(metrics_card, height=6, progress_color=THEME["arc_blue"], fg_color="#10192A")
        self.ram_bar.pack(fill="x", padx=14, pady=(1, 6))
        self.ram_bar.set(0.1)

        # Battery / Storage
        self.bat_label = ctk.CTkLabel(metrics_card, text="POWER: Checking...", font=ctk.CTkFont(family=THEME["font_tech"], size=11), text_color=THEME["text_main"])
        self.bat_label.pack(anchor="w", padx=14)
        self.bat_bar = ctk.CTkProgressBar(metrics_card, height=6, progress_color=THEME["green"], fg_color="#10192A")
        self.bat_bar.pack(fill="x", padx=14, pady=(1, 10))
        self.bat_bar.set(0.5)

        # -------------------------------------------------------------
        # RIGHT COLUMN (Quick Action Cyber Deck + Terminal Console)
        # -------------------------------------------------------------
        right_col = ctk.CTkFrame(grid_frame, fg_color="transparent")
        right_col.pack(side="right", fill="both", expand=True)

        # Quick Actions Bar
        actions_bar = ctk.CTkFrame(
            right_col, 
            fg_color=THEME["card_bg"], 
            corner_radius=12, 
            border_width=1, 
            border_color=THEME["card_border"]
        )
        actions_bar.pack(fill="x", pady=(0, 8))

        act_title = ctk.CTkLabel(
            actions_bar, 
            text="QUICK PROTOCOL SHORTCUTS", 
            font=ctk.CTkFont(family=THEME["font_tech"], size=10, weight="bold"),
            text_color=THEME["text_dim"]
        )
        act_title.pack(anchor="w", padx=14, pady=(8, 4))

        btn_grid = ctk.CTkFrame(actions_bar, fg_color="transparent")
        btn_grid.pack(fill="x", padx=10, pady=(0, 10))

        shortcuts = [
            ("📊 Status", lambda: self._execute_quick_action("Report full system status")),
            ("🧮 Calc", lambda: self._execute_quick_action("Open calculator")),
            ("🎵 YouTube", lambda: self._execute_quick_action("Play Iron Man theme on YouTube")),
            ("📸 Screen", lambda: self._execute_quick_action("Take a screenshot")),
            ("🧹 Clean", lambda: self._execute_quick_action("Empty recycle bin")),
            ("🔒 Lock", lambda: self._execute_quick_action("Lock workstation"))
        ]

        for idx, (label, cmd_func) in enumerate(shortcuts):
            btn = ctk.CTkButton(
                btn_grid, 
                text=label, 
                font=ctk.CTkFont(family=THEME["font_tech"], size=11, weight="bold"),
                fg_color="#101828",
                hover_color="#182740",
                text_color=THEME["cyan"],
                border_width=1,
                border_color=THEME["card_border"],
                height=30,
                width=80,
                command=cmd_func
            )
            btn.grid(row=0, column=idx, padx=3, sticky="ew")
            btn_grid.columnconfigure(idx, weight=1)

        # Hologram Terminal Card
        console_card = ctk.CTkFrame(
            right_col, 
            fg_color=THEME["card_bg"], 
            corner_radius=12, 
            border_width=1, 
            border_color=THEME["card_border"]
        )
        console_card.pack(fill="both", expand=True)

        console_hdr = ctk.CTkFrame(console_card, fg_color="transparent")
        console_hdr.pack(fill="x", padx=14, pady=(8, 4))

        console_title = ctk.CTkLabel(
            console_hdr, 
            text="HOLOGRAPHIC TRANSMISSION CONSOLE", 
            font=ctk.CTkFont(family=THEME["font_tech"], size=10, weight="bold"),
            text_color=THEME["text_dim"]
        )
        console_title.pack(side="left")

        self.wake_switch = ctk.CTkSwitch(
            console_hdr,
            text="Voice Wake ('Hey Jarvis')",
            font=ctk.CTkFont(family=THEME["font_tech"], size=10, weight="bold"),
            progress_color=THEME["cyan"],
            command=self._toggle_wake_word
        )
        self.wake_switch.select()
        self.wake_switch.pack(side="right", padx=(10, 0))

        clear_btn = ctk.CTkButton(
            console_hdr, 
            text="CLEAR", 
            width=46, 
            height=20, 
            font=ctk.CTkFont(size=9, weight="bold"),
            fg_color="#141E30", 
            hover_color="#1E2C44",
            command=self._clear_console
        )
        clear_btn.pack(side="right")

        self.console = ctk.CTkTextbox(
            console_card, 
            font=ctk.CTkFont(family="Consolas", size=13),
            fg_color=THEME["card_inner"],
            text_color=THEME["text_main"],
            border_width=1,
            border_color="#121B2C",
            corner_radius=8
        )
        self.console.pack(fill="both", expand=True, padx=14, pady=(0, 12))

    def _build_bottom_cyber_console(self):
        """Bottom Control Bar with Big Voice Button and Command Line"""
        control_frame = ctk.CTkFrame(
            self, 
            fg_color=THEME["card_bg"], 
            corner_radius=12, 
            border_width=1, 
            border_color=THEME["card_border"]
        )
        control_frame.pack(fill="x", padx=16, pady=(0, 14))

        inner = ctk.CTkFrame(control_frame, fg_color="transparent")
        inner.pack(fill="x", padx=12, pady=10)

        self.voice_btn = ctk.CTkButton(
            inner, 
            text="🎙️ ACTIVATE VOICE", 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=THEME["cyan"],
            text_color="#000000",
            hover_color="#52EFFF",
            height=42,
            width=180,
            command=self._trigger_voice_command
        )
        self.voice_btn.pack(side="left", padx=(0, 10))

        self.cmd_entry = ctk.CTkEntry(
            inner, 
            placeholder_text="Say 'Hey Jarvis' or enter a command (e.g. 'Open VS Code', 'Play music', 'System report')...",
            font=ctk.CTkFont(size=13),
            height=42,
            fg_color=THEME["card_inner"],
            border_color=THEME["card_border"]
        )
        self.cmd_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.cmd_entry.bind("<Return>", lambda e: self._trigger_text_command())

        self.send_btn = ctk.CTkButton(
            inner, 
            text="SEND", 
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#141E30",
            hover_color="#1E2C44",
            text_color=THEME["cyan"],
            height=42,
            width=70,
            command=self._trigger_text_command
        )
        self.send_btn.pack(side="left", padx=(0, 8))

        self.settings_btn = ctk.CTkButton(
            inner, 
            text="⚙️", 
            font=ctk.CTkFont(size=16),
            fg_color="#141E30",
            hover_color="#1E2C44",
            height=42,
            width=42,
            command=self._open_settings_dialog
        )
        self.settings_btn.pack(side="left")

    def log(self, tag: str, message: str, color_hex: str = None):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.console.configure(state="normal")
        self.console.insert("end", f"[{timestamp}] [{tag}] {message}\n\n")
        self.console.configure(state="disabled")
        self.console.see("end")

    def _clear_console(self):
        self.console.configure(state="normal")
        self.console.delete("1.0", "end")
        self.console.configure(state="disabled")

    def _update_system_metrics(self):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.clock_lbl.configure(text=now)

        try:
            stats = get_system_diagnostics()
            cpu = stats["cpu_usage_percent"]
            self.cpu_label.configure(text=f"CPU: {cpu}% ({stats['cpu_threads']} Threads)")
            self.cpu_bar.set(min(cpu / 100.0, 1.0))
            
            ram_pct = stats["ram_usage_percent"]
            self.ram_label.configure(text=f"RAM: {stats['ram_used_gb']} GB / {stats['ram_total_gb']} GB ({ram_pct}%)")
            self.ram_bar.set(min(ram_pct / 100.0, 1.0))
            
            bat = stats["battery"]
            if bat["present"]:
                charging = "⚡ Charging" if bat["power_plugged"] else "🔋 Battery"
                self.bat_label.configure(text=f"POWER: {bat['percent']}% ({charging})")
                self.bat_bar.set(min(bat["percent"] / 100.0, 1.0))
            else:
                self.bat_label.configure(text=f"POWER: AC Online (Drive: {stats['disk_free_gb']}GB Free)")
                self.bat_bar.set(1.0)
        except Exception:
            pass

        self.after(2000, self._update_system_metrics)

    def _boot_greeting(self):
        from core.server import get_local_ip
        local_ip = get_local_ip()
        self.log("SYSTEM", "J.A.R.V.I.S. Humanoid AI Core Online. Background Wake Word Listener Active.")
        self.log("MOBILE", f"📱 Mobile Phone Link: http://{local_ip}:5000 (Open in phone browser to install APK)", THEME["cyan"])
        if not jarvis_brain.is_configured():
            self.log("ALERT", "Gemini API Key is not set. Click ⚙️ in the bottom right to paste your free Gemini API key.", THEME["gold"])
        else:
            self.log("SYSTEM", "All systems nominal, sir. Photorealistic AI Avatar online. Say 'Hey Jarvis' or click Activate.")

    def _execute_quick_action(self, action_text: str):
        if self.is_processing:
            return
        threading.Thread(target=self._process_command_thread, args=(action_text,), daemon=True).start()

    # ==========================================
    # WAKE WORD LISTENER ENGINE
    # ==========================================
    def _start_wake_word_thread(self):
        self.stop_wake_event.clear()
        self.wake_thread = threading.Thread(target=self._wake_word_loop, daemon=True)
        self.wake_thread.start()

    def _toggle_wake_word(self):
        self.wake_listener_active = bool(self.wake_switch.get())
        if self.wake_listener_active:
            self.log("SYSTEM", "Wake Word detection ENABLED. Say 'Hey Jarvis' to activate.")
        else:
            self.log("SYSTEM", "Wake Word detection DISABLED.")

    def _wake_word_loop(self):
        def on_wake_detected(detected_phrase):
            if not self.wake_listener_active or self.is_processing:
                return

            self.log("WAKE", f"Wake phrase detected: '{detected_phrase}'")
            
            for prefix in ["hey jarvis", "wake up jarvis", "hello jarvis", "jarvis"]:
                if prefix in detected_phrase:
                    remaining = detected_phrase.split(prefix, 1)[-1].strip()
                    if remaining:
                        threading.Thread(target=self._process_command_thread, args=(remaining,), daemon=True).start()
                        return

            threading.Thread(target=self._wake_and_listen_worker, daemon=True).start()

        jarvis_voice.listen_for_wake_word(
            wake_words=["jarvis", "hey jarvis", "wake up jarvis", "hello jarvis"],
            stop_event=self.stop_wake_event,
            on_wake=on_wake_detected
        )

    def _wake_and_listen_worker(self):
        if self.is_processing:
            return
        self.is_processing = True
        self.ai_face.set_state("WAKING UP", THEME["gold"])
        self.voice_btn.configure(state="disabled", text="LISTENING...")
        self.log("JARVIS", "Yes, sir? I am listening.")
        
        jarvis_voice.speak("Yes sir, I am listening.")
        
        self.ai_face.set_state("LISTENING", THEME["gold"])
        query = jarvis_voice.listen(timeout=6, phrase_limit=10)

        if not query:
            self.log("VOICE", "No speech detected.")
            self.ai_face.set_state("ONLINE", THEME["cyan"])
            self.voice_btn.configure(state="normal", text="🎙️ ACTIVATE VOICE")
            self.is_processing = False
            return

        self._process_command_thread(query)

    # ==========================================
    # COMMAND PROCESSING
    # ==========================================
    def _trigger_text_command(self):
        if self.is_processing:
            return
        cmd = self.cmd_entry.get().strip()
        if not cmd:
            return
        self.cmd_entry.delete(0, "end")
        threading.Thread(target=self._process_command_thread, args=(cmd,), daemon=True).start()

    def _trigger_voice_command(self):
        if self.is_processing:
            return
        threading.Thread(target=self._manual_voice_worker, daemon=True).start()

    def _manual_voice_worker(self):
        self.is_processing = True
        self.voice_btn.configure(state="disabled", text="LISTENING...")
        self.ai_face.set_state("LISTENING", THEME["gold"])
        self.log("VOICE", "Listening for your command...")

        query = jarvis_voice.listen(timeout=6, phrase_limit=10)

        if not query:
            self.log("VOICE", "No audio detected or speech could not be parsed.")
            self.ai_face.set_state("ONLINE", THEME["cyan"])
            self.voice_btn.configure(state="normal", text="🎙️ ACTIVATE VOICE")
            self.is_processing = False
            return

        self._process_command_thread(query)

    def _process_command_thread(self, query: str):
        self.is_processing = True
        self.voice_btn.configure(state="disabled", text="PROCESSING...")
        self.log("USER", query)
        self.ai_face.set_state("THINKING", THEME["arc_blue"])

        def on_action(action_str):
            self.log("ACTION", action_str)
            self.ai_face.set_state("EXECUTING", THEME["green"])

        # Process with Cloud Brain
        response_text = jarvis_brain.process_command(query, on_action_callback=on_action)

        # Spoken Response
        self.log(ASSISTANT_NAME, response_text)
        self.ai_face.set_state("SPEAKING", THEME["green"])
        self.voice_btn.configure(text="SPEAKING...")

        jarvis_voice.speak(response_text)

        # Reset state
        self.ai_face.set_state("ONLINE", THEME["cyan"])
        self.voice_btn.configure(state="normal", text="🎙️ ACTIVATE VOICE")
        self.is_processing = False

    def _open_settings_dialog(self):
        """Settings Dialog to enter/update Gemini API Key"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Settings // API Configuration")
        dialog.geometry("520x280")
        dialog.configure(fg_color=THEME["card_bg"])
        dialog.grab_set()

        lbl = ctk.CTkLabel(
            dialog, 
            text="Cloud Brain API Configuration", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=THEME["cyan"]
        )
        lbl.pack(padx=20, pady=(20, 5))

        desc = ctk.CTkLabel(
            dialog, 
            text="Enter your Google Gemini API key (Free at aistudio.google.com):",
            font=ctk.CTkFont(size=12),
            text_color=THEME["text_dim"]
        )
        desc.pack(padx=20, pady=(0, 15))

        key_entry = ctk.CTkEntry(
            dialog, 
            width=460, 
            height=40, 
            font=ctk.CTkFont(family="Consolas", size=12),
            placeholder_text="AIzaSy..."
        )
        key_entry.pack(padx=20, pady=(0, 15))
        if jarvis_brain.is_configured():
            key_entry.insert(0, jarvis_brain.api_key)

        def save_key():
            new_key = key_entry.get().strip()
            if new_key:
                jarvis_brain.set_api_key(new_key)
                
                env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
                try:
                    with open(env_path, "w", encoding="utf-8") as f:
                        f.write(f"GEMINI_API_KEY={new_key}\nGEMINI_MODEL=gemini-2.5-flash\nJARVIS_VOICE=en-GB-RyanNeural\n")
                except Exception:
                    pass

                self.cloud_badge.configure(text="● CLOUD CORE ONLINE", text_color=THEME["green"])
                self.log("SYSTEM", "Gemini Cloud API Key configured successfully!")
                dialog.destroy()

        save_btn = ctk.CTkButton(
            dialog, 
            text="SAVE & ACTIVATE BRAIN", 
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=THEME["cyan"],
            text_color="#000000",
            hover_color="#52EFFF",
            height=38,
            command=save_key
        )
        save_btn.pack(pady=10)

if __name__ == "__main__":
    app = JarvisHUD()
    app.mainloop()
