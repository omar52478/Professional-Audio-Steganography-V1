# ui/tabs/hide_tab.py
import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
from logic import hide_data
from ui.widgets import FileInputFrame
from utils import preview_handler
from ui.styles import Theme

INTERNAL_APP_KEY = "ProStegoInternalSecretKey#2024"

class HideTab(ctk.CTkFrame):
    def __init__(self, parent, log_callback, progress_callback):
        super().__init__(parent, fg_color="transparent")
        self.log = log_callback
        self.update_progress = progress_callback
        self.fonts = Theme.get_fonts()
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._setup_ui()

    def _setup_ui(self):
        # Left Column
        left_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", scrollbar_button_color=Theme.COLOR_ACCENT_MAIN)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.cover_audio_frame = FileInputFrame(left_frame, "1. Cover Audio (.wav)", [("WAV", "*.wav")], self.log)
        self.cover_audio_frame.pack(pady=10, fill="x")

        # Payload
        card_payload = ctk.CTkFrame(left_frame, fg_color=Theme.COLOR_CARD, corner_radius=15, border_width=1, border_color=Theme.COLOR_BORDER)
        card_payload.pack(pady=10, fill="x")
        
        ctk.CTkLabel(card_payload, text="2. Secret Payload", font=self.fonts["sub"], text_color=Theme.COLOR_ACCENT_MAIN).pack(pady=(15,5), padx=15, anchor="w")
        
        self.mode_var = ctk.StringVar(value="File")
        self.input_mode = ctk.CTkSegmentedButton(card_payload, values=["File", "Text"], variable=self.mode_var, command=self._switch_mode, 
                                                 font=self.fonts["button"], selected_color=Theme.COLOR_ACCENT_MAIN, unselected_color=Theme.COLOR_SECONDARY)
        self.input_mode.pack(pady=10, padx=15, fill="x")

        self.payload_container = ctk.CTkFrame(card_payload, fg_color="transparent")
        self.payload_container.pack(fill="x", padx=5, pady=(0, 15))
        
        self.secret_file_frame = FileInputFrame(self.payload_container, "Select File to Hide", [("All", "*.*")], self.log)
        self.secret_file_frame.pack(fill="x")
        
        self.secret_text_frame = ctk.CTkFrame(self.payload_container, fg_color="transparent")
        self.secret_text_box = ctk.CTkTextbox(self.secret_text_frame, height=150, corner_radius=10, fg_color=Theme.COLOR_INPUT, font=self.fonts["entry"])
        self.secret_text_box.pack(fill="x", padx=10)

        # Options
        card_opts = ctk.CTkFrame(left_frame, fg_color=Theme.COLOR_CARD, corner_radius=15, border_width=1, border_color=Theme.COLOR_BORDER)
        card_opts.pack(pady=10, fill="x")
        
        ctk.CTkLabel(card_opts, text="3. Options", font=self.fonts["sub"], text_color=Theme.COLOR_ACCENT_MAIN).pack(pady=(15,5), padx=15, anchor="w")
        
        self.encryption_var = ctk.StringVar(value="Standard")
        self.encryption_switch = ctk.CTkSwitch(card_opts, text="Secure Mode (AES-Encrypt)", variable=self.encryption_var, onvalue="AES", offvalue="Standard", 
                                               font=self.fonts["body"], progress_color=Theme.COLOR_ACCENT_GREEN)
        self.encryption_switch.pack(pady=5, padx=15, anchor="w")
        
        self.compress_check = ctk.CTkCheckBox(card_opts, text="Enable Compression (zlib)", font=self.fonts["body"], hover_color=Theme.COLOR_ACCENT_MAIN)
        self.compress_check.pack(pady=(0, 15), padx=15, anchor="w")
        self.compress_check.select()

        self.btn_hide = ctk.CTkButton(left_frame, text="🚀 START HIDING PROCESS", height=50, font=self.fonts["button"], 
                                      fg_color=Theme.COLOR_ACCENT_GREEN, text_color="black", hover_color="#00CC7D", corner_radius=15, command=self._start_hiding)
        self.btn_hide.pack(pady=20, fill="x")

        # Right Column
        right_frame = ctk.CTkFrame(self, fg_color=Theme.COLOR_CARD, corner_radius=15, border_width=1, border_color=Theme.COLOR_BORDER)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(right_frame, text="Live Payload Preview", font=self.fonts["sub"], text_color=Theme.COLOR_ACCENT_MAIN).pack(pady=15)
        
        self.hide_preview_area = ctk.CTkFrame(right_frame, fg_color="#000000", corner_radius=10)
        self.hide_preview_area.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        ctk.CTkLabel(self.hide_preview_area, text="Type or Select to Preview", text_color=Theme.COLOR_TEXT_DIM).pack(expand=True)
        
        # --- التصحيح هنا: استخدام create_text_preview ---
        self.secret_text_box.bind("<KeyRelease>", lambda e: preview_handler.create_text_preview(self.hide_preview_area, self.secret_text_box.get("1.0", "end-1c")))

    def _switch_mode(self, value):
        self.secret_file_frame.pack_forget(); self.secret_text_frame.pack_forget()
        if value == "File":
            self.secret_file_frame.pack(fill="x")
            path = self.secret_file_frame.get()
            if path: self.secret_file_frame.update_preview(path)
        else:
            self.secret_text_frame.pack(fill="x")
            preview_handler.create_text_preview(self.hide_preview_area, self.secret_text_box.get("1.0", "end-1c"))

    def _start_hiding(self):
        cover = self.cover_audio_frame.get()
        if not cover: return messagebox.showerror("Error", "Select cover audio!")
        
        if self.mode_var.get() == "File":
            path = self.secret_file_frame.get()
            if not path: return messagebox.showerror("Error", "Select secret file!")
            with open(path, 'rb') as f: secret = f.read()
            name = os.path.basename(path)
        else:
            secret = self.secret_text_box.get("1.0", "end-1c").encode('utf-8')
            if not secret: return messagebox.showerror("Error", "Enter secret text!")
            name = "message.txt"

        use_encryption = (self.encryption_var.get() == "AES")
        password = INTERNAL_APP_KEY if use_encryption else ""

        out = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV", "*.wav")])
        if out:
            threading.Thread(target=self._run_hide, args=(cover, secret, name, out, password, self.compress_check.get(), use_encryption), daemon=True).start()

    def _run_hide(self, cover, secret, name, out, password, compress, use_enc):
        try:
            self.btn_hide.configure(state="disabled")
            hide_data(cover, secret, name, out, password, compress, use_enc, self.update_progress)
            messagebox.showinfo("Success", "Data Hidden Successfully!")
        except Exception as e:
            self.log(f"ERROR: {e}")
            messagebox.showerror("Error", str(e))
        finally:
            self.btn_hide.configure(state="normal")