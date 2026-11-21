import threading
import win32api, win32con, win32gui # type: ignore

import env_data.env_data as env
import macro_click.show_click_marker as click_marker


__all__ = ["click", "swipe"]


def find_game_child() -> int:
    matches = []
    def on_window(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd) or env.GAME_TITLE.lower() not in win32gui.GetWindowText(hwnd).lower():
            return
        def on_child(child, _):
            if win32gui.GetClassName(child) == env.GAME_TARGET_CLASS:
                matches.append(child)
        win32gui.EnumChildWindows(hwnd, on_child, None)
    win32gui.EnumWindows(on_window, None)

    if not matches:
        raise RuntimeError(f'Game child window {env.GAME_TARGET_CLASS!r} not found (title contains {env.GAME_TITLE!r})')
    
    return matches[0]

def coords(hwnd: int, rx: float, ry: float) -> tuple[int, int]:
    if not (0 <= rx <= 1 and 0 <= ry <= 1):
        raise ValueError('Coordinate ratios must be between 0 and 1')
    
    left, top, right, bottom = win32gui.GetClientRect(hwnd)

    width = right - left
    height = bottom - top

    x = int(width * rx)
    y = int(height * ry)

    if width <= 0 or height <= 0:
        raise RuntimeError('Game client area has zero size')
    return x, y

def click(thread_stop, rx: float, ry: float, duration: float = .05, show_marker: bool = True):
    hwnd = find_game_child()

    if win32gui.IsIconic(win32gui.GetAncestor(hwnd, win32con.GA_ROOT)):
        raise RuntimeError('Game is minimized')

    x, y = coords(hwnd, rx, ry)

    win32gui.PostMessage(
        hwnd, 
        win32con.WM_MOUSEMOVE, 
        0, 
        win32api.MAKELONG(x, y)
    )

    win32gui.PostMessage(
        hwnd, 
        win32con.WM_LBUTTONDOWN, 
        win32con.MK_LBUTTON, 
        win32api.MAKELONG(x, y)
    )

    if show_marker:
        click_marker.show_click_marker(hwnd, x, y)

    try:
        thread_stop.wait(duration)
    finally:
        win32gui.PostMessage(
            hwnd, 
            win32con.WM_LBUTTONUP, 
            0, 
            win32api.MAKELONG(x, y)
        )

def swipe(
        shutdown: threading.Event,
        macro_stop: threading.Event,
        sx: float, 
        sy: float, 
        ex: float, 
        ey: float, 
        duration: float = .5, 
        steps: int = 30, 
        show_marker: bool = True
    ):
    hwnd = find_game_child()

    if win32gui.IsIconic(win32gui.GetAncestor(hwnd, win32con.GA_ROOT)):
        raise RuntimeError('Game is minimized')
    
    x1, y1 = coords(hwnd, sx, sy)
    x2, y2 = coords(hwnd, ex, ey)

    win32gui.PostMessage(
        hwnd, 
        win32con.WM_MOUSEMOVE, 
        0, 
        win32api.MAKELONG(x1, y1)
    )

    win32gui.PostMessage(
        hwnd, 
        win32con.WM_LBUTTONDOWN, 
        win32con.MK_LBUTTON, 
        win32api.MAKELONG(x1, y1)
    )
    if show_marker:
        click_marker.show_click_marker(hwnd, x1, y1)

    try:
        for i in range(1, steps + 1):
            if shutdown.is_set() or macro_stop.is_set():
                break
            macro_stop.wait(duration / steps)

            progress = i / steps
            x, y = int(x1 + (x2 - x1) * progress), int(y1 + (y2 - y1) * progress)

            win32gui.PostMessage(
                hwnd, 
                win32con.WM_MOUSEMOVE, 
                win32con.MK_LBUTTON, 
                win32api.MAKELONG(x, y)
            )

            if show_marker:
                click_marker.show_click_marker(hwnd, x, y)

    finally:
        win32gui.PostMessage(
            hwnd, 
            win32con.WM_LBUTTONUP, 
            0, 
            win32api.MAKELONG(x2, y2)
        )