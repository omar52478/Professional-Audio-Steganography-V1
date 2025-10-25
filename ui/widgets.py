# ui/widgets.py
import customtkinter as ctk
from tkinter import filedialog
import os
from utils import preview_handler

class FileInputFrame(ctk.CTkFrame):
    def __init__(self, master, label_text, file_types=None, progress_callback=None):
        super().__init__(master, fg_color="transparent")
        
        self.file_types = file_types
        self.progress_callback = progress_callback
        
        ctk.CTkLabel(self, text=label_text, font=("Arial", 14, "bold")).pack(pady=(5,0), padx=10, anchor="w")
        self.entry = ctk.CTkEntry(self, placeholder_text="No file selected...")
        self.entry.pack(pady=5, padx=10, fill="x")
        ctk.CTkButton(self, text="📁 Browse...", command=self.browse_file).pack(pady=(0,10), padx=10, anchor="w")

        self.preview_frame = ctk.CTkFrame(self, height=200)
        self.preview_frame.pack(pady=5, padx=10, fill="both", expand=True)
        ctk.CTkLabel(self.preview_frame, text="Preview will be shown here", text_color="gray").pack(expand=True)
    
    def get(self):
        return self.entry.get()

    def browse_file(self):
        path = filedialog.askopenfilename(filetypes=self.file_types if self.file_types else [])
        if path:
            self.entry.delete(0, 'end')
            self.entry.insert(0, path)
            self.update_preview(path)
    
    def update_preview(self, path):
        if not path or not os.path.exists(path): return

        ext = path.split('.')[-1].lower()
        # --- THE FIX IS HERE ---
        if ext in ['wav', 'mp3']:
            preview_handler.create_waveform_preview(self.preview_frame, path, self.progress_callback)
        elif ext in ['png', 'jpg', 'jpeg', 'gif', 'bmp']:
            preview_handler.create_image_preview(self.preview_frame, path)
        elif ext in ['txt', 'py', 'md', 'json']:
            preview_handler.create_text_preview(self.preview_frame, path, from_file=True)
        else:
            preview_handler.create_info_preview(self.preview_frame, file_path=path)