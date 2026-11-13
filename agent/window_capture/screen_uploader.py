import os
import sys
import threading
import time

from Lib.pathlib import Path
from dotenv import load_dotenv
import httpx # type: ignore
from window_capture.screen_capture import capture_jpeg, find_game_child

BASE_DIR = getattr(sys, "frozen", False) and Path(sys.executable).resolve().parent.parent or Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(
    dotenv_path=ENV_PATH,
    override=True
)

API = os.getenv('API_BASE_URL', '').rstrip('/')
DEVICE = os.getenv('DEVICE_ID', 'my-windows-pc')
TOKEN = os.getenv('DEVICE_TOKEN', '')
SCREEN_INTERVAL = max(1, float(os.getenv('SCREEN_INTERVAL_SECONDS', '5')))
SCREEN_REGION = os.getenv('SCREEN_REGION', '').strip()


def screen_loop(stop: threading.Event, screen_watching: threading.Event):
    last_error = None

    region = (
        tuple(float(v.strip()) for v in SCREEN_REGION.split(","))
        if SCREEN_REGION else None
    )

    if region is not None and len(region) != 4:
        raise ValueError("SCREEN_REGION must contain 4 numbers")
    
    headers={'x-device-id': DEVICE, 'x-device-token': TOKEN, 'content-type': 'image/jpeg'}
    with httpx.Client(base_url=API+'/api/agent', headers=headers, timeout=15) as client:
        while not stop.is_set():
            if not screen_watching.is_set():
                threading.Event().wait(1)
                continue

            started = time.monotonic()
            try:
                hwnd = find_game_child()
                if not hwnd:
                    continue
                
                jpeg = capture_jpeg(hwnd, region=region)
                
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

def start_screen_thread():
    stop = threading.Event()
    watching = threading.Event()
    thread = threading.Thread(target=screen_loop, args=(stop, watching), name='screen-uploader', daemon=True)
    thread.start()
    
    return stop, thread, watching
