import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from themes import THEMES
from utils import get_brightness


class SettingsWindow:
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.colors = controller.colors
        
        
        self.window = tk.Toplevel(parent)
        self.window.title("Настройки таймера")
        self.window.geometry("450x600")
        self.window.configure(bg=self.colors["bg"])
        self.window.resizable(False, False)
        
        
        def validate_number(char):
            return char.isdigit() or char == ""
        
        self.validation = self.window.register(validate_number)
        
        
        self.create_tabs()
        
        
        self.load_current_values()
        
        
        self.create_buttons()
    
    def create_tabs(self):
        
        self.tab_control = ttk.Notebook(self.window)
        
        
        self.time_tab = tk.Frame(self.tab_control, bg=self.colors["bg"])
        self.tab_control.add(self.time_tab, text="Время")
        self.create_time_tab()
        
        
        self.color_tab = tk.Frame(self.tab_control, bg=self.colors["bg"])
        self.tab_control.add(self.color_tab, text="Оформление")
        self.create_color_tab()
        
        
        self.sound_tab = tk.Frame(self.tab_control, bg=self.colors["bg"])
        self.tab_control.add(self.sound_tab, text="Звук")
        self.create_sound_tab()
        
        self.tab_control.pack(expand=1, fill="both", padx=10, pady=10)
    
    def create_time_tab(self):
        
        title = tk.Label(
            self.time_tab,
            text="Настройки времени",
            font=("Arial", 14, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["fg"]
        )
        title.pack(pady=15)
        
        
        frame = tk.Frame(self.time_tab, bg=self.colors["bg"])
        frame.pack(pady=10)
        
        
        tk.Label(
            frame,
            text="Работа (минут):",
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=("Arial", 10)
        ).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.work_var = tk.IntVar()
        work_entry = tk.Entry(
            frame,
            textvariable=self.work_var,
            width=10,
            font=("Arial", 10),
            validate="key",
            validatecommand=(self.validation, "%P")
        )
        work_entry.grid(row=0, column=1, padx=10, pady=5)
        
        
        tk.Label(
            frame,
            text="Короткий отдых:",
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=("Arial", 10)
        ).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.short_var = tk.IntVar()
        short_entry = tk.Entry(
            frame,
            textvariable=self.short_var,
            width=10,
            font=("Arial", 10),
            validate="key",
            validatecommand=(self.validation, "%P")
        )
        short_entry.grid(row=1, column=1, padx=10, pady=5)
        
        
        tk.Label(
            frame,
            text="Длинный отдых:",
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=("Arial", 10)
        ).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        self.long_var = tk.IntVar()
        long_entry = tk.Entry(
            frame,
            textvariable=self.long_var,
            width=10,
            font=("Arial", 10),
            validate="key",
            validatecommand=(self.validation, "%P")
        )
        long_entry.grid(row=2, column=1, padx=10, pady=5)
    
    def create_color_tab(self):
        
        title = tk.Label(
            self.color_tab,
            text="Выберите тему оформления",
            font=("Arial", 14, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["fg"]
        )
        title.pack(pady=15)
        
        
        canvas = tk.Canvas(self.color_tab, bg=self.colors["bg"], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.color_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors["bg"])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        
        self.theme_var = tk.StringVar()
        
        
        sorted_themes = sorted(
            THEMES.items(),
            key=lambda x: get_brightness(x[1]["bg"])
        )
        
        
        row = 0
        col = 0
        for theme_name, theme_colors in sorted_themes:
            theme_btn = tk.Radiobutton(
                scrollable_frame,
                text=theme_name,
                variable=self.theme_var,
                value=theme_name,
                bg=self.colors["bg"],
                fg=self.colors["fg"],
                selectcolor=self.colors["bg"],
                font=("Arial", 9)
            )
            theme_btn.grid(row=row, column=col, padx=10, pady=3, sticky="w")
            
            
            preview_frame = tk.Frame(
                scrollable_frame,
                bg=self.colors["fg"],
                width=24,
                height=19
            )
            preview_frame.grid(row=row, column=col+1, padx=5, pady=3)
            preview_frame.grid_propagate(False)
            
            colors_preview = tk.Frame(
                preview_frame,
                bg=theme_colors["bg"],
                width=20,
                height=15
            )
            colors_preview.place(x=2, y=2)
            
            col += 2
            if col > 3:
                col = 0
                row += 1
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
    
    def create_sound_tab(self):
        
        title = tk.Label(
            self.sound_tab,
            text="Настройки звука",
            font=("Arial", 14, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["fg"]
        )
        title.pack(pady=15)
        
        
        frame = tk.Frame(self.sound_tab, bg=self.colors["bg"])
        frame.pack(pady=20)
        
        
        tk.Label(
            frame,
            text="Громкость звука:",
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=("Arial", 11)
        ).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        
        self.volume_var = tk.IntVar()
        volume_value = tk.Label(
            frame,
            text=f"{self.volume_var.get()}%",
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=("Arial", 11, "bold")
        )
        volume_value.grid(row=0, column=1, padx=10, pady=10)
        
        
        volume_scale = tk.Scale(
            frame,
            from_=0,
            to=100,
            orient="horizontal",
            variable=self.volume_var,
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            length=200,
            command=lambda v: volume_value.config(text=f"{int(float(v))}%")
        )
        volume_scale.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
    
    def load_current_values(self):
        """Загружает текущие значения из контроллера"""
        self.work_var.set(self.controller.timer.work_time // 60)
        self.short_var.set(self.controller.timer.short_break // 60)
        self.long_var.set(self.controller.timer.long_break // 60)
        self.theme_var.set(self.controller.current_theme)
        self.volume_var.set(self.controller.volume)
    
    def create_buttons(self):
        """Создаёт кнопки Сохранить и Отмена"""
        button_frame = tk.Frame(self.window, bg=self.colors["bg"])
        button_frame.pack(pady=20)
        
        save_button = tk.Button(
            button_frame,
            text="Сохранить",
            command=self.save_and_close,
            bg=self.colors["button"],
            fg=self.colors["fg"],
            padx=20,
            pady=5
        )
        save_button.pack(side="left", padx=10)
        
        cancel_button = tk.Button(
            button_frame,
            text="Отмена",
            command=self.window.destroy,
            bg=self.colors["button"],
            fg=self.colors["fg"],
            padx=20,
            pady=5
        )
        cancel_button.pack(side="left", padx=10)
    
    def save_and_close(self):
        """Сохраняет настройки и закрывает окно"""
        work = self.work_var.get()
        short = self.short_var.get()
        long_break = self.long_var.get()
        
        if 1 <= work <= 999 and 1 <= short <= 999 and 1 <= long_break <= 999:
            self.controller.update_settings(
                work, short, long_break,
                self.theme_var.get(),
                self.volume_var.get()
            )
            self.window.destroy()
        else:
            messagebox.showerror("Ошибка", "Значения должны быть от 1 до 999!")