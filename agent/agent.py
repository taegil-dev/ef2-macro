"""Windows game macro agent. Polls an authenticated command API; never exposes a port."""
from __future__ import annotations
import importlib
import logging
import os
import signal
import sys
import threading
import time
from typing import Any
from Lib.pathlib import Path
import datetime

import httpx # type: ignore
logging.getLogger("httpx").setLevel(logging.WARNING)

from dotenv import load_dotenv # type: ignore

import macro_click.macro_click as mc
from window_capture.screen_uploader import start_screen_thread
import image_match.image_match as im


BASE_DIR = getattr(sys, "frozen", False) and Path(sys.executable).resolve().parent or Path(__file__).resolve().parent
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
SEQUENCE_DELAY = 0.2
MACRO_DELAY = 2
shutdown = threading.Event()
macro_stop = threading.Event()
macro_thread: threading.Thread | None = None
macro_lock = threading.Lock()
state = 'idle'
last_error = ''

image_matcher = im.ImageMatcher()
image_matcher.load_template("rebirth", BASE_DIR / "image_match" / "templates" / "rebirth.jpg")
image_matcher.load_template("continue", BASE_DIR / "image_match" / "templates" / "continue.jpg")

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

def ignore_condition(
        ignore: dict[str, Any], 
        WAVE_POS: tuple[float, float, float, float], 
        GOLD_POS: tuple[float, float, float, float]
    ) -> bool:
    if not ignore:
        return False
    
    if ignore['condition'] == 'wave':
        floor = im.check_floor(WAVE_POS)
        if floor is None:
            return False
        
        if(ignore['type'] == 'lower' and floor < ignore['goal']):
            return True
        elif (ignore['type'] == 'higher' and floor > ignore['goal']):
            return True
        
    elif ignore['condition'] == 'gold':
        gold_info = im.check_gold(GOLD_POS)
        if not gold_info:
            return False
        
        gold, suffix = gold_info
        if(ignore['type'] == 'lower' and im.compare_gold(f"{gold}{suffix}", ignore['goal']) < 0):
            return True
        elif (ignore['type'] == 'higher' and im.compare_gold(f"{gold}{suffix}", ignore['goal']) > 0):
            return True
        
    return False

def run_sequence(kind, sequence):
    def run_subsequence(subsequence):
        for pos in subsequence:
            if shutdown.is_set() or macro_stop.is_set():
                break

            if pos[0] == "click":
                mc.click(
                    pos[1], 
                    pos[2]
                )
            elif pos[0] == "swipe":
                mc.swipe(
                    shutdown,
                    macro_stop,
                    pos[1], 
                    pos[2], 
                    pos[3], 
                    pos[4], 
                    pos[5], 
                    pos[6]
                )
            elif pos[0] == "delay":
                threading.Event().wait(pos[1])

            threading.Event().wait(SEQUENCE_DELAY)

    if kind == "RUN_MULTI_MACRO":
        for subsequence in sequence:
            if shutdown.is_set() or macro_stop.is_set():
                break

            run_subsequence(subsequence["sequence"])

    elif kind == "RUN_MACRO":
        run_subsequence(sequence)

def run_macro(
        command_id: str,
        macro: list[dict[str, Any]], 
        kind: str,
        is_repeat: bool, 
        GOLD_POS: tuple[float, float, float, float], 
        WAVE_POS: tuple[float, float, float, float], 
        REBIRTH_POS: tuple[float, float, float, float],
        CONTINUE_POS: tuple[float, float, float, float]
    ):
    global state, last_error
    try:
        while not shutdown.is_set() and not macro_stop.is_set():

            print(f'{datetime.datetime.now().strftime("%H:%M")} - {kind == "RUN_MULTI_MACRO" and "멀티 " or "싱글 "}매크로 실행 : {macro["name"]}')

            is_rebirth = False
            for sequence in macro["data"]:
                if shutdown.is_set() or macro_stop.is_set():
                    break

                if is_rebirth:
                    break

                check = kind == "RUN_MULTI_MACRO"
                condition = kind == "RUN_MULTI_MACRO" and sequence['condition'] or "empty"
                goal = kind == "RUN_MULTI_MACRO" and sequence['goal'] or 0
                while True:
                    if shutdown.is_set() or macro_stop.is_set():
                        break

                    result = im.check_rebirth(image_matcher, REBIRTH_POS)
                    if result[0]:
                        _continue = im.check_continue(image_matcher, CONTINUE_POS)

                        print(f'{datetime.datetime.now().strftime("%H:%M")} - 환생창 감지; 이어하기 감지 : {_continue[0]}')

                        if _continue[0]:
                            run_sequence("RUN_MULTI_MACRO", macro["continue"])
                            threading.Event().wait(MACRO_DELAY)
                            continue

                        run_sequence("RUN_MACRO", macro["rebirth"])
                        threading.Event().wait(MACRO_DELAY)
                        is_rebirth = True
                        break

                    if check and condition == "wave":
                        floor = im.check_floor(WAVE_POS)
                        if not floor:
                            threading.Event().wait(MACRO_DELAY)
                            continue

                        # print(f'{datetime.datetime.now().strftime("%H:%M")} - 현재 층 : {floor}, 목표 : {goal}')

                        if floor >= goal:
                            if ignore_condition(sequence['ignore'], WAVE_POS, GOLD_POS):

                                print(f'{datetime.datetime.now().strftime("%H:%M")} - 무시 조건 충족; 시퀀스 실행 건너뜀 : {sequence["name"]}')

                                threading.Event().wait(MACRO_DELAY)
                                break

                            print(f'{datetime.datetime.now().strftime("%H:%M")} - 시퀀스 실행 : {sequence["name"]}')

                            run_sequence(kind, sequence['sequence'])
                            break

                        threading.Event().wait(MACRO_DELAY)
                    elif check and condition == "gold":
                        gold_info = im.check_gold(GOLD_POS)

                        gold, suffix = gold_info
                        if suffix == "":
                            threading.Event().wait(MACRO_DELAY)
                            continue

                        # print(f'{datetime.datetime.now().strftime("%H:%M")} - 현재 골드 : {gold}{suffix}, 목표 : {goal}')

                        if im.compare_gold(f"{gold}{suffix}", goal) >= 0:
                            if ignore_condition(sequence['ignore'], WAVE_POS, GOLD_POS):

                                print(f'{datetime.datetime.now().strftime("%H:%M")} - 무시 조건 충족; 시퀀스 실행 건너뜀 : {sequence["name"]}')

                                threading.Event().wait(MACRO_DELAY)
                                break

                            print(f'{datetime.datetime.now().strftime("%H:%M")} - 시퀀스 실행 : {sequence["name"]}')

                            run_sequence(kind, sequence['sequence'])
                            break

                        threading.Event().wait(MACRO_DELAY)
                    elif check and condition == "rebirth":
                        threading.Event().wait(MACRO_DELAY)
                        continue
                    elif condition == "empty":
                        if check and ignore_condition(sequence['ignore'], WAVE_POS, GOLD_POS):

                            print(f'{datetime.datetime.now().strftime("%H:%M")} - 무시 조건 충족; 시퀀스 실행 건너뜀 : {sequence["name"]}')

                            threading.Event().wait(MACRO_DELAY)
                            break

                        print(f'{datetime.datetime.now().strftime("%H:%M")} - 시퀀스 실행 : {sequence["name"]}')

                        run_sequence(kind, sequence['sequence'])
                        break

                    threading.Event().wait(MACRO_DELAY)

            headers = {'Authorization': f'Bearer {TOKEN}', 'X-Device-ID': DEVICE}
            with httpx.Client(base_url=API+'/', headers=headers, timeout=10) as client:
                try:
                    result = {'status': 'done', 'error': "현재 훈장 🎖️100c 환생 시간 ⏱️10:00 현재 다이아 💎10000"}
                    ack = client.post(f'commands/{command_id}/ack', json=result)
                    ack.raise_for_status()
                except Exception as e:
                    print(f'Error occurred while sending ack: {e}')

            if not is_repeat:
                break
    except Exception as e:
        last_error = str(e)
        log.exception('macro failed')
    finally:
        state = 'idle'


def load_macros():
    path = BASE_DIR / "macro.py"

    if not path.is_file():
        raise FileNotFoundError(f"매크로 파일을 찾을 수 없습니다: {path}")

    spec = importlib.util.spec_from_file_location(
        "external_macros",
        path
    )

    if spec is None or spec.loader is None:
        raise RuntimeError("매크로 파일을 로드할 수 없습니다.")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module.macros, module.multi_macros, module.GOLD_POS, module.WAVE_POS, module.REBIRTH_POS, module.CONTINUE_POS


def execute(command: dict[str, Any], command_id: str):
    global macro_thread, state, last_error

    kind = command['type'].upper()
    p = command.get('payload') or {}
    if kind == 'STOP':
        stop_macro()
        
        print(f'{datetime.datetime.now().strftime("%H:%M")} - 매크로 중지 응답')

    elif kind == 'CLICK':
        stop_macro()

        print(f'{datetime.datetime.now().strftime("%H:%M")} - CLICK command executed')

        mc.click(float(p['x']), float(p['y']), float(p.get('duration', .05)))

    elif kind == 'SWIPE':
        stop_macro()

        print(f'{datetime.datetime.now().strftime("%H:%M")} - SWIPE command executed')

        mc.swipe(
            float(p['start_x']), 
            float(p['start_y']), 
            float(p['end_x']), 
            float(p['end_y']), 
            float(p.get('duration', .5)), 
            int(p.get('steps', 30))
        )

    elif kind == 'RUN_MACRO' or kind == 'RUN_MULTI_MACRO':
        stop_macro()
        macro_name = p.get('name')
        is_repeat = p.get('repeat')

        print(f'{datetime.datetime.now().strftime("%H:%M")} - 매크로 실행 응답 : {macro_name}, 반복 : {is_repeat}')

        if not macro_name:
            raise ValueError('Missing macro name')
        
        macros, multi_macros, GOLD_POS, WAVE_POS, REBIRTH_POS, CONTINUE_POS = load_macros()

        macro = None
        if kind == 'RUN_MACRO':
            macro = macros[macro_name]

        elif kind == 'RUN_MULTI_MACRO':
            macro = multi_macros[macro_name]

        if not macro:
            raise ValueError(f'Unknown macro: {macro_name}')
        
        macro_stop.clear()
        last_error = ''
        state = 'running'
        t = threading.Thread(target=run_macro, args=(command_id, macro, kind, is_repeat, GOLD_POS, WAVE_POS, REBIRTH_POS, CONTINUE_POS), daemon=True)
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

    print(f'Agent started for {DEVICE}')

    last_beat = 0.

    screen_stop, screen_thread, screen_watching = start_screen_thread()

    with httpx.Client(base_url=API+'/', headers=headers, timeout=10) as client:
        while not shutdown.is_set():
            try:
                if time.monotonic() - last_beat >= HEARTBEAT:
                    r = client.post('heartbeat', json={'status': state, 'last_error': last_error})
                    data = r.json()

                    if data.get("screen_watching"):
                        screen_watching.set()
                    else:
                        screen_watching.clear()

                    r.raise_for_status()
                    last_beat = time.monotonic()

                r = client.get('commands/next')

                r.raise_for_status()
                cmd = r.json().get('command')
                if cmd:
                    command_id = str(cmd['id'])
                    try:
                        execute(cmd, command_id)
                        result = {'status': 'claimed'}
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

    screen_stop.set()
    screen_thread.join(timeout=2)
    stop_macro()


if __name__ == '__main__':
    def handle_signal(_signum, _frame):
        shutdown.set()
        macro_stop.set()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    main()
