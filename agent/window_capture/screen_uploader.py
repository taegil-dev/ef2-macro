import os
import sys
import threading
import time

from Lib.pathlib import Path
from dotenv import load_dotenv
import httpx # type: ignore
from window_capture.screen_capture import capture_jpeg, find_game_child

BASE_DIR = getattr(sys, "frozen", False) and Path(sys.executable).resolve().parent or Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(
    dotenv_path=ENV_PATH,
    override=True
)

API = os.environ['API_BASE_URL'].rstrip('/')
DEVICE = os.environ['DEVICE_ID']
TOKEN = os.environ['DEVICE_TOKEN']

SCREEN_INTERVAL = 1
SCREEN_REGION = (0.335, 0.0, 0.658, 1.0)


def screen_loop(shutdown: threading.Event, stop: threading.Event, screen_watching: threading.Event):
    last_error = None
    headers={'x-device-id': DEVICE, 'x-device-token': TOKEN, 'content-type': 'image/jpeg'}
    with httpx.Client(base_url=API+'/api/agent', headers=headers, timeout=15) as client:
        while not shutdown.is_set() and not stop.is_set():
            if not screen_watching.is_set():
                threading.Event().wait(1)
                continue

            started = time.monotonic()
            try:
                hwnd = find_game_child()
                if not hwnd:
                    continue
                
                jpeg = capture_jpeg(hwnd, region=SCREEN_REGION)
                
                if not screen_watching.is_set():
                    continue

                response = client.post("screenshot", content=jpeg)

                response.raise_for_status()
                last_error = None
            except Exception as exc:
                message = str(exc)
                if message != last_error:
                    last_error = message
                    print(f"=== 스크린샷 업로드 실패: {API} {message} ===")

            stop.wait(max(0, SCREEN_INTERVAL - (time.monotonic() - started)))

def start_screen_thread(shutdown: threading.Event):
    stop = threading.Event()
    watching = threading.Event()
    thread = threading.Thread(target=screen_loop, args=(shutdown, stop, watching), name='screen-uploader', daemon=True)
    thread.start()
    
    return stop, thread, watching
