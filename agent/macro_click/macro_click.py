import threading
import time
import macro_click.show_click_marker as click_marker
import win32api, win32con, win32gui # type: ignore

__all__ = ["click", "swipe"]


def find_target(game_title: str = "오늘도 환생 2", target_class: str = 'CROSVM_1') -> int:
    matches = []
    def top(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and game_title.lower() in win32gui.GetWindowText(hwnd).lower():

            children = []
            def child(ch, _):
                if win32gui.GetClassName(ch) == target_class:
                    children.append(ch)

            win32gui.EnumChildWindows(hwnd, child, None)
            matches.extend(children)

    win32gui.EnumWindows(top, None)

    if not matches:
        raise RuntimeError(f'Game child window {target_class!r} not found (title contains {game_title!r})')
    
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
    hwnd = find_target()

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
    hwnd = find_target()

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