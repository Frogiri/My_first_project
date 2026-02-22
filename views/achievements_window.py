import tkinter as tk
from tkinter import ttk
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class AchievementsWindow:
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.colors = controller.colors
        self.achievements = controller.achievements.achievements
        
        
        self.window = tk.Toplevel(parent)
        self.window.title("Достижения")
        self.window.geometry("450x550")
        self.window.configure(bg=self.colors["bg"])
        self.window.resizable(False, False)
        
        
        title = tk.Label(
            self.window,
            text="🏆 Ваши достижения",
            font=("Arial", 18, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["fg"]
        )
        title.pack(pady=15)
        
        
        unlocked = self.controller.achievements.get_unlocked_count()
        total = len(self.achievements)
        
        stats_text = f"🍅 Всего помидорок: {self.controller.total_pomodoros}\n"
        stats_text += f"🏆 Разблокировано: {unlocked}/{total}"
        
        stats_label = tk.Label(
            self.window,
            text=stats_text,
            font=("Arial", 12),
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            justify="center"
        )
        stats_label.pack(pady=10)
        
        
        self.create_scrollable_area()
        
        
        close_button = tk.Button(
            self.window,
            text="Закрыть",
            command=self.window.destroy,
            bg=self.colors["button"],
            fg=self.colors["fg"],
            activebackground=self.colors["button_hover"],
            activeforeground=self.colors["fg"],
            relief="flat",
            padx=30,
            pady=8,
            cursor="hand2",
            font=("Arial", 11)
        )
        close_button.pack(pady=15)
    
    def create_scrollable_area(self):
        """Создаёт область с прокруткой для списка достижений"""
        main_frame = tk.Frame(self.window, bg=self.colors["bg"])
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(main_frame, bg=self.colors["bg"], highlightthickness=0)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
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
        
        
        self.populate_achievements(scrollable_frame)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def populate_achievements(self, parent):
        
        for ach_id, ach_data in self.achievements.items():
            
            ach_frame = tk.Frame(parent, bg=self.colors["bg"], relief="ridge", bd=2)
            ach_frame.pack(fill="x", padx=10, pady=5)
            
            
            title_frame = tk.Frame(ach_frame, bg=self.colors["bg"])
            title_frame.pack(fill="x", padx=5, pady=5)
            
            status = "✅" if ach_data["unlocked"] else "⏳"
            name_label = tk.Label(
                title_frame,
                text=f"{status}  {ach_data['name']}",
                font=("Arial", 12, "bold"),
                bg=self.colors["bg"],
                fg=self.colors["fg"],
                anchor="w"
            )
            name_label.pack(anchor="w")
            
            
            desc_label = tk.Label(
                ach_frame,
                text=ach_data["desc"],
                font=("Arial", 10),
                bg=self.colors["bg"],
                fg="#95a5a6",
                anchor="w",
                justify="left",
                wraplength=350
            )
            desc_label.pack(fill="x", padx=5, pady=2)
            
            
            if not ach_data["unlocked"] and "progress" in ach_data and "target" in ach_data:
                progress_frame = tk.Frame(ach_frame, bg=self.colors["bg"])
                progress_frame.pack(fill="x", padx=5, pady=5)
                
                progress_text = f"{ach_data['progress']}/{ach_data['target']}"
                progress_label = tk.Label(
                    progress_frame,
                    text=progress_text,
                    font=("Arial", 9),
                    bg=self.colors["bg"],
                    fg=self.colors["fg"]
                )
                progress_label.pack(side="right")
                
                progress_bar = ttk.Progressbar(
                    progress_frame,
                    length=300,
                    mode="determinate",
                    value=(ach_data['progress'] / ach_data['target']) * 100
                )
                progress_bar.pack(side="left", fill="x", expand=True)