import time
import threading

class TimerModel:
    def __init__(self):
        self.work_time = 25 * 60
        self.short_break = 5 * 60
        self.long_break = 15 * 60
        self.cycles = 0
        self.max_cycles = 4
        self.is_running = False
        self.is_paused = False
        self.current_time = self.work_time
        self.current_phase = "work"
        self.timer_thread = None
        self.next_second = 0
        
        
        self.on_update = None
        self.on_phase_change = None
    
    def set_times(self, work, short, long):
        """Устанавливает время работы и отдыха"""
        self.work_time = work * 60
        self.short_break = short * 60
        self.long_break = long * 60
        if not self.is_running:
            self.current_time = self.work_time
    
    def start(self):
        """Запускает таймер"""
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            self.timer_thread = threading.Thread(target=self._run, daemon=True)
            self.timer_thread.start()
    
    def _run(self):
        """Основной цикл таймера (в отдельном потоке)"""
        self.next_second = time.time() + 1
        while self.is_running and self.current_time > 0:
            if not self.is_paused:
                now = time.time()
                if now >= self.next_second:
                    self.current_time -= 1
                    if self.on_update:
                        self.on_update()
                    self.next_second += 1
                time.sleep(0.05)
            else:
                time.sleep(0.1)
                self.next_second = time.time() + 1
        
        if self.is_running and self.current_time <= 0:
            self.is_running = False
            self._switch_phase()
    
    def pause(self):
        """Ставит на паузу"""
        if self.is_running:
            if not self.is_paused:
                self.is_paused = True
                return "paused"
            else:
                self.is_paused = False
                self.next_second = time.time() + 1
                return "resumed"
        return None
    
    def reset(self):
        """Сбрасывает таймер"""
        self.is_running = False
        self.is_paused = False
        self.current_time = self.work_time
        self.current_phase = "work"
        self.cycles = 0
        if self.on_update:
            self.on_update()
    
    def _switch_phase(self):
        """Переключает между работой и отдыхом"""
        if self.current_phase == "work":
            self.cycles += 1
            
            if self.cycles % self.max_cycles == 0:
                self.current_phase = "long_break"
                self.current_time = self.long_break
            else:
                self.current_phase = "short_break"
                self.current_time = self.short_break
        else:
            self.current_phase = "work"
            self.current_time = self.work_time
        
        if self.on_phase_change:
            self.on_phase_change(self.current_phase)
        
        self.start()
    
    def get_time_str(self):
        """Возвращает текущее время в формате ММ:СС"""
        minutes = int(self.current_time // 60)
        seconds = int(self.current_time % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_progress(self):
        """Возвращает прогресс в процентах"""
        if self.current_phase == "work":
            total = self.work_time
        elif self.current_phase == "short_break":
            total = self.short_break
        else:
            total = self.long_break
        
        if total > 0:
            return ((total - self.current_time) / total) * 100
        return 0