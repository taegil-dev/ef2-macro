import os
import sys
import threading
import time

from pathlib import Path
import httpx # type: ignore
from window_capture.screen_capture import capture_jpeg, find_game_child
from dotenv import load_dotenv # type: ignore

if getattr(sys, "frozen", False):
    base_dir = Path(sys.executable).resolve().parent
else:
    base_dir = Path(__file__).resolve().parent.parent

load_dotenv(base_dir / ".env")


def screen_loop(stop: threading.Event, screen_watching: threading.Event):
    base = os.environ['API_BASE_URL'].rstrip('/')
    device_id = os.environ['DEVICE_ID']
    token = os.environ['DEVICE_TOKEN']
    title = os.environ.get('GAME_TITLE')
    target_class = os.environ.get('TARGET_CLASS')
    interval = float(os.environ.get('SCREEN_INTERVAL_SECONDS'))
    last_error = None

    region_text = os.environ.get("SCREEN_REGION").strip()

    region = (
        tuple(float(v.strip()) for v in region_text.split(","))
        if region_text else None
    )

    if region is not None and len(region) != 4:
        raise ValueError("SCREEN_REGION must contain 4 numbers")
    
    with httpx.Client(timeout=15) as client:
        while not stop.is_set():
            if not screen_watching.is_set():
                threading.Event().wait(1)
                continue

            started = time.monotonic()
            try:
                hwnd = find_game_child(title, target_class)
                if not hwnd:
                    continue
                
                jpeg = capture_jpeg(hwnd, region=region)
                
                if not screen_watching.is_set():
                    continue

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
                    print('Screen upload unavailable: %s', message)
                    last_error = message

            stop.wait(max(0, interval - (time.monotonic() - started)))

def start_screen_thread():
    stop = threading.Event()
    watching = threading.Event()
    thread = threading.Thread(target=screen_loop, args=(stop, watching), name='screen-uploader', daemon=True)
    thread.start()
    
    return stop, thread, watching
