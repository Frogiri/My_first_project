import tkinter as tk
from tkinter import messagebox, ttk
import time
import threading
import pygame
import os
from datetime import datetime

class PomodoroTimer:
    #Здесь будет настройка таймера (в секундах!)
    WORK_MINUTES = 25
    SHORT_BREAK_MINUTES = 5
    LONG_BREAK_MINUTES = 15
    CYCLES_BEFORE_LONG_BREAK = 4
    def __init__(self, root):
        """Создаёт и настраивает таймер, окошки и кнопки"""
        self.root = root
        self.root.title("Таймер помодоро")
        self.root.geometry("500x600")
        self.root.resizable(False, False)

        self.colors = {
            "bg": "#2c3e50",
            "fg": "#ecf0f1",
            "work": "#e74c3c",
            "short_break": "#3498db",
            "long_break": "#27ae60",
            "button": "#34495e",
            "button_hover": "#2990b9"
        }
        self.root.configure(bg=self.colors["bg"])

        pygame.mixer.init()
        self.load_bell_sound()

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
        
        self.create_widgets()
    
    def load_bell_sound(self):
        """Загрузка звука колокольчика из папки souds. Если же звука нет - то ничего страшного!"""
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
        """Играет звонок, когда время вышло"""
        try:
            if self.bell_sound:
                self.bell_sound.play()
            else:
                print("\a")
        except Exception as e:
            print(f"Ошибка воспроизведения: {e}")
            print("\a")
    
    def create_widgets(self):
        """Создаёт кнопки и надписи на самом экране"""
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
        
        info_frame = tk.Frame(self.root, bg=self.colors["bg"])
        info_frame.pack(side="bottom", pady=20)
        
        info_text = """25 минут работа → 5 минут отдыха
4 цикла → 15 минут большой перерыв"""
        
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
        """Делает одну красивенькую кнопку"""
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
        """Показывает сколько времени осталось"""
        minutes = self.current_time // 60
        seconds = self.current_time % 60
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
    
    def switch_phase(self):
        """Переключение между работой и отдыхом"""
        if self.current_phase == "work":
            self.cycles += 1
            self.cycles_label.config(text=f"Циклов завершено: {self.cycles}")
            
            if self.cycles % self.max_cycles == 0:
                self.current_phase = "long_break"
                self.current_time = self.long_break
                self.phase_label.config(
                    text="Большой перерыв!",
                    fg=self.colors["long_break"]
                )
            else:
                self.current_phase = "short_break"
                self.current_time = self.short_break
                self.phase_label.config(
                    text="Короткий отдых",
                    fg=self.colors["short_break"]
                )
        else: 
            self.current_phase = "work"
            self.current_time = self.work_time
            self.phase_label.config(
                text="Время работать!",
                fg=self.colors["work"]
            )
        
        self.play_bell()
        self.update_display()
        
        
        self.is_running = False  
        self.start_timer()  
    
    def timer_function(self):
        """Считает секунды внутри таймера"""
        while self.is_running and self.current_time > 0:
            if not self.is_paused:
                time.sleep(1)
                self.current_time -= 1
                self.root.after(0, self.update_display)
        
        
        if self.is_running and self.current_time == 0:
            self.is_running = False  
            self.root.after(0, self.switch_phase)

    
    def start_timer(self):
        """Запускает таймер/отсчёт времени"""
        if not self.is_running:
            print(f"Запуск таймера: {self.current_phase}")
            self.is_running = True
            self.is_paused = False
            self.start_button.config(state="disabled")
            self.pause_button.config(state="normal")
            self.timer_thread = threading.Thread(target=self.timer_function, daemon=True)
            self.timer_thread.start()
    
    def pause_timer(self):
        """Ставит или снимает таймер с паузы"""
        if self.is_running:
            if not self.is_paused:
                self.is_paused = True
                self.pause_button.config(text="▶️ Продолжить")
            else:
                self.is_paused = False
                self.pause_button.config(text="⏸️ Пауза")
    
    def reset_timer(self):
        """Сбрасывает время"""
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

def main():
    """Запуск программы"""
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
