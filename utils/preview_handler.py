# utils/preview_handler.py
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import customtkinter as ctk
from PIL import Image
import os
import io
import numpy as np
from .audio_player import controller as audio_ctrl
import pygame

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

# Style Constants
P_BG = "#0F0F0F"         # خلفية الرسمة
P_WAVE = "#00E5FF"       # لون الموجة
P_TEXT = "#888888"

def format_time(seconds):
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02}:{secs:02}"

# --- 1. AUDIO VISUALIZER (MOVING TIMELINE) ---
def create_waveform_preview(frame, audio_path, progress_callback):
    for widget in frame.winfo_children(): widget.destroy()
    
    if not PYDUB_AVAILABLE: 
        ctk.CTkLabel(frame, text="pydub missing").pack()
        return

    try:
        # Load & Analyze
        ext = os.path.splitext(audio_path)[1].lower()
        if ext == '.wav': audio = AudioSegment.from_wav(audio_path)
        elif ext == '.mp3': audio = AudioSegment.from_mp3(audio_path)
        else: audio = AudioSegment.from_file(audio_path)
        
        duration = len(audio) / 1000.0
        samples = np.array(audio.get_array_of_samples())
        
        # Optimization
        if audio.channels > 1: samples = samples[::2]
        if len(samples) > 8000: samples = samples[::len(samples)//8000]
        
        # Plotting (Neon Style)
        fig, ax = plt.subplots(figsize=(8, 3), dpi=80)
        fig.patch.set_facecolor(P_BG)
        ax.set_facecolor(P_BG)
        ax.plot(samples, color=P_WAVE, linewidth=0.6, alpha=0.9) # Neon Line
        ax.set_axis_off()
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        
        buf = io.BytesIO()
        fig.savefig(buf, format='png', facecolor=P_BG)
        buf.seek(0)
        img = Image.open(buf)
        plt.close(fig)
        
        # Display Image
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(380, 100))
        ctk.CTkLabel(frame, image=ctk_img, text="").pack(fill="x", pady=(5,0))
        
        # Controls (Timeline)
        ctrl = ctk.CTkFrame(frame, fg_color="transparent")
        ctrl.pack(fill="x", padx=10, pady=5)
        
        # Play Button
        btn_play = ctk.CTkButton(ctrl, text="▶", width=30, height=30, corner_radius=15,
                                 fg_color="#222", hover_color="#333", 
                                 border_width=1, border_color=P_WAVE, text_color=P_WAVE)
        btn_play.pack(side="left", padx=5)
        
        # Slider (The Moving Part)
        slider = ctk.CTkSlider(ctrl, from_=0, to=duration, number_of_steps=100, 
                               progress_color=P_WAVE, button_color="white", button_hover_color=P_WAVE, height=15)
        slider.pack(side="left", fill="x", expand=True, padx=10)
        slider.set(0)
        
        # Time Label
        lbl_time = ctk.CTkLabel(ctrl, text=f"00:00 / {format_time(duration)}", font=("Consolas", 10), text_color=P_TEXT)
        lbl_time.pack(side="right", padx=5)
        
        # --- Logic for Animation ---
        audio_ctrl.load(audio_path)
        
        def update_ui():
            if pygame.mixer.music.get_busy():
                # Animation Loop
                pos = audio_ctrl.get_pos()
                slider.set(pos)
                lbl_time.configure(text=f"{format_time(pos)} / {format_time(duration)}")
                frame.after(100, update_ui) # Repeat every 100ms
            elif not audio_ctrl.is_paused:
                # Reset when finished
                btn_play.configure(text="▶", fg_color="#222", text_color=P_WAVE)
                slider.set(0)

        def toggle():
            if audio_ctrl.is_paused or not pygame.mixer.music.get_busy():
                audio_ctrl.play()
                btn_play.configure(text="⏸", fg_color=P_WAVE, text_color="black")
                update_ui() # Start Animation
            else:
                audio_ctrl.pause()
                btn_play.configure(text="▶", fg_color="#222", text_color=P_WAVE)
        
        btn_play.configure(command=toggle)

    except Exception as e:
        ctk.CTkLabel(frame, text="Audio Error", text_color="gray").pack(expand=True)

# --- 2. IMAGE RENDERER (Centered High Quality) ---
def create_image_preview(frame, file_path_or_data):
    for widget in frame.winfo_children(): widget.destroy()
    try:
        if isinstance(file_path_or_data, str): pil_image = Image.open(file_path_or_data)
        else: pil_image = Image.open(io.BytesIO(file_path_or_data))

        # Smart Fit
        max_h = 160
        ratio = max_h / pil_image.size[1]
        new_w = int(pil_image.size[0] * ratio)
        
        if new_w > 380: new_w = 380
            
        # High Quality Scaling
        my_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(new_w, max_h))
        
        ctk.CTkLabel(frame, image=my_image, text="").pack(expand=True, pady=5)
        
        dims = f"{pil_image.size[0]}x{pil_image.size[1]} px"
        ctk.CTkLabel(frame, text=dims, font=("Consolas", 10), text_color="#555").pack(pady=0)

    except Exception:
        ctk.CTkLabel(frame, text="Image Error", text_color="gray").pack(expand=True)

# --- 3. TEXT & INFO ---
def create_text_preview(frame, text_content, from_file=False):
    for widget in frame.winfo_children(): widget.destroy()
    try:
        textbox = ctk.CTkTextbox(frame, fg_color="#080808", font=("Consolas", 11), 
                                 text_color="#00FF9D", border_width=0, corner_radius=5)
        textbox.pack(fill="both", expand=True, padx=5, pady=5)
        text = ""
        if from_file:
            with open(text_content, 'r', encoding='utf-8', errors='ignore') as f: text = f.read(1000)
        else: text = text_content[:1000]
        textbox.insert("1.0", text)
        textbox.configure(state="disabled")
    except Exception:
        ctk.CTkLabel(frame, text="Text Error").pack(expand=True)

def create_info_preview(frame, file_path=None, filename=None, data=None):
    for widget in frame.winfo_children(): widget.destroy()
    try:
        name = os.path.basename(file_path) if file_path else filename
        size = os.path.getsize(file_path) if file_path else len(data)
        ctk.CTkLabel(frame, text="📄 FILE DETECTED", font=("Segoe UI", 12, "bold"), text_color="#00E5FF").pack(pady=(40, 5))
        ctk.CTkLabel(frame, text=f"{name[:25]}...", font=("Segoe UI", 14), text_color="white").pack()
        ctk.CTkLabel(frame, text=f"{size/1024:.2f} KB", font=("Consolas", 12), text_color="gray").pack(pady=5)
    except Exception:
        ctk.CTkLabel(frame, text="Info Error").pack(expand=True)