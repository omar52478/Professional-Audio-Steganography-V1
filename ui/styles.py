# ui/styles.py
import customtkinter as ctk

class Theme:
    # --- Midnight Neon Palette ---
    COLOR_BG = "#050505"            # أسود حالك
    COLOR_CARD = "#101010"          # رمادي داكن جداً للكروت
    COLOR_CARD_HOVER = "#1A1A1A"    # لون أفتح قليلاً عند التفاعل
    COLOR_BORDER = "#333333"        # لون الحدود
    COLOR_INPUT = "#0A0A0A"         # لون خانات الإدخال
    
    # Neon Accents
    COLOR_ACCENT_MAIN = "#00E5FF"   # أزرق نيون
    COLOR_ACCENT_HOVER = "#00B8CC"  # أزرق غامق
    COLOR_SUCCESS = "#00FF9D"       # أخضر نيون
    COLOR_DANGER = "#FF2E63"        # أحمر نيون
    
    # Text
    COLOR_TEXT_WHITE = "#FFFFFF"
    COLOR_TEXT_GRAY = "#666666"
    COLOR_LOG_TEXT = "#00FF9D"

    # --- Mappings (لتوافق الأسماء ومنع الأخطاء) ---
    COLOR_PRIMARY = COLOR_CARD
    COLOR_SECONDARY = "#141414"
    COLOR_SURFACE = COLOR_CARD
    COLOR_CARD_BORDER = "#333333" # تمت إضافته لمنع خطأ NameError
    COLOR_BORDER = COLOR_CARD_BORDER
    
    COLOR_ACCENT = COLOR_ACCENT_MAIN
    COLOR_ACCENT_BLUE = COLOR_ACCENT_MAIN
    COLOR_ACCENT_GREEN = COLOR_SUCCESS
    COLOR_WARNING = COLOR_DANGER
    
    COLOR_TEXT = COLOR_TEXT_WHITE
    COLOR_TEXT_DIM = COLOR_TEXT_GRAY

    # --- Fonts (الخطوط) ---
    @staticmethod
    def get_fonts():
        return {
            "header": ctk.CTkFont(family="Roboto Medium", size=28, weight="bold"),
            
            # العناوين الفرعية (باسمين للتوافق)
            "sub": ctk.CTkFont(family="Roboto", size=15, weight="bold"),
            "sub_header": ctk.CTkFont(family="Roboto", size=15, weight="bold"),
            
            "body": ctk.CTkFont(family="Roboto", size=13),
            "button": ctk.CTkFont(family="Roboto", size=13, weight="bold"),
            
            # الخطوط الناقصة التي سببت المشكلة
            "console": ctk.CTkFont(family="Consolas", size=11),
            "mono": ctk.CTkFont(family="Consolas", size=12), # <-- تم إصلاح الخطأ هنا
            
            "entry": ctk.CTkFont(family="Roboto Mono", size=12),
            "label": ctk.CTkFont(family="Roboto", size=12, weight="bold"),
            "ui": ctk.CTkFont(family="Roboto", size=12, weight="bold")
        }