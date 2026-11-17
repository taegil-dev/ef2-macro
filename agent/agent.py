from __future__ import annotations
import ctypes
import importlib
import json
import logging
import os
import signal
import subprocess
import sys
import threading
import time
from types import SimpleNamespace
from typing import Any
from Lib.pathlib import Path
import datetime
import httpx
from dotenv import load_dotenv # type: ignore
from supabase import create_client

import macro_click.macro_click as mc
from window_capture.screen_uploader import start_screen_thread
import image_match.image_match as im
from macro_process import run_macro as rm, restart_game as rg
from updater import check_update as cu


BASE_DIR = getattr(sys, "frozen", False) and Path(sys.executable).resolve().parent or Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(
    dotenv_path=ENV_PATH,
    override=True
)

API = os.environ['API_BASE_URL'].rstrip('/')
DEVICE = os.environ['DEVICE_ID']
TOKEN = os.environ['DEVICE_TOKEN']

POLL = 2.0
HEARTBEAT = 15

shutdown = threading.Event()
macro_stop = threading.Event()
macro_thread: threading.Thread | None = None
macro_lock = threading.Lock()
state = 'idle'
last_error = ''

screen_stop, screen_thread, screen_watching = start_screen_thread(shutdown)

restart = threading.Event()

thread_var = SimpleNamespace(
    shutdown=shutdown,
    macro_stop=macro_stop,
    restart=restart,
    screen_watching=screen_watching
)


supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_ANON_KEY"]
)

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


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


def post_repeat_command(kind: str, macro: dict[str, Any]):
    access_token = get_access_token()
    server_headers = {'Authorization': f'Bearer {access_token}'}
    with httpx.Client(base_url=API+'/', headers=server_headers, timeout=10) as client:
        try:
            ack = client.post('api/dashboard/commands', 
                    json={"type": kind, "payload": {"name": macro["name"], "repeat": True}})
            ack.raise_for_status()
        except Exception as e:
            print(f'Error occurred while sending repeat command: {e}')


def post_command_result(
        command_id: str, 
        pos: dict[str, tuple[float, float, float, float]],
        wave,
        is_rebirth: bool):
    client_headers = {'Authorization': f'Bearer {TOKEN}', 'X-Device-ID': DEVICE}
    with httpx.Client(base_url=API+'/api/agent', headers=client_headers, timeout=10) as client:
        try:
            msg = ""
            if is_rebirth:
                diamond = im.check_diamond(pos["DIAMOND_POS"])
                medal, medal_unit = im.check_medal(pos["MEDAL_POS"])

                msg = f"❇️ 환생 결과 : Wave {wave} 🎖️{medal}{medal_unit} 💎{diamond}"
                print(f'{datetime.datetime.now().strftime("%H:%M")} - {msg}')

            result = {'status': 'done', 'error': msg}
            ack = client.post(f'commands/{command_id}/ack', json=result)
            ack.raise_for_status()
        except Exception as e:
            print(f'Error occurred while sending ack: {e}')


def run_command(
        command_id: str,
        macro: list[dict[str, Any]], 
        kind: str,
        is_repeat: bool, 
        pos: dict[str, tuple[float, float, float, float]]
    ):
    global state, last_error
    try:
        is_rebirth = False
        wave = 0

        # 매크로 안 시퀀스 순차적으로 실행
        for sequence in macro["data"]:
            if shutdown.is_set() or macro_stop.is_set():
                break

            # 어떤 매크로든 환생하면 그대로 종료
            if is_rebirth:
                break

            # 매크로 실행; 실행 결과로 환생 또는 종료 시 현재 웨이브랑 환생 여부를 반환
            wave, is_rebirth = rm.run_macro(thread_var, kind, sequence, pos)

        print(f'{datetime.datetime.now().strftime("%H:%M")} - ✅ 매크로 종료{is_rebirth and "; 환생 성공" or ""}')

        # 매크로 실행 결과를 클라이언트로 전송
        post_command_result(command_id, pos, wave, is_rebirth)

    except Exception as e:
        last_error = str(e)
        print(f'{datetime.datetime.now().strftime("%H:%M")} - ❌ 매크로 실패: {last_error}; 매크로 종료')
        macro_stop.set()

    finally:
        state = 'idle'

    # 반복 매크로의 경우 다시 실행
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
            "TIMER_POS": module.TIMER_POS,
            "MEDAL_POS": module.MEDAL_POS,
            "REBIRTH_POS": module.REBIRTH_POS,
            "CONTINUE_POS": module.CONTINUE_POS
        }
    }


def stop_macro():
    global state

    macro_stop.set()
    with macro_lock:
        thread = macro_thread

    if thread and thread.is_alive():
        thread.join(timeout=2)

    state = 'idle'


def execute(command: dict[str, Any], command_id: str):
    global macro_thread, state, last_error

    kind = command['type'].upper()
    p = command.get('payload') or {}
    if kind == 'STOP':
        stop_macro()
        
        print(f'{datetime.datetime.now().strftime("%H:%M")} - ⛔ 매크로 중지')

    elif kind == 'CLICK':
        stop_macro()

        print(f'{datetime.datetime.now().strftime("%H:%M")} - CLICK command executed')

        mc.click(macro_stop, float(p['x']), float(p['y']))

    elif kind == 'SWIPE':
        stop_macro()

        print(f'{datetime.datetime.now().strftime("%H:%M")} - SWIPE command executed')

        mc.swipe(
            shutdown,
            macro_stop,
            float(p['start_x']), 
            float(p['start_y']), 
            float(p['end_x']), 
            float(p['end_y'])
        )

    elif kind == 'RUN_MACRO' or kind == 'RUN_MULTI_MACRO':
        stop_macro()
        macro_name = p.get('name')
        is_repeat = p.get('repeat')

        print(f'{datetime.datetime.now().strftime("%H:%M")} - ✅ 매크로 {macro_name} 실행{is_repeat and " (반복)" or ""}')

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
        t = threading.Thread(target=run_command, args=(command_id, macro, kind, is_repeat, data["pos"]), daemon=True)
        with macro_lock:
            macro_thread = t
        t.start()
    else:
        raise ValueError(f'Unsupported command: {kind}')


def main():
    if not API.startswith('https://') and not API.startswith('http://localhost'):
        raise SystemExit('API_BASE_URL must use HTTPS (except localhost)')
    
    print(f'\n{datetime.datetime.now().strftime("%H:%M")} - ✅ 에이전트 정상 실행중 id: {DEVICE}')

    last_beat = 0.

    headers = {'Authorization': f'Bearer {TOKEN}', 'X-Device-ID': DEVICE}
    with httpx.Client(base_url=API+'/api/agent', headers=headers, timeout=10) as client:
        while not shutdown.is_set():
            try:
                # 주기적인 연결
                if time.monotonic() - last_beat >= HEARTBEAT:
                    r = client.post('heartbeat', json={'status': state, 'last_error': last_error})
                    if r.status_code == 404:
                        continue

                    data = r.json()

                    # 웹페이지를 보고 있을 때만 화면 공유
                    if data.get("screen_watching"):
                        screen_watching.set()
                    else:
                        screen_watching.clear()

                    r.raise_for_status()
                    last_beat = time.monotonic()

                # 명령 받기
                r = client.get('commands/next')

                r.raise_for_status()

                # 명령 실행
                cmd = r.json().get('command')
                if cmd:
                    command_id = str(cmd['id'])
                    try:
                        execute(cmd, command_id)

                        # 명령 결과를 매크로 중지일 땐 done, 그 외엔 claimed로 처리; 매크로는 실행이 종료되면 done으로 처리됨
                        result = {'status': cmd["type"].upper() == "STOP" and 'done' or 'claimed', 'error': ''}
                    except Exception as e:
                        print(f'{datetime.datetime.now().strftime("%H:%M")} - Command {command_id} failed: {e}')
                        result = {'status': 'failed', 'error': str(e)[:500]}

                    # Backend must deduplicate commands and atomically claim them.
                    ack = client.post(f'commands/{command_id}/ack', json=result)
                    ack.raise_for_status()

            except httpx.HTTPStatusError as e:
                print(f'{datetime.datetime.now().strftime("%H:%M")} - {e.request.url}; Backend returned {e.response.text}')

            except (httpx.HTTPError, KeyError) as e:
                print(f'{datetime.datetime.now().strftime("%H:%M")} - Connection/protocol error: {e}')

            except ValueError as e:
                print(f'{datetime.datetime.now().strftime("%H:%M")} - ValueError: {e}')

            shutdown.wait(POLL)

    screen_stop.set()
    screen_thread.join(timeout=2)
    stop_macro()


def apply_restart():
    res = input("\n🔁 자동 재실행 기능을 사용하시겠습니까?(y/n): ").strip().lower() == "y"
    if not res:
        return
    
    print("바탕화면에 있는 바로가기 파일을 찾고 있습니다...")

    # 바탕화면 경로 가져오기; 윈도우 환경에 따라 절대적인 경로가 다르기 때문에 컴퓨터에 저장되어 있는 바탕화면 경로를 가져오는 방법을 사용
    buffer = ctypes.create_unicode_buffer(260)
    ctypes.windll.shell32.SHGetFolderPathW(
        None,
        0x0010,  # CSIDL_DESKTOPDIRECTORY
        None,
        0,
        buffer
    )

    desktop = Path(buffer.value)

    # 파일이름은 항상 동일(구글 플레이 for PC 기준)
    target_path = desktop / "오늘도 환생 2  방치형 디펜스 RPG.lnk"
    if target_path.exists():
        print(f"✅ 파일을 정상적으로 찾았습니다: {target_path}")
    else:
        print(f"❌ 파일을 찾을 수 없습니다. 파일을 추가하고 다시 시도해주세요.")
        exit(1)

    restart_time = input("⏱️ 자동 재실행 시간 설정(기본 3600초)(숫지만 입력): ")
    try:
        restart_time = int(restart_time)
    except ValueError:
        restart_time = 3600

    rg.set_restart(shutdown, restart, target_path, restart_time)


def apply_update():
    update_info = cu.check_update()
    print(f"🚀 agent.exe v{cu.get_current_version()} 실행 중...")
    if not update_info[0]:
        return

    print(f"\n🎉 새로운 버전이 있습니다: v{update_info[1]['version']} 🎉")
    is_update = input("업데이트 하시겠습니까? (y/n): ").strip().lower() == "y"
    if not is_update:
        return

    updater = os.path.join(BASE_DIR, "updater.exe")
    subprocess.Popen(
        [
            updater,
            str(os.getpid()),
            json.dumps(update_info[1]),
            sys.executable
        ], cwd=BASE_DIR, creationflags=subprocess.CREATE_NEW_CONSOLE)

    sys.exit(0)


if __name__ == '__main__':
    def handle_signal(_signum, _frame):
        shutdown.set()
        macro_stop.set()
        screen_stop.set()
        rg.stop_restart()

    # 시그널 등록
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    # 업데이트 확인
    apply_update()
    # 재시작 설정
    apply_restart()
        
    main()
