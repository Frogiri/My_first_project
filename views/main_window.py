import tkinter as tk
from tkinter import ttk
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from themes import THEMES
from utils import adjust_color_alpha

class MainWindow:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.colors = THEMES["Классическая (тёмная)"]
        
        
        self.root.title("Таймер помодоро")
        self.root.geometry("500x700")
        self.root.resizable(False, False)
        self.root.configure(bg=self.colors["bg"])
        
        
        self.pulse_alpha = 1.0
        self.pulse_direction = -0.03
        
        
        self.create_widgets()
        
        
        self.controller.register_view(self)
    
    def create_widgets(self):
        
        title_frame = tk.Frame(self.root, bg=self.colors["bg"])
        title_frame.pack(pady=20)
        
        title_label = tk.Label(
            title_frame,
            text="Таймер Помодоро",
            font=("Arial", 24, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["fg"]
        )
        title_label.pack()
        
        
        timer_frame = tk.Frame(
            self.root, 
            bg=self.colors["bg"], 
            highlightbackground=self.colors["fg"], 
            highlightthickness=2
        )
        timer_frame.pack(pady=20, padx=40, fill="x")
        
        
        self.phase_label = tk.Label(
            timer_frame,
            text="Время работать!",
            font=("Arial", 16),
            bg=self.colors["bg"],
            fg=self.colors["work"]
        )
        self.phase_label.pack(pady=10)
        
        
        self.timer_label = tk.Label(
            timer_frame,
            text="25:00",
            font=("Arial", 48, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["fg"]
        )
        self.timer_label.pack(pady=10)
        
        
        self.progress = ttk.Progressbar(
            timer_frame,
            length=300,
            mode="determinate"
        )
        self.progress.pack(pady=10)
        
        
        cycles_frame = tk.Frame(self.root, bg=self.colors["bg"])
        cycles_frame.pack(pady=10)
        
        self.cycles_label = tk.Label(
            cycles_frame,
            text="Циклов завершено: 0",
            font=("Arial", 12),
            bg=self.colors["bg"],
            fg=self.colors["fg"]
        )
        self.cycles_label.pack()
        
        
        stats_frame = tk.Frame(self.root, bg=self.colors["bg"])
        stats_frame.pack(pady=2)

        stats_inner = tk.Frame(stats_frame, bg=self.colors["bg"])
        stats_inner.pack()

        emoji_label = tk.Label(
            stats_inner,
            text="📊",
            font=("Arial", 11),
            bg=self.colors["bg"],
            fg=self.colors["fg"]
        )
        emoji_label.pack(side="left", padx=(0, 2))

        self.stats_text_label = tk.Label(
            stats_inner,
            text="Сегодня: 0 | Всего: 0",
            font=("Arial", 10),
            bg=self.colors["bg"],
            fg=self.colors["fg"]
        )
        self.stats_text_label.pack(side="left")
        
        
        control_frame = tk.Frame(self.root, bg=self.colors["bg"])
        control_frame.pack(pady=20)
        
        self.start_button = self.create_button(
            control_frame,
            "▶️Старт",
            self.controller.start_timer,
            self.colors["button_hover"]
        )
        self.start_button.pack(side="left", padx=5)
        
        self.pause_button = self.create_button(
            control_frame,
            "⏸️Пауза",
            self.controller.pause_timer,
            self.colors["button"]
        )
        self.pause_button.pack(side="left", padx=5)
        self.pause_button.config(state="disabled")
        
        self.reset_button = self.create_button(
            control_frame,
            "↺Сброс",
            self.controller.reset_timer,
            self.colors["button"]
        )
        self.reset_button.pack(side="left", padx=5)
        
        self.settings_button = self.create_button(
            control_frame,
            "⚙️Настройки",
            self.controller.open_settings,
            self.colors["button_hover"]
        )
        self.settings_button.pack(side="left", padx=5)
        
        
        achievements_frame = tk.Frame(self.root, bg=self.colors["bg"])
        achievements_frame.pack(pady=10)
        
        self.achievements_button = self.create_button(
            achievements_frame,
            "🏆 Достижения",
            self.controller.open_achievements,
            self.colors["button_hover"]
        )
        self.achievements_button.pack()
        
        
        info_frame = tk.Frame(self.root, bg=self.colors["bg"])
        info_frame.pack(side="bottom", pady=20)
        
        self.info_label = tk.Label(
            info_frame,
            text="25 минут работа → 5 минут отдыха\n4 цикла → 15 минут большой перерыв",
            font=("Arial", 10),
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            justify="center"
        )
        self.info_label.pack()
    
    def create_button(self, parent, text, command, hover_color):
        """Создаёт красивую кнопку"""
        outline_color = self.colors.get("button_outline", self.colors["fg"])
        
        if "Пауза" in text:
            button_color = self.colors.get("button_pause", self.colors["button"])
        elif "Сброс" in text:
            button_color = self.colors.get("button_reset", self.colors["button"])
        else:
            button_color = self.colors["button"]
        
        button = tk.Button(
            parent,
            text=text,
            font=("Arial", 11),
            bg=button_color,
            fg=self.colors["fg"],
            activebackground=hover_color,
            activeforeground=self.colors["fg"],
            relief="flat",
            padx=15,
            pady=8,
            cursor="hand2",
            command=command,
            highlightbackground=outline_color,
            highlightthickness=1 if "button_outline" in self.colors else 0
        )
        
        def on_enter(e):
            button["background"] = hover_color
            button.config(font=("Arial", 12, "bold"))
        
        def on_leave(e):
            if "Пауза" in text:
                button["background"] = self.colors.get("button_pause", self.colors["button"])
            elif "Сброс" in text:
                button["background"] = self.colors.get("button_reset", self.colors["button"])
            else:
                button["background"] = self.colors["button"]
            button.config(font=("Arial", 11))
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
        return button
    
    
    
    def update_timer(self, time_str, progress):
        self.timer_label.config(text=time_str)
        self.progress["value"] = progress
    
    def update_phase(self, phase, color):
        texts = {
            "work": "Время работать!",
            "short_break": "Короткий отдых",
            "long_break": "Большой перерыв!"
        }
        self.phase_label.config(text=texts.get(phase, ""), fg=color)
    
    def update_cycles(self, cycles):
        self.cycles_label.config(text=f"Циклов завершено: {cycles}")
    
    def update_stats(self, today, total):
        self.stats_text_label.config(text=f"Сегодня: {today} | Всего: {total}")
    
    def update_info(self, work, short, long_break, cycles):
        self.info_label.config(
            text=f"{work} минут работа → {short} минут отдыха\n{cycles} цикла → {long_break} минут большой перерыв"
        )
    
    def update_theme(self, colors):
        self.colors = colors
        self.root.configure(bg=colors["bg"])
        # Пересоздаём виджеты с новыми цветами
        for widget in self.root.winfo_children():
            widget.destroy()
        self.create_widgets()
    
    def set_button_state(self, is_running, is_paused):
        if is_running:
            self.start_button.config(state="disabled")
            self.pause_button.config(state="normal")
            self.pause_button.config(text="⏸️Пауза" if not is_paused else "▶️Продолжить")
        else:
            self.start_button.config(state="normal")
            self.pause_button.config(state="disabled", text="⏸️Пауза")
    
    
    
    def start_animations(self):
        self.pulse_animation()
    
    def pulse_animation(self):
        
        self.root.after(50, self.pulse_animation)