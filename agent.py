"""Windows game macro agent. Polls an authenticated command API; never exposes a port."""
from __future__ import annotations
import logging
import os
import signal
import threading
import time
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger('macro-agent')

API = os.getenv('API_BASE_URL', '').rstrip('/')
DEVICE = os.getenv('DEVICE_ID', 'my-windows-pc')
TOKEN = os.getenv('DEVICE_TOKEN', '')
TITLE = os.getenv('GAME_TITLE', '오늘도 환생 2')
CLASS = os.getenv('TARGET_CLASS', 'CROSVM_1')
POLL = max(.25, float(os.getenv('POLL_SECONDS', '1')))
HEARTBEAT = max(5, float(os.getenv('HEARTBEAT_SECONDS', '15')))
DRY_RUN = os.getenv('DRY_RUN', 'true').lower() in ('1', 'true', 'yes')
shutdown = threading.Event()
macro_stop = threading.Event()
macro_thread: threading.Thread | None = None
macro_lock = threading.Lock()
state = 'idle'
last_error = ''


def win32():
    if os.name != 'nt':
        raise RuntimeError('Actual clicking requires Windows')
    import win32api, win32con, win32gui
    return win32api, win32con, win32gui


def find_target() -> int:
    _, _, gui = win32()
    matches = []
    def top(hwnd, _):
        if gui.IsWindowVisible(hwnd) and TITLE.lower() in gui.GetWindowText(hwnd).lower():
            children = []
            def child(ch, _):
                if gui.GetClassName(ch) == CLASS:
                    children.append(ch)
            gui.EnumChildWindows(hwnd, child, None)
            matches.extend(children)
    gui.EnumWindows(top, None)
    if not matches:
        raise RuntimeError(f'Game child window {CLASS!r} not found (title contains {TITLE!r})')
    return matches[0]


def coords(hwnd: int, rx: float, ry: float) -> tuple[int, int]:
    if not (0 <= rx <= 1 and 0 <= ry <= 1):
        raise ValueError('Coordinate ratios must be between 0 and 1')
    _, _, gui = win32()
    l, t, r, b = gui.GetClientRect(hwnd)
    w, h = r-l, b-t
    if w <= 0 or h <= 0:
        raise RuntimeError('Game client area has zero size')
    return min(w-1, int(w*rx)), min(h-1, int(h*ry))


def send_click(rx: float, ry: float, duration: float = .05):
    duration = max(.01, min(.5, float(duration)))
    if DRY_RUN:
        log.info('[DRY RUN] click at %.3f %.3f', rx, ry)
        return
    api, con, gui = win32()
    hwnd = find_target()
    if gui.IsIconic(gui.GetAncestor(hwnd, con.GA_ROOT)):
        raise RuntimeError('Game is minimized')
    x, y = coords(hwnd, rx, ry)
    p = api.MAKELONG(x, y)
    gui.PostMessage(hwnd, con.WM_MOUSEMOVE, 0, p)
    gui.PostMessage(hwnd, con.WM_LBUTTONDOWN, con.MK_LBUTTON, p)
    try:
        time.sleep(duration)
    finally:
        gui.PostMessage(hwnd, con.WM_LBUTTONUP, 0, p)


def send_swipe(sx: float, sy: float, ex: float, ey: float, duration: float = .5, steps: int = 30):
    duration = max(.05, min(5., float(duration)))
    steps = max(2, min(120, int(steps)))
    if DRY_RUN:
        log.info('[DRY RUN] swipe %.3f %.3f -> %.3f %.3f', sx, sy, ex, ey)
        return
    api, con, gui = win32()
    hwnd = find_target()
    if gui.IsIconic(gui.GetAncestor(hwnd, con.GA_ROOT)):
        raise RuntimeError('Game is minimized')
    x1, y1 = coords(hwnd, sx, sy)
    x2, y2 = coords(hwnd, ex, ey)
    gui.PostMessage(hwnd, con.WM_MOUSEMOVE, 0, api.MAKELONG(x1, y1))
    gui.PostMessage(hwnd, con.WM_LBUTTONDOWN, con.MK_LBUTTON, api.MAKELONG(x1, y1))
    try:
        for i in range(1, steps+1):
            if shutdown.is_set() or macro_stop.is_set():
                break
            f = i/steps
            x, y = round(x1+(x2-x1)*f), round(y1+(y2-y1)*f)
            gui.PostMessage(hwnd, con.WM_MOUSEMOVE, con.MK_LBUTTON, api.MAKELONG(x, y))
            if macro_stop.wait(duration/steps):
                break
    finally:
        gui.PostMessage(hwnd, con.WM_LBUTTONUP, 0, api.MAKELONG(x2, y2))


def stop_macro():
    global state
    macro_stop.set()
    with macro_lock:
        thread = macro_thread
    if thread and thread.is_alive():
        thread.join(timeout=2)
    state = 'idle'


def repeat_worker(rx: float, ry: float, interval: float, duration: float):
    global state, last_error
    try:
        while not shutdown.is_set() and not macro_stop.is_set():
            send_click(rx, ry, duration)
            if macro_stop.wait(interval):
                break
    except Exception as e:
        last_error = str(e)
        log.exception('Repeating click failed')
    finally:
        state = 'idle'


def execute(command: dict[str, Any]):
    global macro_thread, state, last_error
    kind = command['type'].upper()
    p = command.get('payload') or {}
    if kind == 'STOP':
        stop_macro()
    elif kind == 'CLICK':
        stop_macro()
        send_click(float(p['x']), float(p['y']), float(p.get('duration', .05)))
    elif kind == 'SWIPE':
        stop_macro()
        send_swipe(float(p['start_x']), float(p['start_y']), float(p['end_x']), float(p['end_y']), float(p.get('duration', .5)), int(p.get('steps', 30)))
    elif kind == 'START_REPEAT':
        stop_macro()
        rx, ry = float(p['x']), float(p['y'])
        if not 0 <= rx <= 1 or not 0 <= ry <= 1:
            raise ValueError('x and y must be in [0,1]')
        interval = max(.1, min(3600, float(p.get('interval', 1))))
        duration = max(.01, min(.5, float(p.get('duration', .05))))
        macro_stop.clear()
        last_error = ''
        state = 'running'
        t = threading.Thread(target=repeat_worker, args=(rx, ry, interval, duration), daemon=True)
        with macro_lock:
            macro_thread = t
        t.start()
    else:
        raise ValueError(f'Unsupported command: {kind}')


def main():
    if not API.startswith('https://') and not API.startswith('http://localhost'):
        raise SystemExit('API_BASE_URL must use HTTPS (except localhost)')
    if not TOKEN or TOKEN.startswith('replace-'):
        raise SystemExit('Set DEVICE_TOKEN in .env')
    if not DRY_RUN:
        win32()
    headers = {'Authorization': f'Bearer {TOKEN}', 'X-Device-ID': DEVICE}
    log.info('Agent started for %s; DRY_RUN=%s', DEVICE, DRY_RUN)
    last_beat = 0.
    with httpx.Client(base_url=API+'/', headers=headers, timeout=10) as client:
        while not shutdown.is_set():
            try:
                if time.monotonic()-last_beat >= HEARTBEAT:
                    r = client.post('heartbeat', json={'status': state, 'last_error': last_error})
                    r.raise_for_status()
                    last_beat = time.monotonic()
                r = client.get('commands/next')
                r.raise_for_status()
                cmd = r.json().get('command')
                if cmd:
                    command_id = str(cmd['id'])
                    try:
                        execute(cmd)
                        result = {'status': 'done'}
                    except Exception as e:
                        log.exception('Command %s failed', command_id)
                        result = {'status': 'failed', 'error': str(e)[:500]}
                    # Backend must deduplicate commands and atomically claim them.
                    ack = client.post(f'commands/{command_id}/ack', json=result)
                    ack.raise_for_status()
            except httpx.HTTPStatusError as e:
                log.error('Backend returned %s; check API/auth', e.response.status_code)
            except (httpx.HTTPError, ValueError, KeyError) as e:
                log.warning('Connection/protocol error: %s', e)
            shutdown.wait(POLL)
    stop_macro()


if __name__ == '__main__':
    def handle_signal(_signum, _frame):
        shutdown.set()
        macro_stop.set()
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    main()
