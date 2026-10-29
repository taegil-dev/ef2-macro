import ctypes
from ctypes import wintypes
import io
import win32con, win32gui, win32ui # type: ignore
from PIL import Image, ImageStat # type: ignore

user32 = ctypes.windll.user32
user32.PrintWindow.argtypes = [wintypes.HWND, wintypes.HDC, wintypes.UINT]
user32.PrintWindow.restype = wintypes.BOOL


def find_game_child(game_title: str, target_class: str = 'CROSVM_1') -> int:
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
        raise RuntimeError(f'Game child window not found: {game_title} / {target_class}')
    return matches[0]


def capture_jpeg(hwnd: int, quality: int = 65, max_width: int = 1280) -> bytes:
    if win32gui.IsIconic(win32gui.GetAncestor(hwnd, win32con.GA_ROOT)):
        raise RuntimeError('Game is minimized; background capture not supported')
    
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    width, height = right - left, bottom - top
    if width < 10 or height < 10:
        raise RuntimeError('Invalid capture dimensions')
    
    src_dc = win32gui.GetWindowDC(hwnd)
    if not src_dc:
        raise RuntimeError('GetWindowDC failed')
    
    dc = win32ui.CreateDCFromHandle(src_dc)
    mem = dc.CreateCompatibleDC()
    bmp = win32ui.CreateBitmap()
    try:
        bmp.CreateCompatibleBitmap(dc, width, height)
        mem.SelectObject(bmp)

        # PW_CLIENTONLY (1) + PW_RENDERFULLCONTENT (2)
        ok = user32.PrintWindow(hwnd, mem.GetSafeHdc(), 3)
        if not ok:
            raise RuntimeError('PrintWindow failed; try Windows Graphics Capture')
        
        info = bmp.GetInfo()
        data = bmp.GetBitmapBits(True)
        image = Image.frombuffer('RGB', (info['bmWidth'], info['bmHeight']), data, 'raw', 'BGRX', 0, 1).copy()
    finally:
        win32gui.DeleteObject(bmp.GetHandle())
        mem.DeleteDC()
        dc.DeleteDC()
        win32gui.ReleaseDC(hwnd, src_dc)

    # A black frame can be legitimate; flag it so it is not mistaken for successful rendering.
    mean = ImageStat.Stat(image.convert('L')).mean[0]
    if mean < 2:
        raise RuntimeError('Captured frame is nearly black; PrintWindow may not support this game')
    
    if image.width > max_width:
        image.thumbnail((max_width, 10000), Image.Resampling.LANCZOS)

    out = io.BytesIO()
    image.save(out, 'JPEG', quality=quality, optimize=True)
    
    return out.getvalue()
