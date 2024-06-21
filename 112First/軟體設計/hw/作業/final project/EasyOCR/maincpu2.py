import time
import psutil

def monitor_process(pid):
    try:
        process = psutil.Process(pid)
    except psutil.NoSuchProcess:
        print(f"No process found with PID {pid}")
        return

    num_cores = psutil.cpu_count()
    print(f"Number of CPU cores: {num_cores}")

    while True:
        try:
            # 獲取進程的 CPU 使用率
            cpu_usage_percent = process.cpu_percent(interval=1) / num_cores
            print(f"Total CPU Usage of process {pid}: {cpu_usage_percent}%")

            # 估算每個核心的使用率
            for i in range(num_cores):
                # 這裡只是一個近似估算，並不精確
                print(f"Estimated usage on core {i}: {cpu_usage_percent}%")

            time.sleep(2)  # 每 2 秒更新一次
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            print(f"Process {pid} terminated or access denied.")
            break

if __name__ == "__main__":
    pid = 1236  # 替換為您要監控的進程 PID
    monitor_process(pid)