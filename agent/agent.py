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
from supabase import create_client

import macro_click.macro_click as mc
from window_capture.screen_uploader import start_screen_thread
import image_match.image_match as im
import arrow_target_macro.arrow_target_macro as atm


BASE_DIR = getattr(sys, "frozen", False) and Path(sys.executable).resolve().parent or Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(
    dotenv_path=ENV_PATH,
    override=True
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger('macro-agent')

API = os.getenv('API_BASE_URL', '').rstrip('/')
API_COMMON = os.getenv('API_COMMON_URL', '').rstrip('/')
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
image_matcher.load_template("continue_end", BASE_DIR / "image_match" / "templates" / "continue_end.jpg")
image_matcher.load_template("arrow_target", BASE_DIR / "image_match" / "templates" / "arrow_target.jpg")


supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_ANON_KEY"]
)

# from check_memory.check_memory import monitor_memory

# threading.Thread(
#     target=monitor_memory,
#     args=(shutdown,),
#     daemon=True
# ).start()



def get_access_token():
    session = supabase.auth.get_session()

    if session is None:
        auth = supabase.auth.sign_in_with_password({
            "email": os.environ["SUPABASE_EMAIL"],
            "password": os.environ["SUPABASE_PASSWORD"]
        })
        session = auth.session

    if session is None:
        raise RuntimeError("Supabase 인증 실패")

    return session.access_token


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


def post_repeat_command(kind: str, macro: dict[str, Any]):
    access_token = get_access_token()
    server_headers = {'Authorization': f'Bearer {access_token}'}
    with httpx.Client(base_url=API_COMMON+'/', headers=server_headers, timeout=10) as client:
        try:
            ack = client.post('api/dashboard/commands', 
                    json={"type": kind, "payload": {"name": macro["name"], "repeat": True}})
            ack.raise_for_status()
        except Exception as e:
            print(f'Error occurred while sending repeat command: {e}')


def post_rebirth_result(
        command_id: str, 
        pos: dict[str, tuple[float, float, float, float]],
        wave,
        is_rebirth: bool):
    client_headers = {'Authorization': f'Bearer {TOKEN}', 'X-Device-ID': DEVICE}
    with httpx.Client(base_url=API+'/', headers=client_headers, timeout=10) as client:
        try:
            msg = ""
            if is_rebirth:
                diamond = im.check_diamond(pos["DIAMOND_POS"])
                medal, medal_unit = im.check_medal(pos["MEDAL_POS"])

                msg = f"환생 결과 : Wave {wave} 🎖️{medal}{medal_unit} 💎{diamond}"

            result = {'status': 'done', 'error': msg}
            ack = client.post(f'commands/{command_id}/ack', json=result)
            ack.raise_for_status()
        except Exception as e:
            print(f'Error occurred while sending ack: {e}')
            

def ignore_condition(
        ignore: dict[str, Any], 
        pos: dict[str, tuple[float, float, float, float]]
    ) -> bool:
    if not ignore:
        return False
    
    if ignore['condition'] == 'wave':
        floor = im.check_floor(pos['WAVE_POS'], pos['WAVE_POS2'])
        if floor is None:
            return False
        
        if(ignore['type'] == 'lower' and floor < ignore['goal']):
            return True
        elif (ignore['type'] == 'higher' and floor > ignore['goal']):
            return True
        
    elif ignore['condition'] == 'gold':
        gold_info = im.check_gold(pos['GOLD_POS'])
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
                macro_stop.wait(pos[1])

            macro_stop.wait(SEQUENCE_DELAY)

    if kind == "RUN_MULTI_MACRO":
        for subsequence in sequence:
            if shutdown.is_set() or macro_stop.is_set():
                break

            run_subsequence(subsequence["sequence"])

    elif kind == "RUN_MACRO":
        run_subsequence(sequence)


def run_macro(kind, macro, sequence, pos):
    check = kind == "RUN_MULTI_MACRO"
    condition = kind == "RUN_MULTI_MACRO" and sequence['condition'] or "empty"
    goal = kind == "RUN_MULTI_MACRO" and sequence['goal'] or 0

    wave = 0
    is_rebirth = False
    while not shutdown.is_set() and not macro_stop.is_set():
        result = im.check_rebirth(image_matcher, pos["REBIRTH_POS"])
        if result:
            _continue = im.check_continue(image_matcher, pos["CONTINUE_POS"])

            print(f'{datetime.datetime.now().strftime("%H:%M")} - 환생 감지; 이어하기 감지 : {_continue}')
            
            if _continue:
                run_sequence("RUN_MULTI_MACRO", macro["continue"])
                macro_stop.wait(MACRO_DELAY)
                continue

            wave = im.check_floor(pos["WAVE_POS"], pos["WAVE_POS2"], compare=False)
            run_sequence("RUN_MULTI_MACRO", macro["rebirth"])
            macro_stop.wait(MACRO_DELAY)
            is_rebirth = True
            return wave, is_rebirth

        if check and condition == "wave":
            floor = im.check_floor(pos["WAVE_POS"], pos["WAVE_POS2"])
            if not floor:
                macro_stop.wait(MACRO_DELAY)
                continue


            if floor >= goal:
                if ignore_condition(sequence['ignore'], pos):

                    print(f'{datetime.datetime.now().strftime("%H:%M")} - 무시 조건 충족; 시퀀스 실행 건너뜀 : {sequence["name"]}')

                    macro_stop.wait(MACRO_DELAY)
                    break

                # print(f'{datetime.datetime.now().strftime("%H:%M")} - 현재 층 : {floor}, 목표 : {goal}')
                print(f'{datetime.datetime.now().strftime("%H:%M")} - 시퀀스 실행 : {sequence["name"]}')

                run_sequence(kind, sequence['sequence'])
                break

            macro_stop.wait(MACRO_DELAY)
        elif check and condition == "gold":
            gold_info = im.check_gold(pos["GOLD_POS"])

            gold, suffix = gold_info
            if suffix == "":
                macro_stop.wait(MACRO_DELAY)
                continue


            if im.compare_gold(f"{gold}{suffix}", goal) >= 0:
                if ignore_condition(sequence['ignore'], pos):

                    print(f'{datetime.datetime.now().strftime("%H:%M")} - 무시 조건 충족; 시퀀스 실행 건너뜀 : {sequence["name"]}')

                    macro_stop.wait(MACRO_DELAY)
                    break

                # print(f'{datetime.datetime.now().strftime("%H:%M")} - 현재 골드 : {gold}{suffix}, 목표 : {goal}')
                print(f'{datetime.datetime.now().strftime("%H:%M")} - 시퀀스 실행 : {sequence["name"]}')

                run_sequence(kind, sequence['sequence'])
                break

            macro_stop.wait(MACRO_DELAY)
        elif check and condition == "rebirth":
            macro_stop.wait(MACRO_DELAY)
            continue

        elif check and condition == "custom":
            data = {
                "양궁": { "func": atm.auto_shoot_fast, "args": [image_matcher, macro_stop] }
            }

            print(f'{datetime.datetime.now().strftime("%H:%M")} - 시퀀스 실행 : {sequence["name"]}')

            if sequence['name'] in data:
                data[sequence['name']]["func"](*data[sequence['name']]["args"])
                break

            macro_stop.wait(MACRO_DELAY)
        elif condition == "empty":
            if check and ignore_condition(sequence['ignore'], pos):

                print(f'{datetime.datetime.now().strftime("%H:%M")} - 무시 조건 충족; 시퀀스 실행 건너뜀 : {sequence["name"]}')

                macro_stop.wait(MACRO_DELAY)
                break

            print(f'{datetime.datetime.now().strftime("%H:%M")} - 시퀀스 실행 : {sequence["name"]}')

            run_sequence(kind, sequence['sequence'])
            break

        macro_stop.wait(MACRO_DELAY)

    return wave, is_rebirth


def run_multi_macro(
        command_id: str,
        macro: list[dict[str, Any]], 
        kind: str,
        is_repeat: bool, 
        pos: dict[str, tuple[float, float, float, float]]
    ):
    global state, last_error
    try:

        print(f'{datetime.datetime.now().strftime("%H:%M")} - {kind == "RUN_MULTI_MACRO" and "멀티 " or "싱글 "}매크로 실행 : {macro["name"]}')

        is_rebirth = False
        wave = 0
        for sequence in macro["data"]:
            if shutdown.is_set() or macro_stop.is_set():
                break

            if is_rebirth:
                break

            wave, is_rebirth = run_macro(kind, macro, sequence,  pos)
        
        post_rebirth_result(command_id, pos, wave, is_rebirth)
    except Exception as e:
        last_error = str(e)
        print(f'{datetime.datetime.now().strftime("%H:%M")} - 매크로 실패: {last_error}')
    finally:
        state = 'idle'

    if is_repeat and not shutdown.is_set() and not macro_stop.is_set():
        post_repeat_command(kind, macro)


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

    return {
        "macros": module.macros,
        "multi_macros": module.multi_macros,
        "pos": {
            "GOLD_POS": module.GOLD_POS,
            "WAVE_POS": module.WAVE_POS,
            "WAVE_POS2": module.WAVE_POS2,
            "DIAMOND_POS": module.DIAMOND_POS,
            "MEDAL_POS": module.MEDAL_POS,
            "REBIRTH_POS": module.REBIRTH_POS,
            "CONTINUE_POS": module.CONTINUE_POS
        }
    }


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
        
        data = load_macros()

        macro = None
        if kind == 'RUN_MACRO':
            macro = data["macros"][macro_name]

        elif kind == 'RUN_MULTI_MACRO':
            macro = data["multi_macros"][macro_name]

        if not macro:
            raise ValueError(f'Unknown macro: {macro_name}')
        
        macro_stop.clear()
        last_error = ''
        state = 'running'
        t = threading.Thread(target=run_multi_macro, args=(command_id, macro, kind, is_repeat, data["pos"]), daemon=True)
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
                        result = {'status': cmd["type"].upper() == "STOP" and 'done' or 'claimed', 'error': ''}
                    except Exception as e:
                        print(f'{datetime.datetime.now().strftime("%H:%M")} - Command {command_id} failed: {e}')
                        result = {'status': 'failed', 'error': str(e)[:500]}

                    # Backend must deduplicate commands and atomically claim them.
                    ack = client.post(f'commands/{command_id}/ack', json=result)
                    ack.raise_for_status()

            except httpx.HTTPStatusError as e:
                print(f'{datetime.datetime.now().strftime("%H:%M")} - Backend returned {e.response.status_code}; check API/auth')

            except (httpx.HTTPError, ValueError, KeyError) as e:
                print(f'{datetime.datetime.now().strftime("%H:%M")} - Connection/protocol error: {e}')

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
