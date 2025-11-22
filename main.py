# main.py
import customtkinter as ctk
import tempfile
import atexit
import shutil
from ui.main_window import MainWindow

# --- Temp file management ---
temp_dir = tempfile.mkdtemp()

def cleanup_temp_dir():
    try:
        shutil.rmtree(temp_dir)
    except Exception:
        pass

atexit.register(cleanup_temp_dir)

# --- Entry Point ---
if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    
    app = MainWindow()
    app.mainloop()