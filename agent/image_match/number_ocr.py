"""Read numbers from a normalized region of a captured JPEG using RapidOCR."""
from dataclasses import dataclass
import io
import re
from typing import Optional

import numpy as np # type: ignore
from PIL import Image, ImageEnhance, ImageOps # type: ignore
from rapidocr import RapidOCR # type: ignore


@dataclass(frozen=True)
class NumberResult:
    value: Optional[int]
    raw_text: str
    confidence: Optional[float]


class NumberReader:
    def __init__(self, region=(0.70, 0.05, 0.90, 0.12), min_confidence=0.5):
        x1, y1, x2, y2 = region
        if not (0 <= x1 < x2 <= 1 and 0 <= y1 < y2 <= 1):
            raise ValueError('OCR_REGION must be x1,y1,x2,y2 in 0..1')
        
        self.region = region
        self.min_confidence = min_confidence
        self.engine = RapidOCR()

    def read(self, jpeg: bytes) -> NumberResult:
        with Image.open(io.BytesIO(jpeg)) as source:
            rgb = source.convert('RGB')

        w, h = rgb.size
        x1, y1, x2, y2 = self.region
        crop = rgb.crop((int(x1*w), int(y1*h), int(x2*w), int(y2*h)))
        if crop.width < 2 or crop.height < 2:
            return NumberResult(None, '', None)
        
        crop = ImageOps.autocontrast(crop)
        crop = ImageEnhance.Contrast(crop).enhance(1.5)
        crop = crop.resize((crop.width * 3, crop.height * 3), Image.Resampling.LANCZOS)
        result = self.engine(np.asarray(crop))
        texts = list(getattr(result, 'txts', None) or [])
        scores = list(getattr(result, 'scores', None) or [])
        if not texts:
            return NumberResult(None, '', None)
        
        # Intended for a single number within the crop; reject ambiguous multi-line results.
        raw = ' '.join(str(t) for t in texts).strip()
        confidence = min(map(float, scores)) if scores else None
        if confidence is not None and confidence < self.min_confidence:
            return NumberResult(None, raw, confidence)
        
        normalized = raw.replace(',', '').replace(' ', '')
        if not re.fullmatch(r'\d+', normalized):
            return NumberResult(None, raw, confidence)
        return NumberResult(int(normalized), raw, confidence)
