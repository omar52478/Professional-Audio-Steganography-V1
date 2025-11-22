# ui/widgets.py
import customtkinter as ctk
from tkinter import filedialog
import os
from utils import preview_handler
from .styles import Theme

class FileInputFrame(ctk.CTkFrame):
    def __init__(self, master, label_text, file_types=None, progress_callback=None):
        super().__init__(master, fg_color=Theme.COLOR_CARD, corner_radius=15, 
                         border_width=1, border_color=Theme.COLOR_BORDER)
        self.fonts = Theme.get_fonts()
        self.file_types = file_types
        self.progress_callback = progress_callback
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(10,5))
        ctk.CTkLabel(header, text="●", font=("Arial", 12), text_color=Theme.COLOR_ACCENT_MAIN).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(header, text=label_text, font=self.fonts["sub"], text_color="white").pack(side="left")
        
        # Input
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        self.entry = ctk.CTkEntry(input_frame, placeholder_text="Select file...", font=self.fonts["mono"], 
                                  corner_radius=8, border_width=1, border_color=Theme.COLOR_BORDER, 
                                  fg_color="#0A0A0A", height=38, text_color="#CCCCCC")
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(input_frame, text="📂 BROWSE", width=100, height=38, command=self.browse_file, 
                      font=self.fonts["button"], corner_radius=8, 
                      fg_color="#222222", hover_color="#333333",
                      border_width=1, border_color=Theme.COLOR_ACCENT_MAIN, text_color=Theme.COLOR_ACCENT_MAIN).pack(side="right")

        # Preview Area
        self.preview_frame = ctk.CTkFrame(self, height=200, corner_radius=8, fg_color="#000000", border_width=1, border_color="#151515")
        self.preview_frame.pack(pady=(0, 15), padx=15, fill="both", expand=True)
        self.preview_frame.pack_propagate(False)
        
        self.placeholder = ctk.CTkLabel(self.preview_frame, text="[ NO SIGNAL ]", font=("Consolas", 12), text_color=Theme.COLOR_TEXT_DIM)
        self.placeholder.place(relx=0.5, rely=0.5, anchor="center")
    
    def get(self): return self.entry.get()

    def browse_file(self):
        path = filedialog.askopenfilename(filetypes=self.file_types if self.file_types else [])
        if path:
            self.entry.delete(0, 'end')
            self.entry.insert(0, path)
            self.update_preview(path)
    
    def update_preview(self, path):
        if not path or not os.path.exists(path): return
        try: self.placeholder.place_forget()
        except: pass
        
        for widget in self.preview_frame.winfo_children(): 
            try: widget.destroy()
            except: pass

        ext = os.path.splitext(path)[1].lower()
        
        # --- التصحيح هنا: استخدام الأسماء create_... بدلاً من render_... ---
        if ext in ['.wav', '.mp3']:
            preview_handler.create_waveform_preview(self.preview_frame, path, self.progress_callback)
        elif ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
            preview_handler.create_image_preview(self.preview_frame, path)
        elif ext in ['.txt', '.py', '.md', '.json']:
            preview_handler.create_text_preview(self.preview_frame, path, from_file=True)
        else:
            preview_handler.create_info_preview(self.preview_frame, file_path=path)