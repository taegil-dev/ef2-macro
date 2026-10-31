import threading
import time
import macro_click.show_click_marker as click_marker


def win32():
    import win32api, win32con, win32gui # type: ignore
    return win32api, win32con, win32gui

__all__ = ["click", "swipe"]


def find_target(game_title: str = "오늘도 환생 2", target_class: str = 'CROSVM_1') -> int:
    _, _, gui = win32()

    matches = []
    def top(hwnd, _):
        if gui.IsWindowVisible(hwnd) and game_title.lower() in gui.GetWindowText(hwnd).lower():

            children = []
            def child(ch, _):
                if gui.GetClassName(ch) == target_class:
                    children.append(ch)

            gui.EnumChildWindows(hwnd, child, None)
            matches.extend(children)

    gui.EnumWindows(top, None)

    if not matches:
        raise RuntimeError(f'Game child window {target_class!r} not found (title contains {game_title!r})')
    
    return matches[0]

def coords(hwnd: int, rx: float, ry: float) -> tuple[int, int]:
    if not (0 <= rx <= 1 and 0 <= ry <= 1):
        raise ValueError('Coordinate ratios must be between 0 and 1')
    
    _, _, gui = win32()
    left, top, right, bottom = gui.GetClientRect(hwnd)

    width = right - left
    height = bottom - top

    x = int(width * rx)
    y = int(height * ry)

    if width <= 0 or height <= 0:
        raise RuntimeError('Game client area has zero size')
    return x, y

def click(rx: float, ry: float, duration: float = .05, show_marker: bool = True):
    api, con, gui = win32()
    hwnd = find_target()

    if gui.IsIconic(gui.GetAncestor(hwnd, con.GA_ROOT)):
        raise RuntimeError('Game is minimized')

    x, y = coords(hwnd, rx, ry)

    gui.PostMessage(
        hwnd, 
        con.WM_MOUSEMOVE, 
        0, 
        api.MAKELONG(x, y)
    )

    gui.PostMessage(
        hwnd, 
        con.WM_LBUTTONDOWN, 
        con.MK_LBUTTON, 
        api.MAKELONG(x, y)
    )

    if show_marker:
        click_marker.show_click_marker(hwnd, x, y)

    try:
        time.sleep(duration)
    finally:
        gui.PostMessage(
            hwnd, 
            con.WM_LBUTTONUP, 
            0, 
            api.MAKELONG(x, y)
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
    api, con, gui = win32()
    hwnd = find_target()

    if gui.IsIconic(gui.GetAncestor(hwnd, con.GA_ROOT)):
        raise RuntimeError('Game is minimized')
    
    x1, y1 = coords(hwnd, sx, sy)
    x2, y2 = coords(hwnd, ex, ey)

    gui.PostMessage(
        hwnd, 
        con.WM_MOUSEMOVE, 
        0, 
        api.MAKELONG(x1, y1)
    )

    gui.PostMessage(
        hwnd, 
        con.WM_LBUTTONDOWN, 
        con.MK_LBUTTON, 
        api.MAKELONG(x1, y1)
    )
    if show_marker:
        click_marker.show_click_marker(hwnd, x1, y1)

    try:
        for i in range(1, steps + 1):
            if shutdown.is_set() or macro_stop.is_set():
                break
            threading.Event().wait(duration / steps)

            progress = i / steps
            x, y = int(x1 + (x2 - x1) * progress), int(y1 + (y2 - y1) * progress)

            gui.PostMessage(
                hwnd, 
                con.WM_MOUSEMOVE, 
                con.MK_LBUTTON, 
                api.MAKELONG(x, y)
            )

            if show_marker:
                click_marker.show_click_marker(hwnd, x, y)

    finally:
        gui.PostMessage(
            hwnd, 
            con.WM_LBUTTONUP, 
            0, 
            api.MAKELONG(x2, y2)
        )