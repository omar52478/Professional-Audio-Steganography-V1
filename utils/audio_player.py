# utils/audio_player.py
import simpleaudio as sa
import threading
import numpy as np
import os
import io

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False


current_playback = None

def play_audio(audio_path, progress_callback):
    global current_playback
    stop_audio()
    
    try:
        if not PYDUB_AVAILABLE:
            raise ImportError("pydub is required to play audio.")

        # --- FIX: Use pydub to load any audio format and get raw data ---
        ext = os.path.splitext(audio_path)[1].lower()
        if ext == '.wav':
            audio = AudioSegment.from_wav(audio_path)
        elif ext == '.mp3':
            audio = AudioSegment.from_mp3(audio_path)
        else:
            # Fallback for other potential formats if ffmpeg supports them
            audio = AudioSegment.from_file(audio_path)

        # Get raw audio data compatible with simpleaudio
        data = audio.raw_data
        samplerate = audio.frame_rate
        num_channels = audio.channels
        bytes_per_sample = audio.sample_width

        def player_thread():
            global current_playback
            progress_callback(f"▶️ Playing {os.path.basename(audio_path)}...")
            current_playback = sa.play_buffer(data, num_channels, bytes_per_sample, samplerate)
            current_playback.wait_done()
            progress_callback("⏹️ Playback finished.")
            current_playback = None

        threading.Thread(target=player_thread, daemon=True).start()

    except Exception as e:
        progress_callback(f"Error playing audio: {e}")

def stop_audio():
    global current_playback
    if current_playback and current_playback.is_playing():
        sa.stop_all()
        current_playback = None
        return True
    return False