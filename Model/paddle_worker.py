import os

os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'

from paddleocr import PaddleOCR
import numpy as np
import cv2
import re

PLATE_PATTERN = re.compile(r"[A-Z]{2}[0-9]{3}[A-Z]{2}")

def paddle_worker(worker_name, ocr_queue):
    class Model():
        def __init__(self):
            print("[init] Loading PaddleOCR")
            self.paddle_model = PaddleOCR(use_textline_orientation=True, lang='en')
        
        def preprocess(self, crop_bgr: np.ndarray, resize_width: int = 800):
            """
            Full preprocessing pipeline for a single licence-plate crop.

            Returns
            -------
            thresh_otsu  : Otsu global threshold
            thresh_adapt : adaptive Gaussian threshold (better for uneven lighting)
            """
            ratio   = resize_width / float(crop_bgr.shape[1])
            height  = int(crop_bgr.shape[0] * ratio)
            resized = cv2.resize(crop_bgr, (resize_width, height), interpolation=cv2.INTER_CUBIC)

            gray    = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)

            _, thresh_otsu = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            kernel      = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            thresh_otsu = cv2.morphologyEx(thresh_otsu, cv2.MORPH_OPEN, kernel)

            thresh_adapt = cv2.adaptiveThreshold(
                blurred, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )

            return thresh_otsu, thresh_adapt
        
        def ensure_bgr(self, image: np.ndarray) -> np.ndarray:
            """Convert grayscale (2-D) to BGR so both OCR engines get a 3-channel image."""
            if image.ndim == 2:
                return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            return image
        
        
        def clean_plate_text(self, raw: str) -> str:
            """Keep only uppercase letters and digits."""
            return re.sub(r'[^A-Z0-9]', '', raw.upper())

            
        def predict(self, image: np.ndarray) -> tuple:
            """
            Run PaddleOCR on a pre-processed image.

            In PaddlePaddle 3.x, predict() returns a list of OCRResult objects.
            OCRResult behaves like a dict → access fields via res['rec_texts'],
            NOT via attribute access (res.rec_texts) or block.get('rec_text').

            Returns
            -------
            (clean_text, best_confidence)
            """
            img_bgr = self.ensure_bgr(image)

            full_text       = ""
            best_confidence = 0.0

            for res in self.paddle_model.predict(img_bgr):
                if res is None:
                    continue

                # OCRResult is dict-like: use bracket access
                try:
                    rec_texts  = res['rec_texts']
                    rec_scores = res['rec_scores']
                except (KeyError, TypeError):
                    # Unexpected structure — skip silently
                    continue

                for text, score in zip(rec_texts, rec_scores):
                    full_text       += text
                    best_confidence  = max(best_confidence, score)

            if not full_text:
                print("  PaddleOCR → (no result)")
                return "", 0.0

            clean = self.clean_plate_text(full_text)
            print(f"  PaddleOCR → {clean or '(no text)'}  [conf: {best_confidence:.2f}]")
            return clean, best_confidence
    
    model = Model()
    print(f"[worker] {worker_name} is ready")
    
    while True:
        task = ocr_queue.get()
        
        if task is None:
            print("AI Worker: Shutting down.")
            ocr_queue.task_done()
            break
        
        plate_crop, reply_queue = task
        
        thresh_otsu, thresh_adapt = model.preprocess(plate_crop)
        
        print("  [ocr] Otsu threshold:")
        paddle_text_otsu, conf_otsu = model.predict(thresh_otsu)

        print("  [ocr] Adaptive threshold:")
        paddle_text_adapt, conf_adapt = model.predict(thresh_adapt)
        
        if not PLATE_PATTERN.fullmatch(paddle_text_otsu) and not PLATE_PATTERN.fullmatch(paddle_text_adapt):
            print("  [warn] Wrong OCR match, skipping.")
            best_paddle, best_conf = None, 0.0
        elif not PLATE_PATTERN.fullmatch(paddle_text_otsu):
            best_paddle, best_conf = paddle_text_adapt, conf_adapt
        elif not PLATE_PATTERN.fullmatch(paddle_text_adapt):
            best_paddle, best_conf = paddle_text_otsu,  conf_otsu
        else:
            if conf_otsu >= conf_adapt:
                best_paddle, best_conf = paddle_text_otsu,  conf_otsu
            else:
                best_paddle, best_conf = paddle_text_adapt, conf_adapt
                
        print(f"\n  ★ Best PaddleOCR : {best_paddle}  [conf: {best_conf:.2f}]")
        
        reply_queue.put(best_paddle)
        
        ocr_queue.task_done()        