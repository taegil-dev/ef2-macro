import re
import cv2
import numpy as np
from image_match.number_ocr import OCRService
from window_capture.screen_capture import capture_jpeg, find_game_child

ocr = OCRService()

def parse_gold_value(text: str):
    match = re.fullmatch(r"(\d+(?:\.\d+)?)([a-z]+)", text.strip())

    if not match:
        return None

    return {
        "value": float(match.group(1)),
        "unit": match.group(2).lower()
    }

def compare_gold(gold1: str, gold2: str) -> int:
    num1 = parse_gold_value(gold1)
    num2 = parse_gold_value(gold2)

    if num1 is None or num2 is None:
        print("Invalid gold format")
        return 0
    
    # 단위 길이 비교
    if len(num1["unit"]) != len(num2["unit"]):
        return 1 if len(num1["unit"]) > len(num2["unit"]) else -1

    # 단위 알파벳 순서 비교
    if num1["unit"] != num2["unit"]:
        return 1 if num1["unit"] > num2["unit"] else -1

    # 같은 단위일 경우 숫자 비교
    return (num1["value"] > num2["value"]) - (num1["value"] < num2["value"])

def check_gold(GOLD_POS):
    # 현재 게임 화면 캡처 (JPEG bytes 반환)
    jpeg = capture_jpeg(find_game_child(), region=GOLD_POS)

    # OCR 분석
    text = ocr.recognize_jpeg(jpeg)

    gold = parse_gold_value(text)

    if gold is None:
        return 0, ""

    return gold["value"], gold["unit"]

def check_diamond(DIAMOND_POS):
    # 현재 게임 화면 캡처 (JPEG bytes 반환)
    jpeg = capture_jpeg(find_game_child(), region=DIAMOND_POS)

    # OCR 분석
    text = ocr.recognize_jpeg(jpeg)

    match = re.search(r"\d+", text)
    
    if not match:
        return False

    diamond = int(match.group())

    return diamond

def check_medal(MEDAL_POS):
    # 현재 게임 화면 캡처 (JPEG bytes 반환)
    jpeg = capture_jpeg(find_game_child(), region=MEDAL_POS)

    # OCR 분석
    text = ocr.recognize_jpeg(jpeg)

    medal = parse_gold_value(text)

    if medal is None:
        print(f"Invalid gold format: {text}")
        return 0, ""

    return medal["value"], medal["unit"]

def check_floor(WAVE_POS, WAVE_POS2, compare=True):
    # 현재 게임 화면 캡처 (JPEG bytes 반환)
    jpeg = capture_jpeg(find_game_child(), region=WAVE_POS)
    jpeg2 = capture_jpeg(find_game_child(), region=WAVE_POS2)

    # OCR 분석
    text = ocr.recognize_jpeg(jpeg)
    text2 = ocr.recognize_jpeg(jpeg2)

    text = text.split(",")[0]

    # 숫자 추출
    match = re.search(r"\d+", text)
    match2 = re.search(r"\d+", text2)

    if not match:
        return False

    floor = int(match.group())

    if compare and match2:
        floor2 = int(match2.group())

        if floor2 < floor:
            return False

    return floor

def check_rebirth(image_matcher, REBIRTH_POS):
    # 현재 게임 화면 캡처 (JPEG bytes 반환)
    jpeg = capture_jpeg(find_game_child(), region=REBIRTH_POS)
    
    # 이미지 매칭
    match_result = image_matcher.match(jpeg, "rebirth", threshold=0.8)

    return match_result["matched"]


def check_continue(image_matcher, CONTINUE_POS):
    # 현재 게임 화면 캡처 (JPEG bytes 반환)
    jpeg = capture_jpeg(find_game_child(), region=CONTINUE_POS)

    # 이미지 매칭
    match_result = image_matcher.match(jpeg, "continue", threshold=0.9)

    return match_result["matched"]


class ImageMatcher:
    def __init__(self):
        self.templates = {}

    def load_template(self, name: str, path: str):
        template = cv2.imread(path, cv2.IMREAD_COLOR)

        if template is None:
            raise FileNotFoundError(path)

        self.templates[name] = template

    def match(self, jpeg: bytes, name: str, threshold=0.85):
        if name not in self.templates:
            raise ValueError(f"템플릿 없음: {name}")

        image_array = np.frombuffer(jpeg, dtype=np.uint8)
        screenshot = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if screenshot is None:
            raise ValueError("이미지 디코딩 실패")

        template = self.templates[name]

        th, tw = template.shape[:2]
        sh, sw = screenshot.shape[:2]

        if tw > sw or th > sh:
            return {
                "matched": False,
                "confidence": 0.0,
                "position": None
            }

        result = cv2.matchTemplate(
            screenshot,
            template,
            cv2.TM_CCOEFF_NORMED
        )

        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        return {
            "matched": max_val >= threshold,
            "confidence": float(max_val),
            "position": max_loc
        }