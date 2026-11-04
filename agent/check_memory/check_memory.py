import ctypes
import os
import psutil
import threading
import time

process = psutil.Process(os.getpid())

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

GR_GDIOBJECTS = 0
GR_USEROBJECTS = 1

def get_gui_resources():
    process = kernel32.GetCurrentProcess()

    gdi = user32.GetGuiResources(process, GR_GDIOBJECTS)
    user = user32.GetGuiResources(process, GR_USEROBJECTS)

    return gdi, user

def monitor_memory(shutdown: threading.Event):
    while not shutdown.is_set():
        memory = process.memory_info().rss / 1024 / 1024
        gdi, user = get_gui_resources()

        print(
            f"[MEMORY] "
            f"RSS: {memory:.2f} MB | "
            f"GDI: {gdi} | "
            f"USER: {user} | "
            f"Threads: {threading.active_count()}"
        )

        shutdown.wait(60)