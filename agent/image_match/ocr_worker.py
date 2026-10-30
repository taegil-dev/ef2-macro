"""Run OCR in a background thread without blocking macro command polling."""
import logging
import os
from pathlib import Path
import re
import threading
import time
from image_match.number_ocr import NumberReader
from window_capture.screen_capture import capture_jpeg, find_game_child 
from dotenv import load_dotenv # type: ignore

current_file = Path(__file__).resolve()
parent_directory = current_file.parent.parent
env_path = parent_directory / '.env'

load_dotenv(dotenv_path=env_path)

log = logging.getLogger('number_ocr')

def parse_game_value(text: str):
    match = re.fullmatch(r"(\d+)([a-zA-Z]+)", text.strip())

    if not match:
        return None

    return {
        "value": int(match.group(1)),
        "suffix": match.group(2).lower()
    }

def run_ocr_loop(stop: threading.Event):
    region = tuple(float(v.strip()) for v in os.getenv('OCR_REGION', '0.70,0.05,0.90,0.12').split(','))
    if len(region) != 4:
        raise ValueError('OCR_REGION requires 4 numbers')
    
    reader = NumberReader(region, float(os.getenv('OCR_MIN_CONFIDENCE', '0.5')))
    interval = max(0.2, float(os.getenv('OCR_INTERVAL_SECONDS', '1')))
    title = os.getenv('GAME_TITLE', '오늘도 환생 2')
    target_class = os.getenv('TARGET_CLASS', 'CROSVM_1')
    previous = object()
    previous_error = None

    while not stop.is_set():
        started = time.monotonic()
        try:
            hwnd = find_game_child(title, target_class)
            frame = capture_jpeg(hwnd, quality=90, max_width=1920)
            result = reader.read(frame)
            if result.value != previous:
                log.info('OCR number=%s raw=%r confidence=%s', result.value, result.raw_text,
                         f'{result.confidence:.2f}' if result.confidence is not None else 'N/A')
                previous = result.value

            previous_error = None
        except Exception as exc:
            if str(exc) != previous_error:
                log.warning('OCR unavailable: %s', exc)
                previous_error = str(exc)

        stop.wait(max(0, interval - (time.monotonic() - started)))


def start_ocr_thread():
    stop = threading.Event()
    thread = threading.Thread(target=run_ocr_loop, args=(stop,), daemon=True, name='number-ocr')
    thread.start()

    return stop, thread

# run_ocr_loop(threading.Event())