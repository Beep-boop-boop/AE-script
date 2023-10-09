import psutil
import keyboard
import pyautogui
import time
import os
import sys

cpu_threshold = 60
afterfx_pid = None
rendering_start_time = None

timeout_cpu = 30
timeout_shutdown = 60

stop_combination = "ctrl+a+s"

def is_afterfx_running():
    global afterfx_pid
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        if proc.info['name'] == 'AfterFX.exe':
            afterfx_pid = proc.info['pid']
            return True
    return False

def consecutive30():
    consecutive_seconds = 0
    start_time = time.time()

    while consecutive_seconds < timeout_cpu:
        cpu_percent = int(psutil.Process(afterfx_pid).cpu_percent(interval=1))
        
        current_time = time.time()
        if current_time - start_time > 5:
            print(f"{cpu_percent} < {cpu_threshold} for {consecutive_seconds} seconds")
            pyautogui.move(2, 2)
            start_time = current_time

        if cpu_percent < cpu_threshold: 
            consecutive_seconds +=1
        else:
            consecutive_seconds = 0

    return consecutive_seconds == timeout_cpu

def main():
    global rendering_start_time
    global cpu_percent

    while True:
        if is_afterfx_running():
            cpu_percent = psutil.Process(afterfx_pid).cpu_percent(interval=1)
            print(cpu_percent)

            if cpu_percent > cpu_threshold:
                rendering_start_time = time.time()
            
                print("Keeping the PC awake")
                pyautogui.move(2, 2)

            elif cpu_percent < cpu_threshold and consecutive30():
                print(f"Preparing for shutdown, press {stop_combination} to exit")
                shutdown_timer = timeout_shutdown

                while not keyboard.is_pressed(stop_combination) and shutdown_timer > 0:
                    print(f"Shutting down in {shutdown_timer} seconds...")
                    time.sleep(1)
                    shutdown_timer -= 1

                if keyboard.is_pressed(stop_combination):
                    print("Process terminated by user")
                    sys.exit()

                print("Shutting down...")
                os.system('shutdown /s /t 1')

        else:
            print("No process found")

        time.sleep(5)

if __name__ == "__main__":
    main()
