import time
from screenlib import screen

def read_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            raw_temp = int(f.read().strip())
            return raw_temp / 1000.0  # Convert to Celsius

    except FileNotFoundError:
        print("Error: The file /sys/class/thermal/thermal_zone0/temp was not found.")
        print("This file may not exist on your system or you may not have the necessary permissions.")
    except Exception as e:
        print(f"An error occurred: {e}")


def read_cpu_load_percent(interval=0.4):
    # Calcula %CPU usando /proc/stat
    def read_times():
        with open("/proc/stat","r") as f:
            for line in f:
                if line.startswith("cpu "):
                    parts = line.split()
                    vals = list(map(int, parts[1:]))
                    # user,nice,system,idle,iowait,irq,softirq,steal,guest,guest_nice
                    # algunos kernels traen 7-10 campos; maneja de forma segura
                    while len(vals) < 7: 
                        vals.append(0)

                    user, nice, system, idle, iowait, irq, softirq = vals[:7]
                    idle_all = idle + iowait
                    non_idle = user + nice + system + irq + softirq
                    total = idle_all + non_idle

                    return total, idle_all
        return None, None

    t1, i1 = read_times()
    time.sleep(interval)
    t2, i2 = read_times()

    if None in (t1, i1, t2, i2): 
        return None
    
    dt, di = (t2 - t1), (i2 - i1)
    if dt <= 0: 
        return None

    usage = 100.0 * (1.0 - (di / dt))
    return max(0.0, min(100.0, usage))

def main():
    screen.initialize()

    screen.draw_text("ZERO VOLTS", 1)
    while True:

        # load = read_cpu_load_percent(interval=0.3)
        # screen.draw_text(f'CPU load: {load:4.0f}', 2)

        temp = read_cpu_temp()
        screen.draw_text(f'Temp: {temp:.1f} C', 3)

        time.sleep(1)


if __name__ == "__main__":
    main()