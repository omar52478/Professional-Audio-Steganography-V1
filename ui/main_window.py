# ui/main_window.py
import customtkinter as ctk
from ui.tabs.hide_tab import HideTab
from ui.tabs.extract_tab import ExtractTab
from ui.styles import Theme

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ProStego | Cyber Security Suite")
        self.geometry("1080x850")
        self.minsize(950, 750)
        self.fonts = Theme.get_fonts()
        
        self.configure(fg_color=Theme.COLOR_BG)
        self._setup_layout()

    def _setup_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 1. Top Bar
        top_bar = ctk.CTkFrame(self, fg_color="transparent", height=60, corner_radius=0)
        top_bar.grid(row=0, column=0, sticky="ew", padx=25, pady=(20, 5))
        
        ctk.CTkLabel(top_bar, text="🔊 PROSTEGO", font=("Impact", 32), text_color=Theme.COLOR_ACCENT_MAIN).pack(side="left")
        ctk.CTkLabel(top_bar, text=" |  SECURE ENCRYPTION PROTOCOL", font=("Segoe UI", 12, "bold"), text_color="gray").pack(side="left", pady=(12, 0), padx=10)

        # 2. Content
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        self.tab_view = ctk.CTkTabview(self.main_frame, 
                                       fg_color=Theme.COLOR_CARD, 
                                       segmented_button_fg_color=Theme.COLOR_BG,
                                       segmented_button_selected_color=Theme.COLOR_ACCENT_MAIN,
                                       segmented_button_unselected_color=Theme.COLOR_SECONDARY,
                                       segmented_button_selected_hover_color=Theme.COLOR_ACCENT_MAIN,
                                       text_color="white",
                                       corner_radius=15)
                                       
        self.tab_view.pack(fill="both", expand=True)
        self.tab_view.add(" Hide Data ")
        self.tab_view.add(" Extract Data ")

        # 3. Bottom Console
        self.bottom_panel = ctk.CTkFrame(self, fg_color=Theme.COLOR_BG, height=160, corner_radius=0, border_width=1, border_color=Theme.COLOR_BORDER)
        self.bottom_panel.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
        self.bottom_panel.grid_columnconfigure(0, weight=1)
        
        self.progress_bar = ctk.CTkProgressBar(self.bottom_panel, mode='determinate', height=3, corner_radius=0, 
                                               progress_color=Theme.COLOR_SUCCESS, fg_color="#111")
        self.progress_bar.set(0)
        self.progress_bar.grid(row=0, column=0, sticky="ew")
        
        self.log_console = ctk.CTkTextbox(self.bottom_panel, height=140, state="disabled", 
                                          font=self.fonts["console"], 
                                          fg_color="transparent", 
                                          text_color=Theme.COLOR_LOG_TEXT)
        self.log_console.grid(row=1, column=0, padx=15, pady=5, sticky="nsew")

        # Init Tabs
        self.hide_tab = HideTab(self.tab_view.tab(" Hide Data "), self._log, self._update_progress)
        self.hide_tab.pack(fill="both", expand=True)
        
        self.extract_tab = ExtractTab(self.tab_view.tab(" Extract Data "), self._log, self._update_progress)
        self.extract_tab.pack(fill="both", expand=True)

    def _log(self, message):
        self.log_console.configure(state="normal")
        self.log_console.insert("end", f"[SYSTEM] >> {message}\n")
        self.log_console.see("end")
        self.log_console.configure(state="disabled")

    def _update_progress(self, message, value):
        self._log(message)
        self.progress_bar.set(value)
        self.update_idletasks()