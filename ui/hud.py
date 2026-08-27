import os
import math
import time
import random
import threading
import datetime
import tkinter as tk
import customtkinter as ctk
from config import ASSISTANT_NAME, USER_NAME, GEMINI_API_KEY
from core.sys_info import get_system_diagnostics
from core.brain import jarvis_brain
from core.voice import jarvis_voice

# ====================================================================
# CINEMATIC LUMINESCENT MALE AI HOLOGRAM PALETTE
# ====================================================================
THEME = {
    "bg": "#02040A",               # Pitch Black Void
    "card_bg": "#060A14",          # Deep Glass Card
    "card_inner": "#03060D",       # Dark Inset
    "card_border": "#0E1C30",      # Blueprint Grid Border
    "cyan": "#00F0FF",             # Luminous Stark Cyan
    "cyan_glow": "#007799",        # Ambient Cyan Glow
    "core_white": "#FFFFFF",       # Luminous Core Light
    "arc_blue": "#0088FF",         # Quantum Blue
    "gold": "#FFAA00",             # Listening Gold
    "green": "#00FF88",            # Speaking Green
    "purple": "#B026FF",           # Neural Plasma Violet
    "text_main": "#E6EDF3",        # White Text
    "text_dim": "#717D96",         # Muted Tech Slate
    "font_tech": "Consolas",
    "font_main": "Segoe UI"
}

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MaleLuminescentHologramFace(tk.Canvas):
    """
    Luminescent Chiseled Male AI Hologram Phantom Face (JARVIS):
    - Strong masculine chiseled jawline & angular chin geometry
    - Bold, determined masculine cyber brows and piercing concentric glowing eyes
    - Smooth 2D micro-saccade eye tracking & natural eyelid blinking
    - Sharp masculine nose bridge and articulating masculine lips with live voice sync
    - Ethereal floating energy embers, blueprint HUD framing, and holographic scanlines
    """
    def __init__(self, master, size=260, **kwargs):
        super().__init__(
            master, 
            width=size, 
            height=size, 
            bg="#000206", 
            highlightthickness=0, 
            **kwargs
        )
        self.size = size
        self.cx = size // 2
        self.cy = size // 2
        
        # State
        self.state_color = THEME["cyan"]
        self.glow_color = THEME["cyan_glow"]
        self.status_text = "ONLINE"
        self.is_speaking = False
        self.is_listening = False
        self.is_thinking = False
        
        # Eye Gaze Tracking
        self.look_x = 0.0
        self.look_y = 0.0
        self.target_look_x = 0.0
        self.target_look_y = 0.0
        self.last_gaze_shift = time.time()
        
        # Blinking Physics
        self.blink_val = 1.0           # 1.0 = open, 0.0 = closed
        self.is_blinking = False
        self.last_blink = time.time()
        
        # Articulating Mouth
        self.mouth_open = 0.0          # 0.0 to 1.0
        self.mouth_freqs = [0.1] * 10
        
        # Floating Plasma Particles
        self.particles = [
            {
                "x": random.randint(25, size - 25),
                "y": random.randint(35, size - 35),
                "vx": random.uniform(-0.35, 0.35),
                "vy": -random.uniform(0.5, 1.2),
                "sz": random.uniform(1.2, 2.4)
            }
            for _ in range(22)
        ]
        
        # Head Breathing / Micro-float
        self.scanline_y = 0.0
        self.glitch_timer = time.time()
        
        self._running = True
        self.after(30, self._animate)

    def set_state(self, status: str, color: str = THEME["cyan"]):
        self.status_text = status
        self.state_color = color
        self.is_speaking = (status == "SPEAKING")
        self.is_listening = (status == "LISTENING" or status == "WAKING UP")
        self.is_thinking = (status == "THINKING" or status == "EXECUTING")
        
        if color == THEME["gold"]:
            self.glow_color = "#996600"
        elif color == THEME["green"]:
            self.glow_color = "#006633"
        elif color == THEME["arc_blue"]:
            self.glow_color = "#004499"
        else:
            self.glow_color = THEME["cyan_glow"]

    def _animate(self):
        if not self._running:
            return
            
        self.delete("all")
        cx, cy = self.cx, self.cy
        now = time.time()
        
        # 1. Subtle Head Breathing
        breathe = math.sin(now * 2.0) * 1.5
        cy_dyn = cy + breathe
        
        # 2. Gaze Shift Engine (Masculine Focused Saccades)
        if now - self.last_gaze_shift > random.uniform(2.5, 4.5):
            if self.is_thinking:
                self.target_look_x = random.choice([-0.65, 0.65])
                self.target_look_y = -0.3
            elif self.is_listening:
                self.target_look_x = 0.0
                self.target_look_y = 0.1
            else:
                self.target_look_x = random.uniform(-0.35, 0.35)
                self.target_look_y = random.uniform(-0.2, 0.2)
            self.last_gaze_shift = now
            
        self.look_x += (self.target_look_x - self.look_x) * 0.18
        self.look_y += (self.target_look_y - self.look_y) * 0.18

        # 3. Smooth Natural Blink
        if not self.is_blinking and now - self.last_blink > random.uniform(3.5, 6.0):
            self.is_blinking = True
            self.last_blink = now

        if self.is_blinking:
            self.blink_val -= 0.32
            if self.blink_val <= 0.0:
                self.blink_val = 0.0
                self.is_blinking = False
        else:
            if self.blink_val < 1.0:
                self.blink_val += 0.28
                if self.blink_val > 1.0:
                    self.blink_val = 1.0

        # 4. Blueprint Calibration HUD Framing
        pad = 8
        self.create_rectangle(pad, pad, self.size - pad, self.size - pad, outline="#0B1828", width=1)
        for i in range(1, 8):
            tx = pad + (self.size - 2 * pad) * (i / 8)
            self.create_line(tx, pad, tx, pad + 4, fill="#12253E", width=1)
            self.create_line(tx, self.size - pad - 4, tx, self.size - pad, fill="#12253E", width=1)
            ty = pad + (self.size - 2 * pad) * (i / 8)
            self.create_line(pad, ty, pad + 4, ty, fill="#12253E", width=1)
            self.create_line(self.size - pad - 4, ty, self.size - pad, ty, fill="#12253E", width=1)

        # 5. Floating Plasma Flame Embers
        for p in self.particles:
            p["y"] += p["vy"]
            p["x"] += p["vx"]
            if p["y"] < 20:
                p["y"] = self.size - 25
                p["x"] = cx + random.uniform(-65, 65)
            self.create_oval(
                p["x"], p["y"], p["x"] + p["sz"], p["y"] + p["sz"],
                fill=self.state_color, outline=""
            )

        # 6. Chiseled Masculine Jawline, Cheekbones & Chin (Strong Angular Contour)
        # Left Angular Jaw to Square Chin
        male_jaw = [
            (cx - 78, cy_dyn - 32),            # Left Temple
            (cx - 75, cy_dyn + 20),            # Cheekbone Outer
            (cx - 56, cy_dyn + 66),            # Sharp Gonial Jaw Angle
            (cx - 22, cy_dyn + 96),            # Left Square Chin Corner
            (cx + 22, cy_dyn + 96),            # Right Square Chin Corner
            (cx + 56, cy_dyn + 66),            # Right Gonial Jaw Angle
            (cx + 75, cy_dyn + 20),            # Right Cheekbone Outer
            (cx + 78, cy_dyn - 32),            # Right Temple
        ]
        
        # Multi-layer neon bloom for masculine jawline
        self.create_line(male_jaw, fill=self.glow_color, width=6, smooth=False)
        self.create_line(male_jaw, fill=self.state_color, width=2.5, smooth=False)
        self.create_line(male_jaw, fill=THEME["core_white"], width=1, smooth=False)

        # Masculine Cheekbone Contour Plates
        self.create_line(cx - 68, cy_dyn + 10, cx - 35, cy_dyn + 32, fill=self.glow_color, width=2)
        self.create_line(cx + 68, cy_dyn + 10, cx + 35, cy_dyn + 32, fill=self.glow_color, width=2)

        # Forehead Temple Cyber Circuit
        fh_y = cy_dyn - 68
        self.create_oval(cx - 4, fh_y - 4, cx + 4, fh_y + 4, fill=self.state_color, outline="#FFFFFF", width=1)
        self.create_line(cx - 28, fh_y, cx - 8, fh_y, fill=self.state_color, width=1.5)
        self.create_line(cx + 8, fh_y, cx + 28, fh_y, fill=self.state_color, width=1.5)

        # 7. Bold Masculine Brows & Piercing Eyes
        eye_y = cy_dyn - 16
        eye_spacing = 38
        eye_w = 23
        eye_h = 11.5 * max(0.04, self.blink_val)

        for side in [-1, 1]:
            ex = cx + (side * eye_spacing)
            
            # Bold Angular Masculine Eyebrow (Strong brow ridge)
            brow_y = eye_y - 12
            brow_pts = [
                (ex - side * (eye_w * 0.9), brow_y + 3),       # Inner brow head (low, focused)
                (ex, brow_y - 2),                             # Brow center arch
                (ex + side * (eye_w * 0.9), brow_y - 1),      # Brow arch point
                (ex + side * (eye_w * 1.4), brow_y - 9),      # Cyber tail flare
            ]
            
            self.create_line(brow_pts, fill=self.glow_color, width=6, smooth=False)
            self.create_line(brow_pts, fill=self.state_color, width=3, smooth=False)
            self.create_line(brow_pts, fill=THEME["core_white"], width=1.5, smooth=False)

            # Masculine Angular Eye Contour
            if eye_h > 1.0:
                # Upper Eyelid Arc
                up_pts = [
                    (ex - side * (eye_w * 0.85), eye_y + 1),
                    (ex, eye_y - eye_h * 0.75),
                    (ex + side * (eye_w * 0.85), eye_y - 1)
                ]
                self.create_line(up_pts, fill=self.state_color, width=2.5, smooth=True)
                self.create_line(up_pts, fill=THEME["core_white"], width=1.2, smooth=True)

                # Lower Eyelid Arc
                low_pts = [
                    (ex - side * (eye_w * 0.85), eye_y + 1),
                    (ex, eye_y + eye_h * 0.75),
                    (ex + side * (eye_w * 0.85), eye_y - 1)
                ]
                self.create_line(low_pts, fill=self.glow_color, width=3, smooth=True)
                self.create_line(low_pts, fill=self.state_color, width=1.5, smooth=True)

                # Concentric High-Intensity Glowing Iris Rings
                iris_cx = ex + (self.look_x * 5.5)
                iris_cy = eye_y + (self.look_y * 3.0)
                
                # Outer Iris Glow Ring
                r1 = 6.8
                self.create_oval(
                    iris_cx - r1, iris_cy - r1 * max(0.2, self.blink_val),
                    iris_cx + r1, iris_cy + r1 * max(0.2, self.blink_val),
                    outline=self.state_color, width=2
                )
                
                # Inner Core Pupil
                r2 = 3.0
                self.create_oval(
                    iris_cx - r2, iris_cy - r2 * max(0.2, self.blink_val),
                    iris_cx + r2, iris_cy + r2 * max(0.2, self.blink_val),
                    fill=THEME["core_white"], outline=""
                )

        # 8. Chiseled Straight Masculine Nose Bridge & Tip
        nose_y = cy_dyn + 22
        # Straight dorsal bridge lines
        self.create_line(cx - 3, eye_y, cx - 4, nose_y - 2, fill="#12253E", width=1.5)
        self.create_line(cx + 3, eye_y, cx + 4, nose_y - 2, fill="#12253E", width=1.5)
        
        # Nostril Wings & Tip
        nose_pts = [
            (cx - 8, nose_y + 3),
            (cx - 3, nose_y + 5),
            (cx, nose_y + 2),
            (cx + 3, nose_y + 5),
            (cx + 8, nose_y + 3)
        ]
        self.create_line(nose_pts, fill=self.state_color, width=2, smooth=True)
        self.create_oval(cx - 2, nose_y + 1, cx + 2, nose_y + 3, fill=THEME["core_white"], outline="")

        # 9. Luminous Masculine Articulating Lips (Speaking Mouth)
        mouth_y = cy_dyn + 56
        mouth_w = 30
        
        # Mouth Opening Dynamic Calculation
        if self.is_speaking:
            target_open = random.uniform(0.4, 1.0)
        elif self.is_listening:
            target_open = random.uniform(0.12, 0.4)
        else:
            target_open = 0.04 + math.sin(now * 2.5) * 0.03

        self.mouth_open += (target_open - self.mouth_open) * 0.42
        open_h = self.mouth_open * 15.0

        # Masculine Upper Lip (Crisp, defined center peak)
        up_lip = [
            (cx - mouth_w, mouth_y),
            (cx - mouth_w * 0.4, mouth_y - 3),
            (cx, mouth_y - 1),
            (cx + mouth_w * 0.4, mouth_y - 3),
            (cx + mouth_w, mouth_y)
        ]
        self.create_line(up_lip, fill=self.glow_color, width=6, smooth=True)
        self.create_line(up_lip, fill=self.state_color, width=2.5, smooth=True)
        self.create_line(up_lip, fill=THEME["core_white"], width=1, smooth=True)

        # Masculine Lower Lip
        low_lip = [
            (cx - mouth_w, mouth_y),
            (cx - mouth_w * 0.35, mouth_y + 5 + open_h),
            (cx, mouth_y + 7 + open_h),
            (cx + mouth_w * 0.35, mouth_y + 5 + open_h),
            (cx + mouth_w, mouth_y)
        ]
        self.create_line(low_lip, fill=self.glow_color, width=7, smooth=True)
        self.create_line(low_lip, fill=self.state_color, width=2.8, smooth=True)
        self.create_line(low_lip, fill=THEME["core_white"], width=1, smooth=True)

        # Inner Acoustic Speech Equalizer Bars (inside mouth opening)
        if open_h > 2.5:
            num_bars = len(self.mouth_freqs)
            bar_spacing = (mouth_w * 1.4) / num_bars
            start_bx = cx - (mouth_w * 0.7)
            
            for i in range(num_bars):
                if self.is_speaking:
                    target_f = random.uniform(0.3, 1.0)
                else:
                    target_f = 0.1
                self.mouth_freqs[i] += (target_f - self.mouth_freqs[i]) * 0.5
                bh = self.mouth_freqs[i] * open_h * 0.8
                bx = start_bx + i * bar_spacing
                self.create_line(bx, mouth_y + 2 - bh / 2, bx, mouth_y + 2 + bh / 2, fill=THEME["core_white"], width=1.5)

        # 10. Horizontal Laser Scanline
        self.scanline_y = (self.scanline_y + 3.0) % self.size
        self.create_line(
            pad, self.scanline_y, self.size - pad, self.scanline_y,
            fill=self.state_color, width=1, dash=(4, 8)
        )

        # 11. Holographic Status Badge
        self.create_text(
            cx, self.size - 14, 
            text=f"● JARVIS MALE AI: {self.status_text} ●", 
            fill=self.state_color, 
            font=(THEME["font_tech"], 10, "bold")
        )

        self.after(30, self._animate)

    def stop(self):
        self._running = False


class JarvisHUD(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Futuristic Cyber Window Setup
        self.title("J.A.R.V.I.S. // STARK INDUSTRIES MARK VII - MALE AI HOLOGRAM")
        self.geometry("1040x740")
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
            text="MALE CYBER HOLOGRAM AVATAR · STARK MARK VII", 
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
        """Two-Column Cyber Layout: Left (Male Hologram Face + Gauges), Right (Log + Shortcuts)"""
        grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True, padx=16, pady=4)

        # -------------------------------------------------------------
        # LEFT COLUMN (Male Moveable Face + Hardware Telemetry)
        # -------------------------------------------------------------
        left_col = ctk.CTkFrame(grid_frame, width=350, fg_color="transparent")
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
            text="MALE NEURAL SYNAPSE HOLOGRAM", 
            font=ctk.CTkFont(family=THEME["font_tech"], size=10, weight="bold"),
            text_color=THEME["text_dim"]
        )
        core_lbl.pack(pady=(10, 0))

        # Male Luminescent Cyber Face Canvas
        self.ai_face = MaleLuminescentHologramFace(face_card, size=250)
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
        self.log("SYSTEM", "J.A.R.V.I.S. Male Cyber AI Core Online. Background Wake Word Active.")
        self.log("MOBILE", f"📱 Mobile Phone Link: http://{local_ip}:5000 (Open in phone browser)", THEME["cyan"])
        if not jarvis_brain.is_configured():
            self.log("ALERT", "Gemini API Key is not set. Click ⚙️ in the bottom right to paste your free Gemini API key.", THEME["gold"])
        else:
            self.log("SYSTEM", "All systems nominal, sir. Chiseled Male Hologram Online. Say 'Hey Jarvis' or click Activate.")

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
