import time

class Timer:
    def __init__(self):
        self.start_time = 0.0
        self.paused_time = time.time()
        self.is_paused = True
    
    def start(self):
        if self.is_paused:
            self.start_time += time.time() - self.paused_time
            self.is_paused = False
    
    def pause(self): 
        if not self.is_paused:
            self.paused_time = time.time()
            self.is_paused = True
    
    def reset(self):
        self.start_time = 0.0
        self.paused_time = time.time()
        self.is_paused = True
    
    def time(self) -> float:
        if self.is_paused:
            return self.paused_time - self.start_time
        else:
            return time.time() - self.start_time