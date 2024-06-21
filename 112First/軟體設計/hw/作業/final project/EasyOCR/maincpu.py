# import psutil

# # 獲取 CPU 的使用百分比
# cpu_usage = psutil.cpu_percent(interval=1)
# print(f"CPU Usage: {cpu_usage}%")

# # 獲取每個 CPU 核心的使用情況
# cpu_per_core = psutil.cpu_percent(interval=1, percpu=True)
# for i, percentage in enumerate(cpu_per_core):
#     print(f"Core {i}: {percentage}%")

# # 獲取更多系統信息（如記憶體使用情況）
# memory = psutil.virtual_memory()
# print(f"Memory Usage: {memory.percent}%")

# for proc in psutil.process_iter(['pid', 'name']):
#     print(proc.info)

# 替換這裡的 PID
# pid = 1236  # 請將此處替換為您要監控的進程的 PID

# try:
#     p = psutil.Process(pid)
#     cpu_usage = p.cpu_percent(interval=1)
#     print(f"CPU Usage of process {pid}: {cpu_usage}%")
# except psutil.NoSuchProcess:
#     print(f"No process found with PID {pid}")

import os
import time
import psutil

def monitor_process(pid):
    try:
        process = psutil.Process(pid)
    except psutil.NoSuchProcess:
        print(f"No process found with PID {pid}")
        return

    while True:
        try:
            # 獲取進程的 CPU 使用率
            cpu_usage = process.cpu_percent(interval=1)
            print(f"CPU Usage of process {pid}: {cpu_usage}%")

            # 獲取進程使用的 CPU 核心
            cpu_affinity = process.cpu_affinity()
            print(f"Process running on cores: {cpu_affinity}")

            time.sleep(2)  # 每 2 秒更新一次
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            print(f"Process {pid} terminated or access denied.")
            break

if __name__ == "__main__":
    pid = 1236  # 替換為您要監控的進程 PID
    monitor_process(pid)