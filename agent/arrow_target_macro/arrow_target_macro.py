import time
import cv2
import numpy as np

from collections import deque
from window_capture.screen_capture import capture_jpeg, find_game_child


TARGET_REGION = (0.335, 0.33, 0.658, 0.43)

ARROW_TIME = 0.72
HIT_X = 0.5

CLICK_DURATION = 0

import win32api
import win32con
import win32gui


def shoot(hwnd: int, x: int, y: int) -> float:
    lparam = win32api.MAKELONG(x, y)

    win32gui.PostMessage(
        hwnd,
        win32con.WM_LBUTTONDOWN,
        win32con.MK_LBUTTON,
        lparam
    )

    win32gui.PostMessage(
        hwnd,
        win32con.WM_LBUTTONUP,
        0,
        lparam
    )

    return time.perf_counter()


def auto_shoot_fast(
    matcher,
    stop_event,
    threshold=0.85,
    input_delay=0.02,
    max_shots=7,
):
    hwnd = find_game_child()

    left, top, right, bottom = win32gui.GetClientRect(hwnd)

    shoot_x = (right - left) // 2
    shoot_y = (bottom - top) // 2

    template_width = matcher.templates["arrow_target"].shape[1]

    # 현재 과녁의 위치 기록
    positions = deque(maxlen=20)

    fired = False
    missing = 0
    count = 0

    hit_x = None

    # 속도 측정 조건
    MIN_SPAN = 0.08
    MAX_SPAN = 0.35
    MIN_DISTANCE = 5

    # 위치 추정 오차 허용 범위
    MAX_RESIDUAL = 3.0

    # 발사 시각이 임박했을 때 정밀 대기
    FINAL_WAIT = 0.03

    def detect():
        nonlocal hit_x

        t0 = time.perf_counter()

        jpeg = capture_jpeg(
            hwnd,
            region=TARGET_REGION
        )

        t1 = time.perf_counter()

        if hit_x is None:
            img = cv2.imdecode(
                np.frombuffer(jpeg, dtype=np.uint8),
                cv2.IMREAD_COLOR
            )

            if img is None:
                raise RuntimeError("이미지 디코딩 실패")

            hit_x = img.shape[1] * HIT_X

            print(
                f"캡처 너비={img.shape[1]}px, "
                f"명중 위치={hit_x:.1f}px"
            )

        result = matcher.match(
            jpeg,
            "arrow_target",
            threshold
        )

        if not result["matched"]:
            return None

        x = result["position"][0] + template_width / 2

        return x, (t0 + t1) / 2

    def estimate_motion():
        if len(positions) < 3:
            return None

        samples = np.array(positions, dtype=np.float64)

        xs = samples[:, 0]
        times = samples[:, 1]

        span = times[-1] - times[0]

        if span < MIN_SPAN:
            return None

        if xs[0] - xs[-1] < MIN_DISTANCE:
            return None

        ts = times - times[0]

        slope, intercept = np.polyfit(ts, xs, 1)

        speed = -slope

        if speed <= 0:
            return None

        predicted = slope * ts + intercept

        residual = np.sqrt(
            np.mean((xs - predicted) ** 2)
        )

        if residual > MAX_RESIDUAL:
            return None

        # 현재 시점에서의 예측 위치
        latest_t = times[-1]

        latest_x = (
            slope * (latest_t - times[0])
            + intercept
        )

        return speed, latest_x, latest_t, residual

    def precise_wait(target_time):
        while not stop_event.is_set():
            remaining = target_time - time.perf_counter()

            if remaining <= 0:
                return True

            if remaining > 0.01:
                if stop_event.wait(remaining - 0.005):
                    return False

            elif remaining > 0.002:
                time.sleep(0.001)

        return False

    while not stop_event.is_set() and count < max_shots:
        detected = detect()

        if detected is None:
            missing += 1

            if missing >= 3:
                positions.clear()
                fired = False
                missing = 0

            continue

        missing = 0

        if fired:
            continue

        x, t = detected

        positions.append((x, t))

        # 오래된 위치 기록 제거
        while (
            len(positions) > 1
            and t - positions[0][1] > MAX_SPAN
        ):
            positions.popleft()

        motion = estimate_motion()

        if motion is None:
            continue

        speed, current_x, current_t, residual = motion

        # 과녁이 명중 위치에 도착할 시각
        arrival_time = current_t + (current_x - hit_x) / speed

        # 화살이 발사되어야 할 시각
        release_time = arrival_time - ARROW_TIME

        # 메시지 전송 및 처리 지연 보정
        fire_time = release_time - input_delay

        remaining = fire_time - time.perf_counter()

        if remaining <= 0:
            actual_time = shoot(hwnd, shoot_x, shoot_y)

            count += 1
            fired = True

            print(
                f"즉시 발사 {count}/{max_shots} | "
                f"지연={-remaining * 1000:.2f}ms"
            )
            continue

        # 발사 직전까지 계속 추적
        if remaining > FINAL_WAIT:
            continue

        print(
            f"속도={speed:.1f}px/s | "
            f"오차={residual:.2f}px | "
            f"클릭까지={remaining:.3f}초"
        )

        if precise_wait(fire_time):
            actual_time = shoot(hwnd, shoot_x, shoot_y)

            count += 1
            fired = True

            print(
                f"발사 {count}/{max_shots} | "
                f"전송 시각 오차={(actual_time - fire_time) * 1000:.2f}ms"
            )