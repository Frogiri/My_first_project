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
from plyer import notification


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

        self.load_settings

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
                "theme": self.current_theme
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
                print("Звук колокольчика загружен")
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
        """Отправляет уведосление в Windows"""
        try:
            notification.notify(
                title = title,
                message=message,
                app_name = "Помодоро Таймер",
                timeout = 5
            )
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
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label) and "минут работа" in child.cget("text"):
                        child.config(text=f"{self.WORK_MINUTES} минут работы > {self.SHORT_BREAK_MINUTES} минут отдыха\n{self.CYCLES_BEFORE_LONG_BREAK} цикла > {self.LONG_BREAK_MINUTES} минут большой перерыв")
                        return
    
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
        settings_window.geometry("400x400")
        settings_window.configure(bg=self.colors["bg"])
        settings_window.resizable(False, False)

        tab_control = ttk.Notebook(settings_window)
        
        time_tab = tk.Frame(tab_control, bg=self.colors["bg"])
        tab_control.add(time_tab, text="Время")
        
        color_tab = tk.Frame(tab_control, bg=self.colors["bg"])
        tab_control.add(color_tab, text="Оформление")
        
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

        theme_frame = tk.Frame(color_tab, bg=self.colors["bg"])
        theme_frame.pack(pady=10)

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