import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.timer import TimerModel
from models.achievements import AchievementsModel
from data.file_manager import FileManager
from views.settings_window import SettingsWindow
from views.achievements_window import AchievementsWindow
from themes import THEMES


class AppController:
    def __init__(self):
        self.timer = TimerModel()
        self.achievements = AchievementsModel()
        self.view = None
        self.current_theme = "Классическая (тёмная)"
        self.colors = THEMES[self.current_theme]
        self.volume = 70
        self.no_pause_streak = 0
        self.no_reset_streak = 0
        self.today_pomodoros = 0
        self.total_pomodoros = 0
        self.last_date = None
        
        
        self.load_data()
        
        
        self.timer.on_update = self.on_timer_update
        self.timer.on_phase_change = self.on_phase_change
        self.achievements.on_unlock = self.on_achievement_unlock
    
    def register_view(self, view):
        self.view = view
        self.view.start_animations()
    
    def load_data(self):
        
        settings = FileManager.load_settings()
        self.volume = settings.get("volume", 70)
        self.current_theme = settings.get("theme", "Классическая (тёмная)")
        self.colors = THEMES.get(self.current_theme, THEMES["Классическая (тёмная)"])
        
        
        stats = FileManager.load_stats()
        self.total_pomodoros = stats.get("total_pomodoros", 0)
        self.last_date = stats.get("last_date", "")
        
        
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        if today == self.last_date:
            self.today_pomodoros = stats.get("today_pomodoros", 0)
        else:
            self.today_pomodoros = 0
        
        
        if "achievements" in stats:
            self.achievements.from_dict(stats["achievements"])
    
    def save_data(self):
        settings = {
            "work_minutes": self.timer.work_time // 60,
            "short_break_minutes": self.timer.short_break // 60,
            "long_break_minutes": self.timer.long_break // 60,
            "theme": self.current_theme,
            "volume": self.volume
        }
        FileManager.save_settings(settings)
        
        stats = {
            "today_pomodoros": self.today_pomodoros,
            "total_pomodoros": self.total_pomodoros,
            "last_date": self.last_date,
            "achievements": self.achievements.to_dict()
        }
        FileManager.save_stats(stats)
    
    
    
    def start_timer(self):
        self.timer.start()
        if self.view:
            self.view.set_button_state(True, False)
    
    def pause_timer(self):
        result = self.timer.pause()
        if result == "paused":
            self.no_pause_streak = 0
        if self.view:
            self.view.set_button_state(True, self.timer.is_paused)
    
    def reset_timer(self):
        self.timer.reset()
        self.no_reset_streak = 0
        if self.view:
            self.view.set_button_state(False, False)
    
    def on_timer_update(self):
        if self.view:
            self.view.update_timer(
                self.timer.get_time_str(),
                self.timer.get_progress()
            )
    
    def on_phase_change(self, phase):
        if phase == "work":
            
            pass
        else:
            
            self.today_pomodoros += 1
            self.total_pomodoros += 1
            self.no_pause_streak += 1
            self.no_reset_streak += 1
            
            
            self.achievements.check_all(
                {"today": self.today_pomodoros, "total": self.total_pomodoros},
                self.current_theme,
                self.no_pause_streak,
                self.no_reset_streak
            )
            
            if self.view:
                self.view.update_stats(self.today_pomodoros, self.total_pomodoros)
                self.view.update_cycles(self.timer.cycles)
        
        
        colors = {
            "work": self.colors["work"],
            "short_break": self.colors["short_break"],
            "long_break": self.colors["long_break"]
        }
        if self.view:
            self.view.update_phase(phase, colors.get(phase, self.colors["fg"]))
    
    def on_achievement_unlock(self, name):
        if self.view:
            from tkinter import messagebox
            self.view.root.after(0, lambda: messagebox.showinfo(
                "🏆 Достижение получено!", 
                f"Вы разблокировали: {name}"
            ))
    
    
    
    def open_settings(self):
        SettingsWindow(self.view.root, self)
    
    def open_achievements(self):
        AchievementsWindow(self.view.root, self)
    
    
    
    def update_settings(self, work, short, long_break, theme, volume):
        self.timer.set_times(work, short, long_break)
        self.current_theme = theme
        self.colors = THEMES[theme]
        self.volume = volume
        
        if self.view:
            self.view.update_theme(self.colors)
            self.view.update_info(work, short, long_break, self.timer.max_cycles)
        
        self.save_data()