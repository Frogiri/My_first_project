from datetime import datetime
import tkinter as tk
from tkinter import ttk
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

class AchievementsModel:
    def __init__(self):
        self.achievements = {
            "first_pomodoro": {"name": "🍅 Первый помидор", "desc": "Завершите первый цикл работы", "unlocked": False},
            "early_bird": {"name": "🐦 Ранняя пташка", "desc": "5 помидорок до 10 утра", "unlocked": False, "progress": 0, "target": 5},
            "marathon": {"name": "🏃 Марафонец", "desc": "100 помидорок всего", "unlocked": False, "progress": 0, "target": 100},
            "no_pause": {"name": "🎯 Без пауз", "desc": "10 помидорок подряд без пауз", "unlocked": False, "progress": 0, "target": 10},
            "workaholic": {"name": "💪 Трудоголик", "desc": "20 помидорок за день", "unlocked": False, "progress": 0, "target": 20},
            "night_owl": {"name": "🦉 Полуночник", "desc": "Помидорка после полуночи", "unlocked": False},
            "master_focus": {"name": "🧘 Мастер фокуса", "desc": "10 раз подряд без сброса", "unlocked": False, "progress": 0, "target": 10},
            "colorful": {"name": "🌈 Разноцветный", "desc": "Использовать все темы", "unlocked": False, "progress": 0, "target": 25}
        }
        self.on_unlock = None
    
    def check_all(self, stats, current_theme, no_pause_streak, no_reset_streak):
        """Проверяет все достижения"""
        self._check_first_pomodoro(stats["total"])
        self._check_early_bird()
        self._check_marathon(stats["total"])
        self._check_night_owl()
        self._check_workaholic(stats["today"])
        self._check_no_pause(no_pause_streak)
        self._check_master_focus(no_reset_streak)
        self._check_colorful(current_theme)
    
    def _check_first_pomodoro(self, total):
        if not self.achievements["first_pomodoro"]["unlocked"] and total >= 1:
            self._unlock("first_pomodoro")
    
    def _check_early_bird(self):
        hour = datetime.now().hour
        if hour < 10:
            self.achievements["early_bird"]["progress"] += 1
            if self.achievements["early_bird"]["progress"] >= 5:
                self._unlock("early_bird")
    
    def _check_marathon(self, total):
        self.achievements["marathon"]["progress"] = total
        if total >= 100:
            self._unlock("marathon")
    
    def _check_night_owl(self):
        hour = datetime.now().hour
        if hour == 0 and not self.achievements["night_owl"]["unlocked"]:
            self._unlock("night_owl")
    
    def _check_workaholic(self, today):
        self.achievements["workaholic"]["progress"] = today
        if today >= 20:
            self._unlock("workaholic")
    
    def _check_no_pause(self, streak):
        self.achievements["no_pause"]["progress"] = streak
        if streak >= 10:
            self._unlock("no_pause")
    
    def _check_master_focus(self, streak):
        self.achievements["master_focus"]["progress"] = streak
        if streak >= 10:
            self._unlock("master_focus")
    
    def _check_colorful(self, current_theme):
        
        pass
    
    def _unlock(self, ach_id):
        self.achievements[ach_id]["unlocked"] = True
        if self.on_unlock:
            self.on_unlock(self.achievements[ach_id]["name"])
    
    def get_unlocked_count(self):
        count = 0
        for ach in self.achievements.values():
            if ach["unlocked"]:
                count += 1
        return count
    
    def to_dict(self):
        """Для сохранения в JSON"""
        data = {}
        for ach_id, ach in self.achievements.items():
            data[ach_id] = {"unlocked": ach["unlocked"]}
            if "progress" in ach:
                data[ach_id]["progress"] = ach["progress"]
        return data
    
    def from_dict(self, data):
        """Для загрузки из JSON"""
        for ach_id, ach_data in data.items():
            if ach_id in self.achievements:
                self.achievements[ach_id]["unlocked"] = ach_data.get("unlocked", False)
                if "progress" in self.achievements[ach_id]:
                    self.achievements[ach_id]["progress"] = ach_data.get("progress", 0)