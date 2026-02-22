import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import get_app_folder

class FileManager:
    SETTINGS_FILE = os.path.join(get_app_folder(), "settings.json")
    STATS_FILE = os.path.join(get_app_folder(), "stats.json")
    
    @staticmethod
    def save_settings(settings):
        try:
            with open(FileManager.SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
                print("Настройки сохранены")
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")
    
    @staticmethod
    def load_settings():
        try:
            if os.path.exists(FileManager.SETTINGS_FILE):
                with open(FileManager.SETTINGS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")
        return {}
    
    @staticmethod
    def save_stats(stats):
        try:
            with open(FileManager.STATS_FILE, "w", encoding="utf-8") as f:
                json.dump(stats, f, indent=4, ensure_ascii=False)
                print("Статистика сохранена")
        except Exception as e:
            print(f"Ошибка сохранения статистики: {e}")
    
    @staticmethod
    def load_stats():
        try:
            if os.path.exists(FileManager.STATS_FILE):
                with open(FileManager.STATS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки статистики: {e}")
        return {}