import os
import math
import time
import threading
import datetime
import tkinter as tk
import customtkinter as ctk
from config import ASSISTANT_NAME, USER_NAME, GEMINI_API_KEY
from core.sys_info import get_system_diagnostics
from core.brain import jarvis_brain
from core.voice import jarvis_voice

# UI Color Palette
THEME = {
    "bg": "#0B0E14",
    "card_bg": "#121722",
    "card_border": "#1F293D",
    "cyan": "#00E5FF",
    "arc_blue": "#0099FF",
    "glow_blue": "#0055FF",
    "gold": "#FFB300",
    "green": "#00FF88",
    "red": "#FF3366",
    "text_main": "#E6EDF3",
    "text_dim": "#7D8590",
    "font_family": "Segoe UI"
}

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ArcReactorCanvas(tk.Canvas):
    """Custom Canvas that draws and animates an Iron Man Arc Reactor with glowing rings and pulses."""
    def __init__(self, master, size=180, **kwargs):
        super().__init__(
            master, 
            width=size, 
            height=size, 
            bg=THEME["card_bg"], 
            highlightthickness=0, 
            **kwargs
        )
        self.size = size
        self.center = size // 2
        self.angle = 0
        self.pulse = 0
        self.pulse_dir = 1
        self.state_color = THEME["cyan"]
        self.status_text = "STANDBY"
        self._running = True
        self.after(50, self._animate)

    def set_state(self, status: str, color: str = THEME["cyan"]):
        self.status_text = status
        self.state_color = color

    def _animate(self):
        if not self._running:
            return
            
        self.delete("all")
        c = self.center
        
        # 1. Pulsing Outer Glow Ring
        self.pulse += 0.08 * self.pulse_dir
        if self.pulse > 1.0:
            self.pulse_dir = -1
        elif self.pulse < 0.0:
            self.pulse_dir = 1
            
        glow_r = int(self.size * 0.44 + self.pulse * 4)
        self.create_oval(
            c - glow_r, c - glow_r, c + glow_r, c + glow_r, 
            outline=self.state_color, width=2
        )

        # 2. Main Outer Tech Ring
        r1 = int(self.size * 0.38)
        self.create_oval(c - r1, c - r1, c + r1, c + r1, outline=THEME["card_border"], width=6)
        self.create_oval(c - r1, c - r1, c + r1, c + r1, outline=self.state_color, width=2)

        # 3. Rotating Segments
        self.angle = (self.angle + 2) % 360
        num_segments = 8
        for i in range(num_segments):
            theta = math.radians(self.angle + i * (360 / num_segments))
            x1 = c + math.cos(theta) * (r1 - 10)
            y1 = c + math.sin(theta) * (r1 - 10)
            x2 = c + math.cos(theta) * (r1 + 2)
            y2 = c + math.sin(theta) * (r1 + 2)
            self.create_line(x1, y1, x2, y2, fill=self.state_color, width=3)

        # 4. Inner Ring & Center Core
        r2 = int(self.size * 0.22)
        self.create_oval(c - r2, c - r2, c + r2, c + r2, fill="#081524", outline=self.state_color, width=2)

        r3 = int(self.size * 0.12 + self.pulse * 2)
        self.create_oval(c - r3, c - r3, c + r3, c + r3, fill=self.state_color, outline="#FFFFFF", width=1)

        # 5. Central Status label
        self.create_text(
            c, self.size - 14, 
            text=self.status_text, 
            fill=self.state_color, 
            font=(THEME["font_family"], 9, "bold")
        )

        self.after(40, self._animate)

    def stop(self):
        self._running = False


class JarvisHUD(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.title("J.A.R.V.I.S. // STARK INDUSTRIES MARK VII")
        self.geometry("980x700")
        self.minsize(820, 620)
        self.configure(fg_color=THEME["bg"])
        
        self.is_processing = False
        self.wake_listener_active = True
        self.stop_wake_event = threading.Event()
        
        # Build Interface
        self._build_header()
        self._build_main_layout()
        self._build_controls()
        
        # Start background metrics updater & Wake Word Listener
        self.after(1000, self._update_system_metrics)
        self.after(500, self._boot_greeting)
        self._start_wake_word_thread()

    def _build_header(self):
        """Top Header Bar with Branding, Clock, and Cloud Status"""
        header_frame = ctk.CTkFrame(self, fg_color=THEME["card_bg"], corner_radius=10, border_width=1, border_color=THEME["card_border"])
        header_frame.pack(fill="x", padx=20, pady=(15, 10))

        # Title & Subtitle
        title_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_box.pack(side="left", padx=20, pady=10)

        title_lbl = ctk.CTkLabel(
            title_box, 
            text="J . A . R . V . I . S .", 
            font=ctk.CTkFont(family=THEME["font_family"], size=22, weight="bold"),
            text_color=THEME["cyan"]
        )
        title_lbl.pack(anchor="w")

        sub_lbl = ctk.CTkLabel(
            title_box, 
            text="CLOUD INTELLIGENCE & VOICE AUTOMATION PROTOCOL", 
            font=ctk.CTkFont(family=THEME["font_family"], size=10, weight="normal"),
            text_color=THEME["text_dim"]
        )
        sub_lbl.pack(anchor="w")

        # Right stats: Clock & Cloud badge
        right_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        right_box.pack(side="right", padx=20, pady=10)

        self.clock_lbl = ctk.CTkLabel(
            right_box, 
            text="00:00:00", 
            font=ctk.CTkFont(family="Consolas", size=16, weight="bold"),
            text_color=THEME["text_main"]
        )
        self.clock_lbl.pack(anchor="e")

        api_status = "CLOUD BRAIN ONLINE" if jarvis_brain.is_configured() else "API KEY REQUIRED"
        api_color = THEME["green"] if jarvis_brain.is_configured() else THEME["gold"]
        
        self.cloud_badge = ctk.CTkLabel(
            right_box, 
            text=f"● {api_status}", 
            font=ctk.CTkFont(family=THEME["font_family"], size=10, weight="bold"),
            text_color=api_color
        )
        self.cloud_badge.pack(anchor="e")

    def _build_main_layout(self):
        """Two Column Grid: Left Column (Arc Reactor + Metrics), Right Column (Cyber Console)"""
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.pack(fill="both", expand=True, padx=20, pady=5)

        # Left Column
        left_col = ctk.CTkFrame(self.main_content, width=320, fg_color="transparent")
        left_col.pack(side="left", fill="y", padx=(0, 10))

        # Arc Reactor Card
        reactor_card = ctk.CTkFrame(left_col, fg_color=THEME["card_bg"], corner_radius=10, border_width=1, border_color=THEME["card_border"])
        reactor_card.pack(fill="x", pady=(0, 10))

        reactor_title = ctk.CTkLabel(
            reactor_card, 
            text="CORE REACTOR", 
            font=ctk.CTkFont(family=THEME["font_family"], size=12, weight="bold"),
            text_color=THEME["text_dim"]
        )
        reactor_title.pack(pady=(10, 0))

        self.reactor = ArcReactorCanvas(reactor_card, size=190)
        self.reactor.pack(pady=10)

        # System Metrics Card
        metrics_card = ctk.CTkFrame(left_col, fg_color=THEME["card_bg"], corner_radius=10, border_width=1, border_color=THEME["card_border"])
        metrics_card.pack(fill="x")

        metrics_title = ctk.CTkLabel(
            metrics_card, 
            text="HARDWARE DIAGNOSTICS", 
            font=ctk.CTkFont(family=THEME["font_family"], size=12, weight="bold"),
            text_color=THEME["text_dim"]
        )
        metrics_title.pack(anchor="w", padx=15, pady=(10, 5))

        # CPU Metric
        self.cpu_label = ctk.CTkLabel(metrics_card, text="CPU: 0%", font=ctk.CTkFont(size=11), text_color=THEME["text_main"])
        self.cpu_label.pack(anchor="w", padx=15)
        self.cpu_bar = ctk.CTkProgressBar(metrics_card, height=8, progress_color=THEME["cyan"], fg_color="#1E2638")
        self.cpu_bar.pack(fill="x", padx=15, pady=(2, 8))
        self.cpu_bar.set(0.1)

        # RAM Metric
        self.ram_label = ctk.CTkLabel(metrics_card, text="RAM: 0.0 GB / 0.0 GB (0%)", font=ctk.CTkFont(size=11), text_color=THEME["text_main"])
        self.ram_label.pack(anchor="w", padx=15)
        self.ram_bar = ctk.CTkProgressBar(metrics_card, height=8, progress_color=THEME["arc_blue"], fg_color="#1E2638")
        self.ram_bar.pack(fill="x", padx=15, pady=(2, 8))
        self.ram_bar.set(0.1)

        # Battery / Power Metric
        self.bat_label = ctk.CTkLabel(metrics_card, text="POWER: Checking...", font=ctk.CTkFont(size=11), text_color=THEME["text_main"])
        self.bat_label.pack(anchor="w", padx=15)
        self.bat_bar = ctk.CTkProgressBar(metrics_card, height=8, progress_color=THEME["green"], fg_color="#1E2638")
        self.bat_bar.pack(fill="x", padx=15, pady=(2, 12))
        self.bat_bar.set(0.5)

        # Right Column (Terminal Console Log)
        right_col = ctk.CTkFrame(self.main_content, fg_color=THEME["card_bg"], corner_radius=10, border_width=1, border_color=THEME["card_border"])
        right_col.pack(side="right", fill="both", expand=True)

        console_hdr = ctk.CTkFrame(right_col, fg_color="transparent")
        console_hdr.pack(fill="x", padx=15, pady=(10, 5))

        console_title = ctk.CTkLabel(
            console_hdr, 
            text="TRANSMISSION & ACTION CONSOLE", 
            font=ctk.CTkFont(family=THEME["font_family"], size=12, weight="bold"),
            text_color=THEME["text_dim"]
        )
        console_title.pack(side="left")

        # Wake Word Toggle Switch
        self.wake_switch = ctk.CTkSwitch(
            console_hdr,
            text="Wake Word ('Hey Jarvis')",
            font=ctk.CTkFont(size=11),
            progress_color=THEME["cyan"],
            command=self._toggle_wake_word
        )
        self.wake_switch.select()
        self.wake_switch.pack(side="right", padx=(10, 0))

        clear_btn = ctk.CTkButton(
            console_hdr, 
            text="CLEAR", 
            width=50, 
            height=20, 
            font=ctk.CTkFont(size=10),
            fg_color="#1F293D", 
            hover_color="#2D3A54",
            command=self._clear_console
        )
        clear_btn.pack(side="right")

        self.console = ctk.CTkTextbox(
            right_col, 
            font=ctk.CTkFont(family="Consolas", size=13),
            fg_color="#080C14",
            text_color=THEME["text_main"],
            border_width=1,
            border_color="#1A2234",
            corner_radius=6
        )
        self.console.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def _build_controls(self):
        """Bottom Action & Command Bar"""
        control_frame = ctk.CTkFrame(self, fg_color=THEME["card_bg"], corner_radius=10, border_width=1, border_color=THEME["card_border"])
        control_frame.pack(fill="x", padx=20, pady=(0, 15))

        inner = ctk.CTkFrame(control_frame, fg_color="transparent")
        inner.pack(fill="x", padx=15, pady=12)

        # Voice Button
        self.voice_btn = ctk.CTkButton(
            inner, 
            text="🎙️ ACTIVATE VOICE", 
            font=ctk.CTkFont(family=THEME["font_family"], size=14, weight="bold"),
            fg_color=THEME["cyan"],
            text_color="#000000",
            hover_color="#4DF0FF",
            height=42,
            width=170,
            command=self._trigger_voice_command
        )
        self.voice_btn.pack(side="left", padx=(0, 12))

        # Text Command Input
        self.cmd_entry = ctk.CTkEntry(
            inner, 
            placeholder_text="Say 'Hey Jarvis' or type a command ('Open Chrome', 'Play music on YouTube', 'System status')...",
            font=ctk.CTkFont(size=13),
            height=42,
            fg_color="#080C14",
            border_color="#1F293D"
        )
        self.cmd_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.cmd_entry.bind("<Return>", lambda e: self._trigger_text_command())

        # Send Button
        self.send_btn = ctk.CTkButton(
            inner, 
            text="SEND", 
            font=ctk.CTkFont(family=THEME["font_family"], size=13, weight="bold"),
            fg_color="#1F293D",
            hover_color="#2D3A54",
            height=42,
            width=80,
            command=self._trigger_text_command
        )
        self.send_btn.pack(side="left", padx=(0, 8))

        # API Settings Button
        self.settings_btn = ctk.CTkButton(
            inner, 
            text="⚙️", 
            font=ctk.CTkFont(size=16),
            fg_color="#1A2234",
            hover_color="#26344E",
            height=42,
            width=42,
            command=self._open_settings_dialog
        )
        self.settings_btn.pack(side="left")

    def log(self, tag: str, message: str, color_hex: str = None):
        """Appends formatted message to console."""
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
        """Updates hardware stats every 2 seconds"""
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.clock_lbl.configure(text=now)

        try:
            stats = get_system_diagnostics()
            # CPU
            cpu = stats["cpu_usage_percent"]
            self.cpu_label.configure(text=f"CPU: {cpu}% ({stats['cpu_threads']} Threads)")
            self.cpu_bar.set(min(cpu / 100.0, 1.0))
            
            # RAM
            ram_pct = stats["ram_usage_percent"]
            self.ram_label.configure(text=f"RAM: {stats['ram_used_gb']} GB / {stats['ram_total_gb']} GB ({ram_pct}%)")
            self.ram_bar.set(min(ram_pct / 100.0, 1.0))
            
            # Battery
            bat = stats["battery"]
            if bat["present"]:
                charging = "⚡ Charging" if bat["power_plugged"] else "🔋 On Battery"
                self.bat_label.configure(text=f"POWER: {bat['percent']}% ({charging})")
                self.bat_bar.set(min(bat["percent"] / 100.0, 1.0))
            else:
                self.bat_label.configure(text=f"POWER: AC Power (Drive: {stats['disk_free_gb']}GB Free)")
                self.bat_bar.set(1.0)
        except Exception:
            pass

        self.after(2000, self._update_system_metrics)

    def _boot_greeting(self):
        """Initial startup welcome sequence."""
        self.log("SYSTEM", "J.A.R.V.I.S. Mark VII Core Online. Background Wake Word Listener Active.")
        if not jarvis_brain.is_configured():
            self.log("ALERT", "Gemini API Key is not set. Click ⚙️ in the bottom right to paste your free Gemini API key.", THEME["gold"])
        else:
            self.log("SYSTEM", f"Ready to serve. Say 'Hey Jarvis' or press '🎙️ ACTIVATE VOICE'.")

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
        """Background loop continuously scanning for wake words."""
        def on_wake_detected(detected_phrase):
            if not self.wake_listener_active or self.is_processing:
                return

            self.log("WAKE", f"Wake phrase detected: '{detected_phrase}'")
            
            # Check if user already gave a command in the same breath (e.g. "hey jarvis open calculator")
            for prefix in ["hey jarvis", "wake up jarvis", "hello jarvis", "jarvis"]:
                if prefix in detected_phrase:
                    remaining = detected_phrase.split(prefix, 1)[-1].strip()
                    if remaining:
                        threading.Thread(target=self._process_command_thread, args=(remaining,), daemon=True).start()
                        return

            # Otherwise, greet and listen for full command
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
        self.reactor.set_state("WAKING UP", THEME["gold"])
        self.voice_btn.configure(state="disabled", text="LISTENING...")
        self.log("JARVIS", "Yes, sir? I am listening.")
        
        jarvis_voice.speak("Yes sir, I am listening.")
        
        self.reactor.set_state("LISTENING", THEME["gold"])
        query = jarvis_voice.listen(timeout=6, phrase_limit=10)

        if not query:
            self.log("VOICE", "No speech detected.")
            self.reactor.set_state("STANDBY", THEME["cyan"])
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
        self.reactor.set_state("LISTENING", THEME["gold"])
        self.log("VOICE", "Listening for your command...")

        query = jarvis_voice.listen(timeout=6, phrase_limit=10)

        if not query:
            self.log("VOICE", "No audio detected or speech could not be parsed.")
            self.reactor.set_state("STANDBY", THEME["cyan"])
            self.voice_btn.configure(state="normal", text="🎙️ ACTIVATE VOICE")
            self.is_processing = False
            return

        self._process_command_thread(query)

    def _process_command_thread(self, query: str):
        self.is_processing = True
        self.voice_btn.configure(state="disabled", text="PROCESSING...")
        self.log("USER", query)
        self.reactor.set_state("THINKING", THEME["arc_blue"])

        def on_action(action_str):
            self.log("ACTION", action_str)
            self.reactor.set_state("EXECUTING", THEME["green"])

        # Process with Cloud Brain
        response_text = jarvis_brain.process_command(query, on_action_callback=on_action)

        # Spoken Response
        self.log(ASSISTANT_NAME, response_text)
        self.reactor.set_state("SPEAKING", THEME["green"])
        self.voice_btn.configure(text="SPEAKING...")

        jarvis_voice.speak(response_text)

        # Reset state
        self.reactor.set_state("STANDBY", THEME["cyan"])
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
                
                # Write to .env file
                env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
                try:
                    with open(env_path, "w", encoding="utf-8") as f:
                        f.write(f"GEMINI_API_KEY={new_key}\nGEMINI_MODEL=gemini-2.0-flash\nJARVIS_VOICE=en-GB-RyanNeural\n")
                except Exception:
                    pass

                self.cloud_badge.configure(text="● CLOUD BRAIN ONLINE", text_color=THEME["green"])
                self.log("SYSTEM", "Gemini Cloud API Key configured successfully!")
                dialog.destroy()

        save_btn = ctk.CTkButton(
            dialog, 
            text="SAVE & ACTIVATE BRAIN", 
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=THEME["cyan"],
            text_color="#000000",
            hover_color="#4DF0FF",
            height=38,
            command=save_key
        )
        save_btn.pack(pady=10)

if __name__ == "__main__":
    app = JarvisHUD()
    app.mainloop()
