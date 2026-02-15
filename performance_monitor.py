import psutil
import time

class PerformanceMonitor:
    def __init__(self):
        self.process = psutil.Process()
        self.last_time = time.time()
        try:
            self.last_cpu_times = self.process.cpu_times()
        except:
            self.last_cpu_times = None

    def get_latest_stats(self):
        # Calculate CPU usage since last call without blocking or threading
        current_time = time.time()
        try:
            current_cpu_times = self.process.cpu_times()
            memory_info = self.process.memory_info()
        except:
            return {"cpu": 0, "memory": 0}
        
        delta_time = current_time - self.last_time
        cpu_percent = 0.0
        
        if self.last_cpu_times and delta_time > 0.1:
            # Calculate CPU percentage over the interval manually
            user_delta = current_cpu_times.user - self.last_cpu_times.user
            sys_delta = current_cpu_times.system - self.last_cpu_times.system
            cpu_percent = ((user_delta + sys_delta) / delta_time) * 100
            
            # Clamp to 100% just in case
            cpu_percent = min(max(cpu_percent, 0.0), 100.0)

        self.last_time = current_time
        self.last_cpu_times = current_cpu_times
        memory_usage_mb = memory_info.rss / (1024 * 1024)
        
        return {
            "cpu": round(cpu_percent, 1),
            "memory": int(memory_usage_mb)
        }

    def start(self):
        # No thread needed to avoid GIL issues on Python 3.14
        pass

    def stop(self):
        pass
