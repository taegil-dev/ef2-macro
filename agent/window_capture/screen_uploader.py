import logging
import os
import threading
import time

from Lib.pathlib import Path
import httpx # type: ignore
from window_capture.screen_capture import capture_jpeg, find_game_child
from dotenv import load_dotenv # type: ignore

current_file = Path(__file__).resolve()
parent_directory = current_file.parent.parent
env_path = parent_directory / '.env'

load_dotenv(dotenv_path=env_path)

log = logging.getLogger('screen_uploader')

def screen_loop(stop: threading.Event):
    base = os.environ['API_BASE_URL'].rstrip('/')
    device_id = os.environ['DEVICE_ID']
    token = os.environ['DEVICE_TOKEN']
    title = os.environ.get('GAME_TITLE')
    target_class = os.environ.get('TARGET_CLASS')
    interval = float(os.environ.get('SCREEN_INTERVAL_SECONDS'))
    last_error = None
    with httpx.Client(timeout=15) as client:
        while not stop.is_set():
            started = time.monotonic()
            try:
                hwnd = find_game_child(title, target_class)
                jpeg = capture_jpeg(hwnd)
                response = client.post(
                    f'{base}/screenshot',
                    headers={'x-device-id': device_id, 'x-device-token': token, 'content-type': 'image/jpeg'},
                    content=jpeg,
                )
                response.raise_for_status()
                last_error = None
            except Exception as exc:
                message = str(exc)
                if message != last_error:
                    log.warning('Screen upload unavailable: %s', message)
                    last_error = message
            stop.wait(max(0, interval - (time.monotonic() - started)))

def start_screen_thread():
    stop = threading.Event()
    thread = threading.Thread(target=screen_loop, args=(stop,), name='screen-uploader', daemon=True)
    thread.start()
    return stop, thread
