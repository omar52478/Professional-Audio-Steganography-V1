# utils/preview_handler.py
import matplotlib
matplotlib.use('Agg')  # <<< THE MOST IMPORTANT FIX: Use a non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter as ctk
from PIL import Image, ImageTk
import os
import io
import numpy as np
from . import audio_player

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

plt.style.use('dark_background')

def create_waveform_preview(frame, audio_path, progress_callback):
    """Generates and embeds a waveform plot for audio files using a thread-safe method."""
    for widget in frame.winfo_children():
        widget.destroy()

    try:
        if not PYDUB_AVAILABLE:
            raise ImportError("pydub library is not installed.")

        # --- Read Audio Data using pydub for both WAV and MP3 ---
        ext = os.path.splitext(audio_path)[1].lower()
        if ext == '.wav':
            audio = AudioSegment.from_wav(audio_path)
        elif ext == '.mp3':
            audio = AudioSegment.from_mp3(audio_path)
        else:
            raise NotImplementedError(f"Preview for {ext} is not supported.")
        
        audio = audio.set_channels(1)
        data = np.array(audio.get_array_of_samples())

        # --- Create Matplotlib Figure (this part is now safe in a thread) ---
        fig, ax = plt.subplots(figsize=(4, 2), dpi=100)
        fig.patch.set_facecolor('#2B2B2B')
        ax.set_facecolor('#242424')
        ax.plot(data, color='#1F6AA5', linewidth=0.5)
        ax.set_title("Audio Waveform", color='white', fontsize=10)
        ax.tick_params(axis='x', colors='gray'); ax.tick_params(axis='y', colors='gray')
        plt.tight_layout()

        # --- Convert plot to an image ---
        buf = io.BytesIO()
        fig.savefig(buf, format='png', facecolor=fig.get_facecolor())
        buf.seek(0)
        img = Image.open(buf)
        plt.close(fig) # Close the figure to free memory

        # --- Display the image in the GUI ---
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
        image_label = ctk.CTkLabel(frame, image=ctk_img, text="")
        image_label.pack(fill="both", expand=True, padx=5, pady=5)

        # --- Play/Stop Controls ---
        control_frame = ctk.CTkFrame(frame, fg_color="transparent")
        control_frame.pack(pady=5)
        play_button = ctk.CTkButton(control_frame, text="Play ▶", command=lambda: audio_player.play_audio(audio_path, progress_callback))
        play_button.pack(side="left", padx=5)
        stop_button = ctk.CTkButton(control_frame, text="Stop ■", command=lambda: progress_callback("⏹️ Playback stopped.") if audio_player.stop_audio() else None)
        stop_button.pack(side="left", padx=5)

    except Exception as e:
        ctk.CTkLabel(frame, text=f"⚠️\nCould not plot waveform:\n{e}", text_color="gray").pack(expand=True)

# ... (The rest of the functions remain the same as the final version) ...
def create_image_preview(frame, file_path_or_data):
    for widget in frame.winfo_children():
        widget.destroy()
    try:
        img = Image.open(io.BytesIO(file_path_or_data) if isinstance(file_path_or_data, bytes) else file_path_or_data)
        img.thumbnail((350, 250))
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
        label = ctk.CTkLabel(frame, image=ctk_img, text="")
        label.pack(expand=True, padx=5, pady=5)
    except Exception as e:
        ctk.CTkLabel(frame, text=f"🖼️\nInvalid Image:\n{e}", text_color="gray").pack(expand=True)

def create_text_preview(frame, text_content, from_file=False, from_bytes=False):
    for widget in frame.winfo_children():
        widget.destroy()
    try:
        textbox = ctk.CTkTextbox(frame, state="normal", fg_color="transparent", wrap="word")
        textbox.pack(fill="both", expand=True, padx=5, pady=5)
        textbox.delete("1.0", "end")
        content = ""
        if from_file:
            with open(text_content, 'r', encoding='utf-8', errors='ignore') as f: content = f.read()
        elif from_bytes:
            content = text_content.decode('utf-8', errors='ignore')
        else:
            content = text_content
        textbox.insert("1.0", content)
        textbox.configure(state="disabled")
    except Exception as e:
        ctk.CTkLabel(frame, text=f"📝\nError reading text:\n{e}", text_color="gray").pack(expand=True)
        
def create_info_preview(frame, file_path=None, filename=None, data=None):
    for widget in frame.winfo_children():
        widget.destroy()
    try:
        name = os.path.basename(file_path) if file_path else filename
        size_kb = (os.path.getsize(file_path) if file_path else len(data)) / 1024
        info_text = f"ℹ️ File Info\n\nName: {name}\nSize: {size_kb:.2f} KB\n\n(No visual preview available)"
        ctk.CTkLabel(frame, text=info_text, text_color="gray").pack(expand=True)
    except Exception as e:
        ctk.CTkLabel(frame, text=f"ℹ️\nError reading file:\n{e}", text_color="gray").pack(expand=True)