import threading
import time
import httpx # type: ignore

import env_data.env_data as env
from window_capture.screen_capture import capture_jpeg, find_game_child


SCREEN_REGION = (0.335, 0.0, 0.658, 1.0)

def screen_loop(shutdown: threading.Event, stop: threading.Event, screen_watching: threading.Event):
    last_error = None
    headers={'x-device-id': env.DEVICE, 'x-device-token': env.DEVICE_TOKEN, 'content-type': 'image/jpeg'}
    with httpx.Client(base_url=env.CLIENT_URL+'/api/agent', headers=headers, timeout=15) as client:
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
                    print(f"=== 스크린샷 업로드 실패: {env.CLIENT_URL} {message} ===")

            stop.wait(max(0, env.SCREEN_INTERVAL - (time.monotonic() - started)))

def start_screen_thread(shutdown: threading.Event):
    stop = threading.Event()
    watching = threading.Event()
    thread = threading.Thread(target=screen_loop, args=(shutdown, stop, watching), name='screen-uploader', daemon=True)
    thread.start()
    
    return stop, thread, watching
