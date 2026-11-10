import io

import numpy as np # type: ignore
from PIL import Image, ImageEnhance, ImageOps # type: ignore
from rapidocr import RapidOCR # type: ignore

class OCRService:
    def __init__(self):
        self.engine = RapidOCR()

    def recognize_jpeg(self, jpeg: bytes) -> str:
        image = Image.open(io.BytesIO(jpeg)).convert("RGB")

        # 작은 글자 확대
        image = image.resize(
            (image.width * 4, image.height * 4),
            Image.Resampling.LANCZOS
        )

        # 대비 증가
        image = ImageEnhance.Contrast(image).enhance(1.5)

        # 글자 주변 여백 추가
        image = ImageOps.expand(
            image,
            border=12,
            fill=(0, 0, 0)
        )

        # 텍스트 검출 생략
        result = self.engine(
            np.array(image),
            use_det=False,
            use_cls=False,
            use_rec=True
        )

        if result.txts is None or len(result.txts) == 0:
            return ""

        return "".join(result.txts).strip()