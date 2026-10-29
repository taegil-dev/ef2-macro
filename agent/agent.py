"""Windows game macro agent. Polls an authenticated command API; never exposes a port."""
from __future__ import annotations
import logging
import os
import signal
import threading
import time
from typing import Any
from Lib.pathlib import Path

import httpx # type: ignore
logging.getLogger("httpx").setLevel(logging.WARNING)

from dotenv import load_dotenv # type: ignore

import macro_click as mc

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(
    dotenv_path=ENV_PATH,
    override=True
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger('macro-agent')

API = os.getenv('API_BASE_URL', '').rstrip('/')
DEVICE = os.getenv('DEVICE_ID', 'my-windows-pc')
TOKEN = os.getenv('DEVICE_TOKEN', '')
POLL = max(.25, float(os.getenv('POLL_SECONDS', '1')))
HEARTBEAT = max(5, float(os.getenv('HEARTBEAT_SECONDS', '15')))
shutdown = threading.Event()
macro_stop = threading.Event()
macro_thread: threading.Thread | None = None
macro_lock = threading.Lock()
state = 'idle'
last_error = ''


def win32():
    import win32api, win32con, win32gui # type: ignore
    return win32api, win32con, win32gui


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
            mc.click(rx, ry, duration)
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
        log.info('Executing CLICK command: %s', p)
        stop_macro()
        mc.click(float(p['x']), float(p['y']), float(p.get('duration', .05)))

    elif kind == 'SWIPE':
        stop_macro()
        mc.swipe(
            float(p['start_x']), 
            float(p['start_y']), 
            float(p['end_x']), 
            float(p['end_y']), 
            float(p.get('duration', .5)), 
            int(p.get('steps', 30))
        )

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
    
    win32()
    headers = {'Authorization': f'Bearer {TOKEN}', 'X-Device-ID': DEVICE}
    log.info('Agent started for %s', DEVICE)
    last_beat = 0.

    with httpx.Client(base_url=API+'/', headers=headers, timeout=10) as client:
        while not shutdown.is_set():
            try:
                if time.monotonic() - last_beat >= HEARTBEAT:
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
