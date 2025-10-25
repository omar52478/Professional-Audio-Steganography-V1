# main.py
import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
import tempfile
import atexit
from logic import hide_data, extract_data
from utils import preview_handler
from ui.widgets import FileInputFrame

# --- Temp file management ---
temp_dir = tempfile.mkdtemp()
def cleanup_temp_dir():
    import shutil
    shutil.rmtree(temp_dir)
atexit.register(cleanup_temp_dir)

# --- THEME & STYLE DEFINITIONS ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue") # Using the 'blue' theme as a base

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🔊 Professional Audio Steganography Suite")
        self.geometry("1100x850")
        self.minsize(900, 700)

        # --- Style & Font Definitions ---
        self.title_font = ctk.CTkFont(family="Arial", size=26, weight="bold")
        self.label_font = ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        self.button_font = ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        self.log_font = ctk.CTkFont(family="Consolas", size=12)

        # Class variables for extracted data
        self.extracted_data = None
        self.extracted_filename = None

        # --- Main Layout ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Audio Steganography Suite", font=self.title_font).grid(row=0, column=0, padx=20, pady=20)

        self.main_frame = ctk.CTkFrame(self, fg_color="#1D1D1D", corner_radius=10) # A slightly different bg color
        self.main_frame.grid(row=1, column=0, padx=20, pady=0, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1); self.main_frame.grid_rowconfigure(0, weight=1)

        self.tab_view = ctk.CTkTabview(self.main_frame, corner_radius=8)
        self.tab_view.pack(padx=15, pady=15, fill="both", expand=True)
        self.tab_view.add("🔐 Hide Data"); self.tab_view.add("🔓 Extract Data")
        
        self._create_hide_tab()
        self._create_extract_tab()
        
        # --- Bottom Bar ---
        self.log_console = ctk.CTkTextbox(self, height=90, state="disabled", font=self.log_font, corner_radius=8)
        self.log_console.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.progress_bar = ctk.CTkProgressBar(self, mode='determinate', height=8, corner_radius=8)
        self.progress_bar.set(0); self.progress_bar.grid(row=3, column=0, padx=20, pady=(0,15), sticky="ew")

    def _log(self, message):
        self.log_console.configure(state="normal")
        self.log_console.insert("end", f"> {message}\n"); self.log_console.see("end")
        self.log_console.configure(state="disabled")

    def _update_progress(self, message, value):
        self._log(message); self.progress_bar.set(value); self.update_idletasks()
    
    # ======================== HIDE TAB ========================
    def _create_hide_tab(self):
        tab = self.tab_view.tab("🔐 Hide Data")
        tab.grid_columnconfigure(0, weight=1); tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        input_scroll_frame = ctk.CTkScrollableFrame(tab, label_text="Inputs & Options", label_font=self.label_font)
        input_scroll_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.cover_audio_frame = FileInputFrame(input_scroll_frame, "1. Cover Audio (.wav)", [("WAV files", "*.wav")], self._log)
        self.cover_audio_frame.pack(padx=10, pady=10, fill="x")

        ctk.CTkLabel(input_scroll_frame, text="2. Secret Data", font=self.label_font).pack(pady=(10,0), padx=20, anchor="w")
        self.input_mode_selector = ctk.CTkSegmentedButton(input_scroll_frame, values=["File", "Text"], command=self._switch_input_mode, font=self.button_font)
        self.input_mode_selector.pack(pady=5, padx=10, fill="x"); self.input_mode_selector.set("File")

        self.input_container = ctk.CTkFrame(input_scroll_frame, fg_color="transparent")
        self.input_container.pack(fill="x", expand=True, padx=0, pady=0)

        self.secret_file_frame = FileInputFrame(self.input_container, "", [("All files", "*.*")], self._log)
        self.secret_file_frame.pack(fill="x", expand=True)
        
        self.secret_text_frame = ctk.CTkFrame(self.input_container, fg_color="transparent")
        self.secret_text_box = ctk.CTkTextbox(self.secret_text_frame, height=280, corner_radius=8)
        self.secret_text_box.pack(pady=5, padx=10, fill="both", expand=True)
        
        options_frame = ctk.CTkFrame(input_scroll_frame)
        options_frame.pack(pady=20, padx=10, fill="x")
        ctk.CTkLabel(options_frame, text="3. Options & Action", font=self.label_font).pack(pady=5, padx=10, anchor="w")
        self.password_entry_hide = ctk.CTkEntry(options_frame, placeholder_text="Password (optional)", show="*", corner_radius=8)
        self.password_entry_hide.pack(pady=5, padx=10, fill="x")
        self.compress_check = ctk.CTkCheckBox(options_frame, text="Compress data"); self.compress_check.select()
        self.compress_check.pack(pady=5, padx=10, anchor="w")
        self.hide_button = ctk.CTkButton(options_frame, text="Start Hiding", height=45, command=self._start_hiding_thread, font=self.button_font, corner_radius=8)
        self.hide_button.pack(pady=20, padx=10, fill="x")

        self.hide_preview_scroll_frame = ctk.CTkScrollableFrame(tab, label_text="Secret Data Preview", label_font=self.label_font)
        self.hide_preview_scroll_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(self.hide_preview_scroll_frame, text="Preview of secret data will appear here", text_color="gray").pack(expand=True)
        self.secret_text_box.bind("<KeyRelease>", self._update_hide_preview_from_text)
        self._switch_input_mode("File") # Set initial state

    def _switch_input_mode(self, value):
        self.secret_file_frame.pack_forget(); self.secret_text_frame.pack_forget()
        if value == "File":
            self.secret_file_frame.pack(fill="x", expand=True)
            path = self.secret_file_frame.get()
            if path: self.secret_file_frame.update_preview(path)
        else:
            self.secret_text_frame.pack(fill="x", expand=True)
            self._update_hide_preview_from_text()

    def _update_hide_preview_from_text(self, event=None):
        text = self.secret_text_box.get("1.0", "end-1c")
        preview_handler.create_text_preview(self.hide_preview_scroll_frame, text)

    # ======================== EXTRACT TAB ========================
    def _create_extract_tab(self):
        tab = self.tab_view.tab("🔓 Extract Data")
        tab.grid_columnconfigure(0, weight=1); tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        input_scroll_frame = ctk.CTkScrollableFrame(tab, label_text="Inputs & Options", label_font=self.label_font)
        input_scroll_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.stego_audio_frame = FileInputFrame(input_scroll_frame, "1. Stego Audio (.wav)", [("WAV files", "*.wav")], self._log)
        self.stego_audio_frame.pack(padx=10, pady=10, fill="x")
        
        options_frame = ctk.CTkFrame(input_scroll_frame)
        options_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(options_frame, text="2. Options & Action", font=self.label_font).pack(pady=5, padx=10, anchor="w")
        self.password_entry_extract = ctk.CTkEntry(options_frame, placeholder_text="Password (if required)", show="*", corner_radius=8)
        self.password_entry_extract.pack(pady=5, padx=10, fill="x")
        self.extract_button = ctk.CTkButton(options_frame, text="🔍 Extract & Preview", height=45, command=self._start_extracting_thread, font=self.button_font, corner_radius=8)
        self.extract_button.pack(pady=20, padx=10, fill="x")
        
        self.extract_preview_scroll_frame = ctk.CTkScrollableFrame(tab, label_text="Extracted Data Preview", label_font=self.label_font)
        self.extract_preview_scroll_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(self.extract_preview_scroll_frame, text="Extracted data will be shown here", text_color="gray").pack(expand=True)
        
        self.save_button = ctk.CTkButton(tab, text="💾 Save to Disk", state="disabled", height=45, command=self._save_extracted_file, font=self.button_font, corner_radius=8)
        self.save_button.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

    # --- (Rest of the functions: _start_hiding_thread, _run_hide, etc. remain the same) ---
    def _start_hiding_thread(self):
        cover = self.cover_audio_frame.get()
        if not cover: messagebox.showerror("Error", "Please select a cover audio file."); return
        mode = self.input_mode_selector.get()
        if mode == "File":
            secret_path = self.secret_file_frame.get()
            if not secret_path: messagebox.showerror("Error", "Please select a secret file."); return
            with open(secret_path, 'rb') as f: secret_data = f.read()
            secret_filename = os.path.basename(secret_path)
        else: # Text
            secret_data = self.secret_text_box.get("1.0", "end-1c").encode('utf-8')
            if not secret_data: messagebox.showerror("Error", "Please enter text to hide."); return
            secret_filename = "message.txt"
        password = self.password_entry_hide.get(); compress = self.compress_check.get()
        output = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
        if not output: return
        threading.Thread(target=self._run_hide, args=(cover, secret_data, secret_filename, output, password, compress), daemon=True).start()

    def _run_hide(self, cover, secret_data, filename, output, password, compress):
        try:
            self.hide_button.configure(state="disabled")
            hide_data(cover, secret_data, filename, output, password, compress, self._update_progress)
            messagebox.showinfo("Success", f"Data hidden successfully in\n{output}")
        except Exception as e: self._log(f"ERROR: {e}"); messagebox.showerror("Error", str(e))
        finally: self.hide_button.configure(state="normal")
            
    def _start_extracting_thread(self):
        stego = self.stego_audio_frame.get()
        if not stego: messagebox.showerror("Error", "Please select a stego file."); return
        password = self.password_entry_extract.get()
        self.save_button.configure(state="disabled"); self.extracted_data = None
        threading.Thread(target=self._run_extract, args=(stego, password), daemon=True).start()

    def _run_extract(self, stego, password):
        try:
            self.extract_button.configure(state="disabled")
            self.extracted_data, self.extracted_filename = extract_data(stego, password, self._update_progress)
            self._update_extract_preview()
            messagebox.showinfo("Success", "Data extracted! Preview is now available.")
        except Exception as e: self._log(f"ERROR: {e}"); messagebox.showerror("Error", str(e))
        finally: self.extract_button.configure(state="normal")

    def _update_extract_preview(self):
        for widget in self.extract_preview_scroll_frame.winfo_children(): widget.destroy()
        if not self.extracted_data: return
        
        ext = os.path.splitext(self.extracted_filename)[1].lower()
        if ext in ['.wav', '.mp3']:
            temp_path = os.path.join(temp_dir, self.extracted_filename)
            with open(temp_path, 'wb') as temp_file:
                temp_file.write(self.extracted_data)
            preview_handler.create_waveform_preview(self.extract_preview_scroll_frame, temp_path, self._log)
        elif ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
            preview_handler.create_image_preview(self.extract_preview_scroll_frame, self.extracted_data)
        elif ext in ['.txt', '.py', '.md', '.json']:
            preview_handler.create_text_preview(self.extract_preview_scroll_frame, self.extracted_data, from_bytes=True)
        else:
            preview_handler.create_info_preview(self.extract_preview_scroll_frame, filename=self.extracted_filename, data=self.extracted_data)
        
        self.save_button.configure(state="normal")

    def _save_extracted_file(self):
        if not self.extracted_data: messagebox.showwarning("Warning", "No data to save."); return
        path = filedialog.asksaveasfilename(initialfile=self.extracted_filename)
        if path:
            try:
                with open(path, 'wb') as f: f.write(self.extracted_data)
                self._log(f"File saved to {path}"); messagebox.showinfo("Success", "File saved successfully!")
            except Exception as e: messagebox.showerror("Error", f"Could not save file: {e}")

if __name__ == "__main__":
    app = App()
    app.mainloop()