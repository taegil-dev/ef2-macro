import os
import time
import psutil
import win32gui
import win32con
import threading

PROCESS_KEYWORDS = ["play games"]
RESTART_INTERVAL = 4 * 60 * 60

restart_stop = threading.Event()


def find_game_child(game_title: str = "오늘도 환생 2", target_class: str = 'CROSVM_1') -> int:
    matches = []
    def on_window(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd) or game_title.lower() not in win32gui.GetWindowText(hwnd).lower():
            return
        def on_child(child, _):
            if win32gui.GetClassName(child) == target_class:
                matches.append(child)
        win32gui.EnumChildWindows(hwnd, on_child, None)
    win32gui.EnumWindows(on_window, None)

    if not matches:
        return None
    
    return matches[0]

def close_game(hwnd, timeout = 10.0):
    if not win32gui.IsWindow(hwnd):
        return True

    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)

    start = time.monotonic()

    while time.monotonic() - start < timeout:
        if not win32gui.IsWindow(hwnd):
            return True

        time.sleep(0.2)

    return False


def restart_game(shortcut_path):
    hwnd = find_game_child()
    if hwnd and not close_game(hwnd):
        targets = []
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                name = (proc.info["name"] or "").lower()

                if name in PROCESS_KEYWORDS:
                    print(f"종료 요청: {name} ({proc.pid})")
                    proc.terminate()
                    targets.append(proc)

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        psutil.wait_procs(targets, timeout=10)

        if find_game_child():
            print("=== 게임 종료 실패 ===")
            return False

    print("=== 게임 재실행 ===")
    os.startfile(shortcut_path)

    timeout = 30
    while timeout > 0:
        try:
            hwnd = find_game_child()
            if hwnd:
                print("=== 게임 실행 완료 ===")
                return True
        except RuntimeError:
            pass

        timeout -= 1
        time.sleep(1)

    print("=== 게임 실행 실패 ===")
    return False


def restart_loop(restart, shortcut_path):
    global last_restart

    while not restart_stop.is_set():
        if time.monotonic() - last_restart >= RESTART_INTERVAL:
            restart.set()
            restart_game(shortcut_path)
            restart.clear()
            last_restart = time.monotonic()

        restart_stop.wait(1)



def set_restart(restart, shortcut_path):
    global last_restart
    last_restart = time.monotonic()
    t = threading.Thread(target=restart_loop, args=(restart, shortcut_path,), daemon=True)
    t.start()
