from typing import Any
import datetime

import image_match.image_match as im
import macro_click.macro_click as mc
import arrow_target_macro.arrow_target_macro as atm
from agent import BASE_DIR

SEQUENCE_DELAY = 0.2
MACRO_DELAY = 2

image_matcher = im.ImageMatcher()
image_matcher.load_template("rebirth", BASE_DIR / "image_match" / "templates" / "rebirth.jpg")
image_matcher.load_template("continue", BASE_DIR / "image_match" / "templates" / "continue.jpg")
image_matcher.load_template("continue_end", BASE_DIR / "image_match" / "templates" / "continue_end.jpg")
image_matcher.load_template("arrow_target", BASE_DIR / "image_match" / "templates" / "arrow_target.jpg")


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

def run_sequence(thread_var, kind, sequence):

    # 서브 시퀀스; 멀티 매크로의 경우 시퀀스 안에 시퀀스가 있음
    def run_subsequence(subsequence):
        for pos in subsequence:
            if thread_var.shutdown.is_set() or thread_var.macro_stop.is_set():
                break

            if pos[0] == "click":
                mc.click(
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

    # 멀티 매크로 일 경우 시퀀스 안의 시퀀스를 차례대로 실행
    if kind == "RUN_MULTI_MACRO":
        for subsequence in sequence:
            if thread_var.shutdown.is_set() or thread_var.macro_stop.is_set():
                break

            run_subsequence(subsequence["sequence"])

    # 일반 매크로는 한번만 실행
    elif kind == "RUN_MACRO":
        run_subsequence(sequence)

    # 매크로 실행 후 대기
    thread_var.macro_stop.wait(MACRO_DELAY)


def run_macro(thread_var, kind, macro, sequence, pos):
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

            # 재실행 까지 대기
            while thread_var.restart.is_set():
                thread_var.macro_stop.wait(1)

            # 첫 화면 제거
            thread_var.macro_stop.wait(5)
            mc.click(0.5, 0, show_marker=False)
            thread_var.macro_stop.wait(1)
            mc.click(0.47, 0.55, show_marker=True)
            continue

        # 환생 체크
        result = im.check_rebirth(image_matcher, pos["REBIRTH_POS"])
        if result:

            # 이어하기 체크
            _continue = im.check_continue(image_matcher, pos["CONTINUE_POS"])
            # 매크로 결과에 넣을 웨이브 탐지 단, 환생창이 있을 경우 중앙 웨이브 탐지를 하지 못하므로 비교는 하지 않는다
            wave = im.check_floor(pos["WAVE_POS"], pos["WAVE_POS2"], compare=False)

            print(f'{datetime.datetime.now().strftime("%H:%M")} - ⚠️ 현재 웨이브: {wave}, 환생 감지; {_continue and "🔁 이어하기" or "❇️ 환생"}')

            if _continue:
                run_sequence(thread_var, "RUN_MULTI_MACRO", macro["continue"])
                continue

            run_sequence(thread_var, "RUN_MULTI_MACRO", macro["rebirth"])

            is_rebirth = True
            # 환생 버튼이 안눌러졌어도 어차피 반복 실행 시 다시 환생창 체크부터 진행하기 때문에 문제 없음
            return wave, is_rebirth

        # 웨이브 조건 체크
        if check and condition == "wave":

            # 웨이브를 확인하는 절차; 상단 웨이브는 뿔피리, 엘비에 따라 숫자가 이상하게 생길 수 있으므로 중앙 웨이브랑 비교하여 한번 걸러냄
            floor = im.check_floor(pos["WAVE_POS"], pos["WAVE_POS2"])
            if not floor:
                continue

            if floor >= goal:
                # 무시 조건 체크
                if ignore_condition(sequence['ignore'], pos):
                    print(f'{datetime.datetime.now().strftime("%H:%M")} - ❌ {sequence["name"]} 무시; 현재 웨이브 {floor} : 목표 웨이브 {sequence["ignore"]["goal"]}')
                    break

                print(f'{datetime.datetime.now().strftime("%H:%M")} - ▶️  시퀀스 {sequence["name"]} 실행')

                run_sequence(thread_var, kind, sequence['sequence'])
                break

        # 골드 조건 체크
        elif check and condition == "gold":

            # 골드는 숫자와 단위로 감지
            gold, suffix = im.check_gold(pos["GOLD_POS"])
            if suffix == "":
                continue

            # 골드 비교는 문자열로 비교 "100az"
            if im.compare_gold(f"{gold}{suffix}", goal):
                if ignore_condition(sequence['ignore'], pos):
                    print(f'{datetime.datetime.now().strftime("%H:%M")} - ❌ {sequence["name"]} 무시; 현재 웨이브 {floor} : 목표 웨이브 {sequence["ignore"]["goal"]}')
                    break

                print(f'{datetime.datetime.now().strftime("%H:%M")} - ▶️  시퀀스 {sequence["name"]} 실행')

                run_sequence(thread_var, kind, sequence['sequence'])
                break

        # 시간 조건 체크
        elif check and condition == "time":

            # (초, 분, 시)의 튜플 반환
            current_time = im.check_time(pos["TIMER_POS"])
            # 튜플과 문자열로 비교 00:00:00
            if im.compare_time(current_time, goal):
                if ignore_condition(sequence['ignore'], pos):
                    print(f'{datetime.datetime.now().strftime("%H:%M")} - ❌ {sequence["name"]} 무시; 현재 웨이브 {floor} : 목표 웨이브 {sequence["ignore"]["goal"]}')
                    break

                print(f'{datetime.datetime.now().strftime("%H:%M")} - ▶️  시퀀스 {sequence["name"]} 실행')

                run_sequence(thread_var, kind, sequence['sequence'])
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
            
            print(f'{datetime.datetime.now().strftime("%H:%M")} - ▶️  시퀀스 {sequence["name"]} 실행')

            # 시퀀스 이름으로 함수를 찾아서 실행
            if sequence['name'] in data:
                # 이름(args...)
                data[sequence['name']]["func"](*data[sequence['name']]["args"])
                break

        # 일반 매크로 실행; 아무 조건 없음
        elif condition == "empty":
            if check and ignore_condition(sequence['ignore'], pos):
                print(f'{datetime.datetime.now().strftime("%H:%M")} - ❌ {sequence["name"]} 무시; 현재 웨이브 {floor} : 목표 웨이브 {sequence["ignore"]["goal"]}')
                break

            print(f'{datetime.datetime.now().strftime("%H:%M")} - ▶️  시퀀스 {sequence["name"]} 실행')

            run_sequence(thread_var, kind, sequence['sequence'])
            break

    return wave, is_rebirth