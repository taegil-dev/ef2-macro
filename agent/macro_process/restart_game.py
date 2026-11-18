import os
import sys
import time
from dotenv import load_dotenv
import psutil
import win32api
import win32gui
import win32con
import threading
from pathlib import Path

import macro_click.macro_click as mc

PROCESS_KEYWORDS = ["play games"]
BASE_DIR = getattr(sys, "frozen", False) and Path(sys.executable).resolve().parent or Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(
    dotenv_path=ENV_PATH,
    override=True
)

GAME_TITLE = os.environ["GAME_TITLE"]
GAME_TARGET_CLASS = os.environ["GAME_TARGET_CLASS"]

restart_stop = threading.Event()

def alt_tab():
    win32api.keybd_event(
        win32con.VK_MENU, 0, 0, 0
    )

    win32api.keybd_event(
        win32con.VK_TAB, 0, 0, 0
    )

    win32api.keybd_event(
        win32con.VK_TAB, 0,
        win32con.KEYEVENTF_KEYUP, 0
    )

    win32api.keybd_event(
        win32con.VK_MENU, 0,
        win32con.KEYEVENTF_KEYUP, 0
    )

def restart_init():
    # 첫 화면 제거
    restart_stop.wait(10)
    mc.click(restart_stop, 0.5, 0.05, show_marker=False)

    # 오프라인 등반 창 뜨면 제거
    restart_stop.wait(1)
    mc.click(restart_stop, 0.47, 0.55, show_marker=False)

    # 영웅 탭
    restart_stop.wait(0.2)
    mc.click(restart_stop, 0.425, 0.97, show_marker=False)

    # 영웅 프리셋 창 활성화
    restart_stop.wait(0.2)
    mc.click(restart_stop, 0.52, 0.6, show_marker=False)
    
    restart_stop.wait(0.5)


def find_game_child() -> int:
    matches = []
    def on_window(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd) or GAME_TITLE.lower() not in win32gui.GetWindowText(hwnd).lower():
            return
        def on_child(child, _):
            if win32gui.GetClassName(child) == GAME_TARGET_CLASS:
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

        restart_stop.wait(0.2)

    return False


def restart_game(shortcut_path: Path):
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
                print("=== 게임 실행 완료 ===\n")
                return True
        except RuntimeError:
            pass

        timeout -= 1
        restart_stop.wait(1)

    print("=== 게임 실행 실패 ===")
    return False



def restart_loop(shutdown: threading.Event, restart: threading.Event, shortcut_path: Path, restart_time: int):
    global last_restart

    print("")
    while not shutdown.is_set() and not restart_stop.is_set():
        if time.monotonic() - last_restart >= restart_time:
            # 재시작 이벤트를 발생시키고 매크로가 멈출 때까지 대기
            restart.set()
            restart_stop.wait(5)

            print("=== 게임 종료 시작 ===")
            result = restart_game(shortcut_path)
            if not result:
                continue

            alt_tab()
            restart_stop.wait(1)
            alt_tab()
            restart_stop.wait(1)
            alt_tab()
            restart_stop.wait(1)
            alt_tab()
            restart_stop.wait(1)
            restart_init()
            restart.clear()
            last_restart = time.monotonic()

        restart_stop.wait(1)




def set_restart(shutdown: threading.Event, restart: threading.Event, shortcut_path: Path, restart_time):
    global last_restart
    last_restart = time.monotonic()
    t = threading.Thread(target=restart_loop, args=(shutdown, restart, shortcut_path, restart_time), daemon=True)
    t.start()


def stop_restart():
    restart_stop.set()
