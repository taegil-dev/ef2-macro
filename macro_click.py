from Lib import importlib
win32api = importlib.import_module('win32api')
win32con = importlib.import_module('win32con')
win32gui = importlib.import_module('win32gui')
import time
import show_click_marker as click_marker

__all__ = ["click"]

CLICK_DURATION = 0.05

def click(hwnd, x_ratio, y_ratio, show_marker=False):
    if not win32gui.IsWindow(hwnd):
        return False

    left, top, right, bottom = win32gui.GetClientRect(hwnd)

    width = right - left
    height = bottom - top

    if width <= 0 or height <= 0:
        return False

    x = min(width - 1, max(0, int(width * x_ratio)))
    y = min(height - 1, max(0, int(height * y_ratio)))

    lparam = win32api.MAKELONG(x, y)
    if show_marker:
        click_marker.show_click_marker(hwnd, x, y)

    print(f"Clicking at ({x}, {y}) in window {hwnd}")

    win32gui.PostMessage(
        hwnd,
        win32con.WM_MOUSEMOVE,
        0,
        lparam
    )

    win32gui.PostMessage(
        hwnd,
        win32con.WM_LBUTTONDOWN,
        win32con.MK_LBUTTON,
        lparam
    )

    time.sleep(CLICK_DURATION)

    win32gui.PostMessage(
        hwnd,
        win32con.WM_LBUTTONUP,
        0,
        lparam
    )

    return True

def swipe(
    hwnd,
    start_x_ratio,
    start_y_ratio,
    end_x_ratio,
    end_y_ratio,
    duration=0.5,
    steps=30,
    show_marker=False
):
    if not win32gui.IsWindow(hwnd):
        return False

    left, top, right, bottom = win32gui.GetClientRect(hwnd)

    width = right - left
    height = bottom - top

    if width <= 0 or height <= 0:
        return False

    start_x = int(width * start_x_ratio)
    start_y = int(height * start_y_ratio)

    end_x = int(width * end_x_ratio)
    end_y = int(height * end_y_ratio)

    if show_marker:
        click_marker.show_click_marker(hwnd, start_x, start_y)

    def make_lparam(x, y):
        return win32api.MAKELONG(x, y)

    win32gui.PostMessage(
        hwnd,
        win32con.WM_MOUSEMOVE,
        0,
        make_lparam(start_x, start_y)
    )

    win32gui.PostMessage(
        hwnd,
        win32con.WM_LBUTTONDOWN,
        win32con.MK_LBUTTON,
        make_lparam(start_x, start_y)
    )

    for i in range(1, steps + 1):
        progress = i / steps

        x = int(start_x + (end_x - start_x) * progress)
        y = int(start_y + (end_y - start_y) * progress)

        win32gui.PostMessage(
            hwnd,
            win32con.WM_MOUSEMOVE,
            win32con.MK_LBUTTON,
            make_lparam(x, y)
        )

        if show_marker:
            click_marker.show_click_marker(hwnd, x, y)

        time.sleep(duration / steps)

    win32gui.PostMessage(
        hwnd,
        win32con.WM_LBUTTONUP,
        0,
        make_lparam(end_x, end_y)
    )

    return True