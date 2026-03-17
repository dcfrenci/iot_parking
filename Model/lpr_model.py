"""
License Plate Detection + OCR Pipeline
Uses YOLOv11 for detection, EasyOCR and PaddleOCR for text extraction.
"""

import os
import re
import cv2
import numpy as np
import matplotlib.pyplot as plt

# ── Environment flags (must be set before importing PaddleOCR) ──────────────
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'

# ── Imports ──────────────────────────────────────────────────────────────────
from ultralytics import YOLO
import easyocr
from paddleocr import PaddleOCR


# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────
MODEL_PATH   = 'Model/yolov11x-license-plate.pt'
IMAGE_PATH   = 'Model/Dataset/generic_1.jpg'
RESIZE_WIDTH = 800
PAD          = 5
DEBUG_DIR    = 'Debug'


# ─────────────────────────────────────────────────────────────────────────────
# Model initialisation (done once at module level)
# ─────────────────────────────────────────────────────────────────────────────
print("[init] Loading YOLO model …")
yolo_model = YOLO(MODEL_PATH)

print("[init] Loading EasyOCR …")
easy_reader = easyocr.Reader(['en'], gpu=True)

print("[init] Loading PaddleOCR …")
paddle_engine = PaddleOCR(use_textline_orientation=True, lang='en')


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def clean_plate_text(raw: str) -> str:
    """Keep only uppercase letters and digits — typical licence-plate charset."""
    return re.sub(r'[^A-Z0-9]', '', raw.upper())


def preprocess(crop_bgr: np.ndarray, resize_width: int = RESIZE_WIDTH):
    """
    Full preprocessing pipeline for a single licence-plate crop.

    Returns
    -------
    resized      : colour image at target width (BGR)
    gray         : grayscale version
    thresh_otsu  : Otsu global threshold
    thresh_adapt : adaptive Gaussian threshold (better for uneven lighting)
    """
    ratio   = resize_width / float(crop_bgr.shape[1])
    height  = int(crop_bgr.shape[0] * ratio)
    resized = cv2.resize(crop_bgr, (resize_width, height),
                         interpolation=cv2.INTER_CUBIC)

    gray    = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    _, thresh_otsu = cv2.threshold(blurred, 0, 255,
                                   cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    kernel      = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    thresh_otsu = cv2.morphologyEx(thresh_otsu, cv2.MORPH_OPEN, kernel)

    thresh_adapt = cv2.adaptiveThreshold(
        blurred, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )

    return resized, gray, thresh_otsu, thresh_adapt


def ensure_bgr(image: np.ndarray) -> np.ndarray:
    """Convert grayscale (2-D) to BGR so both OCR engines get a 3-channel image."""
    if image.ndim == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    return image


def save_debug(gray: np.ndarray, thresh_otsu: np.ndarray,
               thresh_adapt: np.ndarray, idx: int):
    """Save side-by-side debug image for one detected plate."""
    os.makedirs(DEBUG_DIR, exist_ok=True)
    comparison = np.hstack([gray, thresh_otsu, thresh_adapt])
    path = os.path.join(DEBUG_DIR, f"plate_{idx:02d}_preprocessing.jpg")
    cv2.imwrite(path, comparison)
    print(f"  [debug] saved → {path}")


# ─────────────────────────────────────────────────────────────────────────────
# OCR engines
# ─────────────────────────────────────────────────────────────────────────────
def run_easyocr(image: np.ndarray) -> str:
    """Run EasyOCR on a pre-processed image."""
    img_bgr    = ensure_bgr(image)
    raw_result = easy_reader.readtext(img_bgr)
    raw_text   = "".join([r[1] for r in raw_result])
    clean      = clean_plate_text(raw_text)
    print(f"  EasyOCR  → {clean or '(no text)'}")
    return clean


def run_paddleocr(image: np.ndarray) -> tuple:
    """
    Run PaddleOCR on a pre-processed image.

    In PaddlePaddle 3.x, predict() returns a list of OCRResult objects.
    OCRResult behaves like a dict → access fields via res['rec_texts'],
    NOT via attribute access (res.rec_texts) or block.get('rec_text').

    Returns
    -------
    (clean_text, best_confidence)
    """
    img_bgr = ensure_bgr(image)

    full_text       = ""
    best_confidence = 0.0

    for res in paddle_engine.predict(img_bgr):
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

    clean = clean_plate_text(full_text)
    print(f"  PaddleOCR → {clean or '(no text)'}  [conf: {best_confidence:.2f}]")
    return clean, best_confidence


# ─────────────────────────────────────────────────────────────────────────────
# Main pipeline
# ─────────────────────────────────────────────────────────────────────────────
def process_image(image_path: str):
    print(f"\n[detect] Running YOLO on: {image_path}")
    detections = yolo_model.predict(source=image_path)

    for result in detections:
        img = result.orig_img

        if result.boxes is None or len(result.boxes) == 0:
            print("[detect] No plates found.")
            continue

        print(f"[detect] Found {len(result.boxes)} plate(s).")

        for idx, box in enumerate(result.boxes):
            print(f"\n── Plate {idx + 1} ──────────────────────────────")

            # ── 1. Crop ──────────────────────────────────────────────────────
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
            h, w            = img.shape[:2]

            y1_p = max(0, y1 - PAD);  y2_p = min(h, y2 + PAD)
            x1_p = max(0, x1 - PAD);  x2_p = min(w, x2 + PAD)

            crop = img[y1_p:y2_p, x1_p:x2_p]

            if crop.size == 0:
                print("  [warn] Empty crop, skipping.")
                continue

            # ── 2. Pre-process ───────────────────────────────────────────────
            resized, gray, thresh_otsu, thresh_adapt = preprocess(crop)

            # ── 3. Save debug images ─────────────────────────────────────────
            save_debug(gray, thresh_otsu, thresh_adapt, idx)

            # ── 4. OCR — Otsu ────────────────────────────────────────────────
            print("  [ocr] Otsu threshold:")
            easy_text_otsu              = run_easyocr(thresh_otsu)
            paddle_text_otsu, conf_otsu = run_paddleocr(thresh_otsu)

            # ── 5. OCR — Adaptive ────────────────────────────────────────────
            print("  [ocr] Adaptive threshold:")
            easy_text_adapt               = run_easyocr(thresh_adapt)
            paddle_text_adapt, conf_adapt = run_paddleocr(thresh_adapt)

            # ── 6. Pick best Paddle result ────────────────────────────────────
            if conf_otsu >= conf_adapt:
                best_paddle, best_conf = paddle_text_otsu,  conf_otsu
            else:
                best_paddle, best_conf = paddle_text_adapt, conf_adapt

            print(f"\n  ★ Best PaddleOCR : {best_paddle}  [conf: {best_conf:.2f}]")
            print(f"  ★ EasyOCR (Otsu) : {easy_text_otsu}")
            print(f"  ★ EasyOCR (Adap) : {easy_text_adapt}")

            # ── 7. Annotate original frame ────────────────────────────────────
            # Fall back to best EasyOCR result if Paddle returned nothing
            label = best_paddle if best_paddle else easy_text_otsu
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        # ── Save annotated frame ──────────────────────────────────────────────
        annotated_path = os.path.join(DEBUG_DIR, "annotated_result.jpg")
        cv2.imwrite(annotated_path, img)
        print(f"\n[save] Annotated image → {annotated_path}")

        # ── Optional matplotlib display ───────────────────────────────────────
        plt.figure(figsize=(10, 6))
        plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        plt.title("Detection result")
        plt.axis('off')
        plt.tight_layout()
        plt.show()


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    process_image(IMAGE_PATH)