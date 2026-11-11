from typing import Any
import datetime

import image_match.image_match as im
import macro_click.macro_click as mc
import arrow_target_macro.arrow_target_macro as atm
from agent import BASE_DIR

SEQUENCE_DELAY = 0.2
MACRO_DELAY = 1

image_matcher = im.ImageMatcher()
image_matcher.load_template("rebirth", BASE_DIR / "image_match" / "templates" / "rebirth.jpg")
image_matcher.load_template("continue", BASE_DIR / "image_match" / "templates" / "continue.jpg")
image_matcher.load_template("continue_end", BASE_DIR / "image_match" / "templates" / "continue_end.jpg")
image_matcher.load_template("arrow_target", BASE_DIR / "image_match" / "templates" / "arrow_target.jpg")


def rebirth(thread_var):
    # 환생 버튼
    mc.click(thread_var.macro_stop, 0.538, 0.47, show_marker=False)
    thread_var.macro_stop.wait(5)

    # 영웅 탭
    mc.click(thread_var.macro_stop, 0.344, 0.97, show_marker=False)


def continue_game(thread_var):
    # 이어하기 버튼
    mc.click(thread_var.macro_stop, 0.608, 0.45, show_marker=False)
    thread_var.macro_stop.wait(0.2)

    # 중앙 성
    for _ in range(18):
        mc.click(thread_var.macro_stop, 0.5, 0.26, show_marker=False)


def rebirth_sequence(thread_var, pos):
    # 이어하기 체크
    _continue = im.check_continue(image_matcher, pos["CONTINUE_POS"])

    # 매크로 결과에 넣을 웨이브 탐지 단, 환생창이 있을 경우 중앙 웨이브 탐지를 하지 못하므로 비교는 하지 않는다
    wave = im.check_floor(pos["WAVE_POS"], pos["WAVE_POS2"], compare=False)

    print(f'{datetime.datetime.now().strftime("%H:%M")} - ⚠️ 현재 웨이브: {wave}, 환생 감지; {_continue and "🔁 이어하기" or "❇️ 환생"}')

    thread_var.macro_stop.wait(1)
    if _continue:
        continue_game(thread_var)
        return False, wave
    
    rebirth(thread_var)
    return True, wave

def ignore_condition(
        sequence_name: str,
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
            print(f'{datetime.datetime.now().strftime("%H:%M")} - ❌ {sequence_name} 무시; 현재 웨이브 {floor} < 목표 웨이브 {ignore["goal"]}')
            return True
        
        elif (ignore['type'] == 'higher' and floor > ignore['goal']):
            print(f'{datetime.datetime.now().strftime("%H:%M")} - ❌ {sequence_name} 무시; 현재 웨이브 {floor} > 목표 웨이브 {ignore["goal"]}')
            return True
        
    elif ignore['condition'] == 'gold':
        gold_info = im.check_gold(pos['GOLD_POS'])
        if not gold_info:
            return False
        
        gold, suffix = gold_info
        result = im.compare_gold(f"{gold}{suffix}", ignore['goal'])
        if(ignore['type'] == 'lower'):
            if not result:
                print(f'{datetime.datetime.now().strftime("%H:%M")} - ❌ {sequence_name} 무시; 현재 골드 {gold}{suffix} < 목표 골드 {ignore["goal"]}')
                return True
        
        elif (ignore['type'] == 'higher'):
            if result:
                print(f'{datetime.datetime.now().strftime("%H:%M")} - ❌ {sequence_name} 무시; 현재 골드 {gold}{suffix} > 목표 골드 {ignore["goal"]}')
                return True
        
    return False

def run_sequence(thread_var, kind, sequence, image_pos):
    is_rebirth = False
    # 서브 시퀀스; 멀티 매크로의 경우 시퀀스 안에 시퀀스가 있음
    def run_subsequence(subsequence):
        while True:
            restart = False
            for pos in subsequence:
                if thread_var.shutdown.is_set() or thread_var.macro_stop.is_set():
                    break

                if thread_var.restart.is_set():
                    print(f'{datetime.datetime.now().strftime("%H:%M")} - ⛔ 매크로 일시중지; 게임 재실행 중')
                    while thread_var.restart.is_set():
                        continue
                    print(f'{datetime.datetime.now().strftime("%H:%M")} - 🚥 매크로 재시작')
                    restart = True
                    break

                # 환생 체크
                result = im.check_rebirth(image_matcher, image_pos["REBIRTH_POS"])
                if result:
                    check = rebirth_sequence(thread_var, image_pos)
                    # 이어하기
                    if not check[0]:
                        continue
                    # 환생
                    else:
                        return True


                if pos[0] == "click":
                    mc.click(
                        thread_var.macro_stop,
                        pos[1], 
                        pos[2],
                        show_marker=False
                    )
                elif pos[0] == "swipe":
                    mc.swipe(
                        thread_var.shutdown,
                        thread_var.macro_stop,
                        pos[1], 
                        pos[2], 
                        pos[3], 
                        pos[4], 
                        pos[5], 
                        pos[6],
                        show_marker=False
                    )
                elif pos[0] == "delay":
                    thread_var.macro_stop.wait(pos[1])

                thread_var.macro_stop.wait(SEQUENCE_DELAY)

            if restart:
                continue
            return False

    # 멀티 매크로 일 경우 시퀀스 안의 시퀀스를 차례대로 실행
    if kind == "RUN_MULTI_MACRO":
        for subsequence in sequence:
            if thread_var.shutdown.is_set() or thread_var.macro_stop.is_set():
                break

            is_rebirth = run_subsequence(subsequence["sequence"])
            if is_rebirth:
                break

    # 일반 매크로는 한번만 실행
    elif kind == "RUN_MACRO":
        is_rebirth = run_subsequence(sequence)

    # 매크로 실행 후 대기
    thread_var.macro_stop.wait(MACRO_DELAY)
    return is_rebirth


def run_macro(thread_var, kind, sequence, pos):
    check = kind == "RUN_MULTI_MACRO"
    condition = kind == "RUN_MULTI_MACRO" and sequence['condition'] or "empty"
    goal = kind == "RUN_MULTI_MACRO" and sequence['goal'] or 0

    wave = 0
    is_rebirth = False
    while not thread_var.shutdown.is_set() and not thread_var.macro_stop.is_set():
        # 매크로 딜레이
        thread_var.macro_stop.wait(MACRO_DELAY)

        # 게임 재실행
        if thread_var.restart.is_set():
            print(f'{datetime.datetime.now().strftime("%H:%M")} - ⛔ 매크로 일시중지; 게임 재실행 중')
            while thread_var.restart.is_set():
                continue
            print(f'{datetime.datetime.now().strftime("%H:%M")} - 🚥 매크로 재시작')
            continue

        # 시퀀스 돌리다가 환생한 상태
        if is_rebirth:
            return wave, is_rebirth

        # 환생 체크
        result = im.check_rebirth(image_matcher, pos["REBIRTH_POS"])
        if result:
            check = rebirth_sequence(thread_var, pos)
            # 이어하기
            if not check[0]:
                continue
            # 환생
            else:
                return check[1], True

        # 웨이브 조건 체크
        if check and condition == "wave":

            # 웨이브를 확인하는 절차; 상단 웨이브는 뿔피리, 엘비에 따라 숫자가 이상하게 생길 수 있으므로 중앙 웨이브랑 비교하여 한번 걸러냄
            floor = im.check_floor(pos["WAVE_POS"], pos["WAVE_POS2"])
            if not floor:
                continue

            if floor >= goal:
                # 무시 조건 체크
                if ignore_condition(sequence["name"], sequence['ignore'], pos):
                    break

                print(f'{datetime.datetime.now().strftime("%H:%M")} - 🔔 현재 웨이브 {floor} : 목표 웨이브 {goal}')
                print(f'{datetime.datetime.now().strftime("%H:%M")} - ▶️ 시퀀스 {sequence["name"]} 실행')

                is_rebirth = run_sequence(thread_var, kind, sequence['sequence'], pos)
                break

        # 골드 조건 체크
        elif check and condition == "gold":

            # 골드는 숫자와 단위로 감지
            gold, suffix = im.check_gold(pos["GOLD_POS"])
            if suffix == "":
                continue

            # 골드 비교는 문자열로 비교 "100az"
            if im.compare_gold(f"{gold}{suffix}", goal):
                if ignore_condition(sequence["name"], sequence['ignore'], pos):
                    break

                print(f'{datetime.datetime.now().strftime("%H:%M")} - 🔔 현재 골드 {gold}{suffix} : 목표 골드 {goal}')
                print(f'{datetime.datetime.now().strftime("%H:%M")} - ▶️ 시퀀스 {sequence["name"]} 실행')

                is_rebirth = run_sequence(thread_var, kind, sequence['sequence'], pos)
                break

        # 시간 조건 체크
        elif check and condition == "time":

            # (초, 분, 시)의 정수 튜플 반환
            current_time = im.check_time(pos["TIMER_POS"])

            # 튜플과 문자열로 비교 00:00:00
            if im.compare_time(current_time, goal):
                if ignore_condition(sequence["name"], sequence['ignore'], pos):
                    break

                print(f'{datetime.datetime.now().strftime("%H:%M")} - 🔔 현재 시간 {current_time[2]}:{current_time[1]}:{current_time[0]} : 목표 시간 {goal}')
                print(f'{datetime.datetime.now().strftime("%H:%M")} - ▶️ 시퀀스 {sequence["name"]} 실행')

                is_rebirth = run_sequence(thread_var, kind, sequence['sequence'], pos)
                break

        # 환생 조건일 경우 환생할 때 까지 반복; 즉, 매크로의 마지막
        elif check and condition == "rebirth":
            continue

        # 일반적인 매크로가 아닌 특수 목적용 매크로를 위한 조건
        elif check and condition == "custom":
            # 실행할 함수를 넣어둠
            data = {
                "양궁": { "func": atm.auto_shoot_fast, "args": [image_matcher, thread_var.macro_stop] }
            }
            
            print(f'{datetime.datetime.now().strftime("%H:%M")} - ▶️ 시퀀스 {sequence["name"]} 실행')

            # 시퀀스 이름으로 함수를 찾아서 실행
            if sequence['name'] in data:
                # 이름(args...)
                data[sequence['name']]["func"](*data[sequence['name']]["args"])
                break

        # 일반 매크로 실행; 아무 조건 없음
        elif condition == "empty":
            if ignore_condition(sequence["name"], sequence['ignore'], pos):
                break

            print(f'{datetime.datetime.now().strftime("%H:%M")} - ▶️ 시퀀스 {sequence["name"]} 실행')

            is_rebirth = run_sequence(thread_var, kind, sequence['sequence'], pos)
            break

    return wave, is_rebirth