from Lib import importlib
win32gui = importlib.import_module('win32gui')
import time

import pos as p
import config
import macro_click as mc

delay = 0.2  # 클릭 간 지연 시간 (초)


def find_game_window():
    results = []
    
    def callback(hwnd, _):
        title = win32gui.GetWindowText(hwnd)

        if config.GAME_TITLE in title:
            results.append(hwnd)

    win32gui.EnumWindows(callback, None)

    return results[0] if results else None

def find_target_window(game_hwnd):
    results = []

    def callback(hwnd, _):
        class_name = win32gui.GetClassName(hwnd)

        if class_name == config.TARGET_CLASS:
            results.append(hwnd)

    win32gui.EnumChildWindows(game_hwnd, callback, None)

    return results[0] if results else None



def main():
    game_hwnd = find_game_window()

    if not game_hwnd:
        print("게임 창을 찾지 못했습니다.")
        return

    target_hwnd = find_target_window(game_hwnd)

    if not target_hwnd:
        print("CROSVM_1 창을 찾지 못했습니다.")
        return

    print(f"게임 HWND: {game_hwnd}")
    print("매크로 시작 (Ctrl+C 종료)")

    try:
        sequence = p.sequence["테스트 시퀀스"]
        for pos in sequence:
            if not win32gui.IsWindow(target_hwnd):
                print("게임 창이 종료되었습니다.")
                return

            if pos[0] == "click":
                success = mc.click(
                    target_hwnd,
                    pos[1],
                    pos[2],
                    show_marker=True
                )
            elif pos[0] == "swipe":
                success = mc.swipe(
                    target_hwnd,
                    pos[1],
                    pos[2],
                    pos[3],
                    pos[4],
                    duration=pos[5],
                    steps=pos[6],
                    show_marker=True
                )

            if not success:
                print("클릭 전송 실패")
                return

            time.sleep(delay)

    except KeyboardInterrupt:
        print("\n매크로 종료")

    time.sleep(1)


if __name__ == "__main__":
    main()