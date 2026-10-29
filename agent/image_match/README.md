# RapidOCR number recognition add-on

This add-on extends the existing Windows PC Agent that uses `screen_capture.py` from `game_screen_addon.zip`. It does not change the Vercel API or database. OCR results are logged **locally**, not sent to the website.

## Install

Copy `agent/number_ocr.py` and `agent/ocr_worker.py` beside `agent.py` and `screen_capture.py`.

```powershell
.\.venv\Scripts\python.exe -m pip install rapidocr onnxruntime numpy pillow pywin32
```

RapidOCR may download model files on first run. This does not require installing a separate OCR executable.

## .env

```dotenv
OCR_REGION=0.70,0.05,0.90,0.12
OCR_INTERVAL_SECONDS=1
OCR_MIN_CONFIDENCE=0.5
```

`OCR_REGION` = left,top,right,bottom as ratios of the **captured image**. Note: `capture_jpeg` downsizes wide images; normalized coordinates still work. Select a tight rectangle containing one numeric value.

## agent.py integration

After `load_dotenv(...)` and logging configuration, before the main polling loop:

```python
from ocr_worker import start_ocr_thread
ocr_stop, ocr_thread = start_ocr_thread()
```

Optionally, in the existing shutdown/finally block:

```python
ocr_stop.set()
ocr_thread.join(timeout=2)
```

Logs only when the recognized numeric value changes. On failure, returns `None` (does not guess). It currently supports integer digits and comma separators only, not `1.2M`, `123/500`, or timers. `PrintWindow` capture can fail or return black for Google Play Games even if background clicks work; test capture first. For more accurate OCR, crop the original full-resolution image rather than the resized JPEG if needed.

If you already have a 1-second screenshot upload thread, this add-on independently captures again. To reduce duplicate captures, refactor both threads to share a recent frame with synchronization.
