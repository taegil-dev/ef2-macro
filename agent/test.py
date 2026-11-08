import image_match.image_match as im
import window_capture.screen_capture as sc

from pathlib import Path

# jpeg = Path("image_match/templates/rebirth.jpg").read_bytes()

# image_matcher = im.ImageMatcher()
# image_matcher.load_template("rebirth", "screenshot.jpg")

# match_result = image_matcher.match(jpeg, "rebirth", threshold=0.7)

# print(match_result)

jpeg = sc.capture_jpeg(sc.find_game_child("오늘도 환생 2"), region=(0.40, 0.55, 0.46, 0.578))
# jpeg = sc.capture_jpeg(sc.find_game_child("오늘도 환생 2"), region=(0.357, 0.129, 0.641, 0.321))

with open("screenshot.jpg", "wb") as f:
    f.write(jpeg)

im.check_time((0.40, 0.55, 0.46, 0.578))