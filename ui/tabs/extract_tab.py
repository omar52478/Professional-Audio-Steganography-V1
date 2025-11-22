# ui/tabs/extract_tab.py
import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
import tempfile
from logic import extract_data
from ui.widgets import FileInputFrame
from utils import preview_handler
from ui.styles import Theme

INTERNAL_APP_KEY = "ProStegoInternalSecretKey#2024"

class ExtractTab(ctk.CTkFrame):
    def __init__(self, parent, log_callback, progress_callback):
        super().__init__(parent, fg_color="transparent")
        self.log = log_callback
        self.update_progress = progress_callback
        self.fonts = Theme.get_fonts()
        self.extracted_data = None
        self.extracted_filename = None
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._setup_ui()

    def _setup_ui(self):
        # Left Column
        left_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", scrollbar_button_color=Theme.COLOR_ACCENT_MAIN)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.stego_file_frame = FileInputFrame(left_frame, "1. Stego Audio File", [("WAV", "*.wav")], self.log)
        self.stego_file_frame.pack(pady=10, fill="x")

        self.btn_extract = ctk.CTkButton(left_frame, text="🔓 EXTRACT DATA", height=50, font=self.fonts["button"], 
                                         fg_color=Theme.COLOR_ACCENT_MAIN, text_color="white", corner_radius=15, command=self._start_extracting)
        self.btn_extract.pack(pady=20, fill="x")

        # Right Column
        right_frame = ctk.CTkFrame(self, fg_color=Theme.COLOR_CARD, corner_radius=15, border_width=1, border_color=Theme.COLOR_BORDER)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(right_frame, text="Extracted Content", font=self.fonts["sub"], text_color=Theme.COLOR_ACCENT_MAIN).pack(pady=15)
        
        self.extract_preview_area = ctk.CTkFrame(right_frame, fg_color="#000000", corner_radius=10)
        self.extract_preview_area.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        ctk.CTkLabel(self.extract_preview_area, text="Waiting for extraction...", text_color="gray").pack(expand=True)

        self.btn_save = ctk.CTkButton(self, text="💾 SAVE TO DISK", state="disabled", height=45, font=self.fonts["button"], fg_color=Theme.COLOR_SUCCESS, command=self._save_file, text_color="black")
        self.btn_save.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

    def _start_extracting(self):
        stego = self.stego_file_frame.get()
        if not stego: return messagebox.showerror("Error", "Select stego file!")
        self.btn_save.configure(state="disabled")
        
        threading.Thread(target=self._run_extract, args=(stego, INTERNAL_APP_KEY), daemon=True).start()

    def _run_extract(self, stego, password):
        try:
            self.btn_extract.configure(state="disabled")
            self.extracted_data, self.extracted_filename = extract_data(stego, password, self.update_progress)
            self._update_extract_view()
            messagebox.showinfo("Success", "Extraction Complete!")
        except ValueError as e:
            msg = str(e)
            if "Authentication failed" in msg:
                self.log(f"❌ Security Error: {msg}")
                messagebox.showerror("Tamper Detected", "❌ Data corrupted or tampered with!")
            else:
                self.log(f"❌ Error: {msg}")
                messagebox.showerror("Error", msg)
        except Exception as e:
            self.log(f"❌ System Error: {e}")
            messagebox.showerror("System Error", str(e))
        finally:
            self.btn_extract.configure(state="normal")

    def _update_extract_view(self):
        for w in self.extract_preview_area.winfo_children(): w.destroy()
        
        ext = os.path.splitext(self.extracted_filename)[1].lower()
        
        # --- التصحيح هنا: استخدام create_... بدلاً من render_... ---
        if ext in ['.wav', '.mp3']:
            temp_path = os.path.join(tempfile.gettempdir(), self.extracted_filename)
            with open(temp_path, 'wb') as f: f.write(self.extracted_data)
            preview_handler.create_waveform_preview(self.extract_preview_area, temp_path, self.log)
        elif ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
            preview_handler.create_image_preview(self.extract_preview_area, self.extracted_data)
        elif ext in ['.txt', '.md', '.py', '.json']:
            preview_handler.create_text_preview(self.extract_preview_area, self.extracted_data, from_bytes=True)
        else:
            preview_handler.create_info_preview(self.extract_preview_area, filename=self.extracted_filename, data=self.extracted_data)
        
        self.btn_save.configure(state="normal")

    def _save_file(self):
        path = filedialog.asksaveasfilename(initialfile=self.extracted_filename)
        if path:
            with open(path, 'wb') as f: f.write(self.extracted_data)
            self.log(f"Saved to: {path}")