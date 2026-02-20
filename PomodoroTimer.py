import tkinter as tk
from tkinter import messagebox, ttk
import time
import threading
import pygame
import os
import sys
from datetime import datetime
import json
from tkinter import simpledialog, font


class PomodoroTimer:
    WORK_MINUTES = 25
    SHORT_BREAK_MINUTES = 5
    LONG_BREAK_MINUTES = 15
    CYCLES_BEFORE_LONG_BREAK = 4

    @staticmethod
    def get_app_folder():
        if getattr(sys, "frozen", False):
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.abspath(__file__))
    
    SETTINGS_FILE = os.path.join(get_app_folder(), "settings.json")
    STATS_FILE = os.path.join(get_app_folder(), "stats.json")

    
    THEMES = {
        "Классическая (тёмная)": {
            "bg": "#2c3e50",
            "fg": "#ecf0f1",
            "work": "#e74c3c",
            "short_break": "#3498db",
            "long_break": "#27ae60",
            "button": "#34495e",
            "button_hover": "#2990b9"
        },
        "Светлая тема": {
            "bg": "#f5f5f5",
            "fg": "#2c3e50",
            "work": "#c0392b",
            "short_break": "#2980b9",
            "long_break": "#27ae60",
            "button": "#bdc3c7",
            "button_hover": "#95a5a6"
        },
        "Космос": {
            "bg": "#1a1a2e",
            "fg": "#e0e0e0",
            "work": "#e94560",
            "short_break": "#0f3460",
            "long_break": "#533483",
            "button": "#16213e",
            "button_hover": "#0f3460"
        },
        "Морская": {
            "bg": "#1e3c72",
            "fg": "#f0f0f0",
            "work": "#f8b400",
            "short_break": "#2a9d8f",
            "long_break": "#e76f51",
            "button": "#2a5298",
            "button_hover": "#1e3c72"
        },
        "Лавандовая": {
            "bg": "#967aa1",
            "fg": "#ffffff",
            "work": "#6b4e71",
            "short_break": "#aa7b9e",
            "long_break": "#b39bc8",
            "button": "#7a5b7d",
            "button_hover": "#8b6b8e"
        },
        "Мятная": {
            "bg": "#98c1d9",
            "fg": "#1e2f4a",
            "work": "#ee6c4d",
            "short_break": "#3d5a80",
            "long_break": "#2b4f5c",
            "button": "#4f7a8c",
            "button_hover": "#5f8a9c"
        },
        "Закат": {
            "bg": "#2d1b3c",
            "fg": "#f6e9e9",
            "work": "#ff6f61",
            "short_break": "#d4a5a5",
            "long_break": "#b76e79",
            "button": "#3d2645",
            "button_hover": "#4d3655"
        },
        "Лесная": {
            "bg": "#1e3c2f",
            "fg": "#e0e7d9",
            "work": "#c44536",
            "short_break": "#558b6e",
            "long_break": "#6b4f47",
            "button": "#2d5a3a",
            "button_hover": "#3d6a4a"
        },
        "Ночной океан": {
            "bg": "#0a2342",
            "fg": "#b9d8f2",
            "work": "#ffb347",
            "short_break": "#2a628f",
            "long_break": "#18435c",
            "button": "#153b5a",
            "button_hover": "#254b6a"
        },
        "Розовый закат": {
            "bg": "#ff9a9e",
            "fg": "#2c3e50",
            "work": "#fad0c4",
            "short_break": "#fbc2eb",
            "long_break": "#a18cd1",
            "button": "#fbc2eb",
            "button_hover": "#fad0c4"
        },
        "Киберпанк": {
            "bg": "#0d0221",
            "fg": "#0ff0fc",
            "work": "#f706cf",
            "short_break": "#6b0f9c",
            "long_break": "#b30fc7",
            "button": "#240b36",
            "button_hover": "#6b0f9c"
        },
        "Кофейня": {
            "bg": "#3e2723",
            "fg": "#d7ccc8",
            "work": "#ff6f4a",
            "short_break": "#8d6e63",
            "long_break": "#a1887f",
            "button": "#5d4037",
            "button_hover": "#8d6e63"
        },
        "Неон": {
            "bg": "#000000",
            "fg": "#ffffff",
            "work": "#39ff14",
            "short_break": "#ff073a",
            "long_break": "#0ff0fc",
            "button": "#111111",
            "button_hover": "#39ff14"
        },
        "Пастель": {
            "bg": "#f8edd9",
            "fg": "#5e5b70",
            "work": "#ffb6b9",
            "short_break": "#bbe4e9",
            "long_break": "#c6d8b9",
            "button": "#e3d8c5",
            "button_hover": "#ffb6b9"
        }
    }
    
    def __init__(self, root):
        self.root = root
        self.root.title("Таймер помодоро")
        self.root.geometry("500x600")
        self.root.resizable(False, False)

        self.colors = self.THEMES["Классическая (тёмная)"]
        self.current_theme = "Классическая (тёмная)"

        self.root.configure(bg=self.colors["bg"])

        pygame.mixer.init()
        self.load_bell_sound()

        self.load_settings()

        self.root.configure(bg=self.colors["bg"])
        
        self.work_time = self.WORK_MINUTES * 60
        self.short_break = self.SHORT_BREAK_MINUTES * 60
        self.long_break = self.LONG_BREAK_MINUTES * 60
        self.cycles = 0
        self.max_cycles = self.CYCLES_BEFORE_LONG_BREAK
        self.is_running = False
        self.is_paused = False
        self.current_time = self.work_time
        self.current_phase = "work"
        self.timer_thread = None
        self.next_second = 0
        self.volume = 70

        self.today_pomodoros = 0
        self.total_pomodoros = 0
        self.last_date = datetime.now().strftime("%Y-%m-%d")
        self.load_stats()


        self.create_widgets()
        
    
    def load_settings(self):
        try:
            if os.path.exists(self.SETTINGS_FILE):
                with open(self.SETTINGS_FILE, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    self.WORK_MINUTES = settings.get("work_minutes", 25)
                    self.SHORT_BREAK_MINUTES = settings.get("short_break_minutes", 5)
                    self.LONG_BREAK_MINUTES = settings.get("long_break_minutes", 15)
                    self.volume = settings.get("volume", 70)
                    
                    theme_name = settings.get("theme", "Классическая (тёмная)")
                    if theme_name in self.THEMES:
                        self.colors = self.THEMES[theme_name]
                        self.current_theme = theme_name
                    else:
                        self.colors = self.THEMES["Классическая (тёмная)"]
                        self.current_theme = "Классическая (тёмная)"
                        
                    print("Настройки загружены")
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")
            self.colors = self.THEMES["Классическая (тёмная)"]
            self.current_theme = "Классическая (тёмная)"
    
    def save_settings(self):
        try:
            settings = {
                "work_minutes": self.WORK_MINUTES,
                "short_break_minutes": self.SHORT_BREAK_MINUTES,
                "long_break_minutes": self.LONG_BREAK_MINUTES,
                "theme": self.current_theme,
                "volume": self.volume
            }
            with open(self.SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
            print("Настройки сохранены")
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")
    
    def load_stats(self):
        try:
            if os.path.exists(self.STATS_FILE):
                with open(self.STATS_FILE, "r", encoding="utf-8") as f:
                    stats = json.load(f)
                    self.total_pomodoros = stats.get("total_pomodoros", 0)
                    self.last_date = stats.get("last_date", datetime.now().strftime("%Y-%m-%d"))
                    
                    today = datetime.now().strftime("%Y-%m-%d")
                    if today == self.last_date:
                        self.today_pomodoros = stats.get("today_pomodoros", 0)
                    else:
                        self.today_pomodoros = 0
                    print("Статистика загружена")
        except Exception as e:
            print(f"Ошибка загрузки статистики: {e}")

    def save_stats(self):
        try:
            stats = {
                "today_pomodoros": self.today_pomodoros,
                "total_pomodoros": self.total_pomodoros,
                "last_date": self.last_date
            }
            with open(self.STATS_FILE, "w", encoding="utf-8") as f:
                json.dump(stats, f, indent=4, ensure_ascii=False)
            print("Статистика сохранена")
        except Exception as e:
            print(f"Ошибка сохранения статистики: {e}")


    def update_stats(self):
        self.today_pomodoros += 1
        self.total_pomodoros += 1
        self.last_date = datetime.now().strftime("%Y-%m-%d")
        self.save_stats()
        self.update_stats_display()
    
    def apply_theme(self):
        self.root.configure(bg=self.colors["bg"])
        
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.create_widgets()
        self.update_display()
        self.update_info_text()
    
    def load_bell_sound(self):
        try:
            if os.path.exists("sounds") and os.path.exists("sounds/bell.wav"):
                self.bell_sound = pygame.mixer.Sound("sounds/bell.wav")
                if hasattr(self, "volume"):
                    self.bell_sound.set_volume(self.volume / 100)
                print(f"Звук колокольчика загружен, громкость: {self.volume}%")
            else:
                self.bell_sound = None
                print("Звук колокольчика не найден, будет системный звук")
        except Exception as e:
            print(f"Ошибка загрузки звука: {e}")
            self.bell_sound = None
    
    def play_bell(self):
        try:
            if self.bell_sound:
                self.bell_sound.play()
            else:
                print("\a")
        except Exception as e:
            print(f"Ошибка воспроизведения: {e}")
            print("\a")
    
    def send_notification(self, title, message):
        """Отправляет уведомление в виде окошка"""
        try:
            self.root.after(0, lambda: messagebox.showinfo(title, message))
        except Exception as e:
            print(f"Ошибка уведомления: {e}")

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
        
        timer_frame = tk.Frame(self.root, bg=self.colors["bg"], highlightbackground=self.colors["fg"], highlightthickness=2)
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
        stats_frame.pack(pady=5)


        self.stats_label = tk.Label(
            stats_frame,
            text=f"📊 Сегодня: {self.today_pomodoros} | Всего: {self.total_pomodoros}",
            font=("Arial", 10),
            bg=self.colors["bg"],
            fg=self.colors["fg"]
        )
        self.stats_label.pack()
        
        control_frame = tk.Frame(self.root, bg=self.colors["bg"])
        control_frame.pack(pady=20)
        
        self.start_button = self.create_button(
            control_frame,
            "▶️ Старт",
            self.start_timer,
            self.colors["button_hover"]
        )
        self.start_button.pack(side="left", padx=5)
        
        self.pause_button = self.create_button(
            control_frame,
            "⏸️ Пауза",
            self.pause_timer,
            self.colors["button"]
        )
        self.pause_button.pack(side="left", padx=5)
        self.pause_button.config(state="disabled")
        
        self.reset_button = self.create_button(
            control_frame,
            "↺ Сброс",
            self.reset_timer,
            self.colors["button"]
        )
        self.reset_button.pack(side="left", padx=5)
        
        self.settings_button = self.create_button(
            control_frame,
            "⚙️ Настройки",
            self.open_settings_window,
            self.colors["button_hover"]
        )
        self.settings_button.pack(side="left", padx=5)
        
        info_frame = tk.Frame(self.root, bg=self.colors["bg"])
        info_frame.pack(side="bottom", pady=20)
        
        info_text = f"{self.WORK_MINUTES} минут работа → {self.SHORT_BREAK_MINUTES} минут отдыха\n{self.CYCLES_BEFORE_LONG_BREAK} цикла → {self.LONG_BREAK_MINUTES} минут большой перерыв"
        
        info_label = tk.Label(
            info_frame,
            text=info_text,
            font=("Arial", 10),
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            justify="center"
        )
        info_label.pack()
        self.info_label = info_label
    
    def create_button(self, parent, text, command, hover_color):
        button = tk.Button(
            parent,
            text=text,
            font=("Arial", 11),
            bg=self.colors["button"],
            fg=self.colors["fg"],
            activebackground=hover_color,
            activeforeground=self.colors["fg"],
            relief="flat",
            padx=15,
            pady=8,
            cursor="hand2",
            command=command
        )
        
        def on_enter(e):
            button["background"] = hover_color
        
        def on_leave(e):
            button["background"] = self.colors["button"]
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
        return button
    
    def update_display(self):
        minutes = int(self.current_time // 60)
        seconds = int(self.current_time % 60)
        self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
        
        if self.current_phase == "work":
            total = self.work_time
        elif self.current_phase == "short_break":
            total = self.short_break
        else:
            total = self.long_break
        
        if total > 0:
            progress_value = ((total - self.current_time) / total) * 100
            self.progress["value"] = progress_value
    
    def update_stats_display(self):
        if hasattr(self, 'stats_label'):
            self.stats_label.config(
                text=f"📊 Сегодня: {self.today_pomodoros} | Всего: {self.total_pomodoros}"
            )
    
    def update_info_text(self):
        """Обновляет информационный текст внизу экрана"""
        if hasattr(self, 'info_label'):
            self.info_label.config(
                text=f"{self.WORK_MINUTES} минут работа → {self.SHORT_BREAK_MINUTES} минут отдыха\n{self.CYCLES_BEFORE_LONG_BREAK} цикла → {self.LONG_BREAK_MINUTES} минут большой перерыв"
            )
    
    def switch_phase(self):
        if self.current_phase == "work":
            self.cycles += 1
            self.cycles_label.config(text=f"Циклов завершено: {self.cycles}")
            
            self.update_stats()
            
            if self.cycles % self.max_cycles == 0:
                self.current_phase = "long_break"
                self.current_time = self.long_break
                self.phase_label.config(
                    text="Большой перерыв!",
                    fg=self.colors["long_break"]
                )
                self.send_notification("🍅 Помодоро", "Время большого перерыва! 15 минут отдыха")
            else:
                self.current_phase = "short_break"
                self.current_time = self.short_break
                self.phase_label.config(
                    text="Короткий отдых",
                    fg=self.colors["short_break"]
                )
                self.send_notification("🍅 Помодоро", f"Короткий перерыв! {self.SHORT_BREAK_MINUTES} минут отдыха")
        else: 
            self.current_phase = "work"
            self.current_time = self.work_time
            self.phase_label.config(
                text="Время работать!",
                fg=self.colors["work"]
            )
            self.send_notification("🍅 Помодоро", f"Отдых закончен! {self.WORK_MINUTES} минут работы")

        
        self.play_bell()
        self.update_display()
        
        self.is_running = False  
        self.start_timer()  
    
    def timer_function(self):
        self.next_second = time.time() + 1
        while self.is_running and self.current_time > 0:
            if not self.is_paused:
                now = time.time()
                if now >= self.next_second:
                    self.current_time -= 1
                    self.root.after(0, self.update_display)
                    self.next_second += 1
                time.sleep(0.05)
            else:
                time.sleep(0.1)
                self.next_second = time.time() + 1
        if self.is_running and self.current_time <= 0:
            self.is_running = False
            self.root.after(0, self.switch_phase)
         
    def start_timer(self):
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            self.start_button.config(state="disabled")
            self.pause_button.config(state="normal")
            self.timer_thread = threading.Thread(target=self.timer_function, daemon=True)
            self.timer_thread.start()
    
    def pause_timer(self):
        if self.is_running:
            if not self.is_paused:
                self.is_paused = True
                self.pause_button.config(text="▶️ Продолжить")
            else:
                self.is_paused = False
                self.pause_button.config(text="⏸️ Пауза")
    
    def reset_timer(self):
        self.is_running = False
        self.is_paused = False
        self.current_time = self.work_time
        self.current_phase = "work"
        self.phase_label.config(text="Время работать!", fg=self.colors["work"])
        self.cycles = 0
        self.cycles_label.config(text="Циклов завершено: 0")
        
        self.start_button.config(state="normal")
        self.pause_button.config(state="disabled", text="⏸️ Пауза")
        
        self.update_display()
        self.progress["value"] = 0
    
    def open_settings_window(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Настройки таймера")
        settings_window.geometry("450x500")
        settings_window.configure(bg=self.colors["bg"])
        settings_window.resizable(False, False)


        tab_control = ttk.Notebook(settings_window)
        
        time_tab = tk.Frame(tab_control, bg=self.colors["bg"])
        tab_control.add(time_tab, text="Время")
        
        color_tab = tk.Frame(tab_control, bg=self.colors["bg"])
        tab_control.add(color_tab, text="Оформление")
        
        sound_tab = tk.Frame(tab_control, bg=self.colors["bg"])
        tab_control.add(sound_tab, text="Звук")
        
        tab_control.pack(expand=1, fill="both", padx=10, pady=10)

        
        title_label = tk.Label(
            time_tab,
            text="Настройки времени",
            font=("Arial", 14, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["fg"]
        )
        title_label.pack(pady=15)

        settings_frame = tk.Frame(time_tab, bg=self.colors["bg"])
        settings_frame.pack(pady=10)

        work_label = tk.Label(
            settings_frame,
            text="Работа (минут):",
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=("Arial", 10)
        )
        work_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        work_var = tk.IntVar(value=self.WORK_MINUTES)
        work_entry = tk.Entry(
            settings_frame,
            textvariable=work_var,
            width=10,
            font=("Arial", 10)
        )
        work_entry.grid(row=0, column=1, padx=10, pady=5)

        short_label = tk.Label(
            settings_frame,
            text="Короткий отдых:",
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=("Arial", 10)
        )
        short_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        short_var = tk.IntVar(value=self.SHORT_BREAK_MINUTES)
        short_entry = tk.Entry(
            settings_frame,
            textvariable=short_var,
            width=10,
            font=("Arial", 10)
        )
        short_entry.grid(row=1, column=1, padx=10, pady=5)

        long_label = tk.Label(
            settings_frame,
            text="Длинный отдых:",
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=("Arial", 10)
        )
        long_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        long_var = tk.IntVar(value=self.LONG_BREAK_MINUTES)
        long_entry = tk.Entry(
            settings_frame,
            textvariable=long_var,
            width=10,
            font=("Arial", 10)
        )
        long_entry.grid(row=2, column=1, padx=10, pady=5)

        
        theme_label = tk.Label(
            color_tab,
            text="Выберите тему оформления",
            font=("Arial", 14, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["fg"]
        )
        theme_label.pack(pady=15)

        # Создаём прокрутку
        canvas = tk.Canvas(color_tab, bg=self.colors["bg"], highlightthickness=0)
        scrollbar = tk.Scrollbar(color_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors["bg"])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        theme_frame = scrollable_frame

        theme_var = tk.StringVar(value=self.current_theme)
        
        row = 0
        col = 0
        for theme_name in self.THEMES.keys():
            theme_btn = tk.Radiobutton(
                theme_frame,
                text=theme_name,
                variable=theme_var,
                value=theme_name,
                bg=self.colors["bg"],
                fg=self.colors["fg"],
                selectcolor=self.colors["bg"],
                font=("Arial", 10)
            )
            theme_btn.grid(row=row, column=col, padx=20, pady=5, sticky="w")
            
            colors_preview = tk.Frame(theme_frame, bg=self.THEMES[theme_name]["bg"], width=30, height=20)
            colors_preview.grid(row=row, column=col+1, padx=5, pady=5)
            
            col += 2
            if col > 3:
                col = 0
                row += 1

        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")

        
        sound_label = tk.Label(
            sound_tab,
            text="Настройки звука",
            font=("Arial", 14, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["fg"]
        )
        sound_label.pack(pady=15)

        sound_frame = tk.Frame(sound_tab, bg=self.colors["bg"])
        sound_frame.pack(pady=20)

        volume_text = tk.Label(
            sound_frame,
            text="Громкость звука:",
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=("Arial", 11)
        )
        volume_text.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        volume_var = tk.IntVar(value=self.volume)
        volume_value = tk.Label(
            sound_frame,
            text=f"{self.volume}%",
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=("Arial", 11, "bold")
        )
        volume_value.grid(row=0, column=1, padx=10, pady=10)

        volume_scale = tk.Scale(
            sound_frame,
            from_=0,
            to=100,
            orient="horizontal",
            variable=volume_var,
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            length=200,
            command=lambda v: volume_value.config(text=f"{int(float(v))}%")
        )
        volume_scale.grid(row=1, column=0, columnspan=2, padx=10, pady=10)


        button_frame = tk.Frame(settings_window, bg=self.colors["bg"])
        button_frame.pack(pady=20)
        
        def save_and_close():
            if work_var.get() > 0 and short_var.get() > 0 and long_var.get() > 0:
                self.WORK_MINUTES = work_var.get()
                self.SHORT_BREAK_MINUTES = short_var.get()
                self.LONG_BREAK_MINUTES = long_var.get()


                self.work_time = self.WORK_MINUTES * 60
                self.short_break = self.SHORT_BREAK_MINUTES * 60
                self.long_break = self.LONG_BREAK_MINUTES * 60

                if not self.is_running:
                    self.current_time = self.work_time
                
                selected_theme = theme_var.get()
                if selected_theme in self.THEMES:
                    self.current_theme = selected_theme
                    self.colors = self.THEMES[selected_theme]
                
                self.volume = volume_var.get()
                if self.bell_sound:
                    self.bell_sound.set_volume(self.volume / 100)
                
                self.save_settings()
                self.apply_theme()
                self.update_info_text()
                
                settings_window.destroy()
            else:
                messagebox.showerror("Ошибка", "Все значения должны быть положительными!")
        
        save_button = tk.Button(
            button_frame,
            text="Сохранить",
            command=save_and_close,
            bg=self.colors["button"],
            fg=self.colors["fg"],
            padx=20,
            pady=5
        )
        save_button.pack(side="left", padx=10)
        
        cancel_button = tk.Button(
            button_frame,
            text="Отмена",
            command=settings_window.destroy,
            bg=self.colors["button"],
            fg=self.colors["fg"],
            padx=20,
            pady=5
        )
        cancel_button.pack(side="left", padx=10)

def main():
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop()

if __name__ == "__main__":
    main()