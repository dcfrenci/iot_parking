from ultralytics import YOLO

model = YOLO('Model/yolov11x-license-plate.pt')
# results = model.predict(source='Dataset/00a7d31c6cc6b7f3_jpg.rf.641695200cda83be76f64c5402215f27.jpg')
# results = model.predict(source='Dataset/005e1faed531ae7e_jpg.rf.b493fac1c7704ed76cf809123c779202.jpg')
results = model.predict(source='Model/Dataset/00e8e5e79255536f_jpg.rf.04e24b86d0c062773ed207e247043b8c.jpg')

# print(results[0].boxes)

# results[0].show()
import easyocr
import re


def ocr(image):
    reader = easyocr.Reader(['en'], gpu=True)
    results = reader.readtext(image)
    
    full_text = "".join([res[1] for res in results])
    
    clean_text = re.sub(r'[^A-Z0-9]', '', full_text.upper())
    print("EASY_OCR===============")
    print(clean_text)



import os
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'

from paddleocr import PaddleOCR

# Disabilita il controllo di connettività che fallisce nel tuo terminale

# Inizializzazione corretta per le versioni recenti
ocr_engine = PaddleOCR(use_angle_cls=True, lang='en')

def ocr_paddle(image_thresh):
    # image_thresh è l'immagine dopo il thresholding
    img = cv2.imread("gray_crop.jpg")

    plt.figure()
    plt.imshow(img)
    plt.show()

    # result = ocr_engine.ocr(img, cls=True)
    
    # print(result[0][1][1])
    return

    if result[0]:
        text, confidence = result[0][0]
        print("PADDLE_OCR===========")
        print(text)
        return text, confidence
    return None, 0


import numpy as np
import cv2
import matplotlib.pyplot as plt

for r in results:
    img = r.orig_img  # The original image as a numpy array
    
    for box in r.boxes:
        # 1. Get coordinates in [xmin, ymin, xmax, ymax] format
        # .xyxy[0] returns a tensor, so we convert to numpy and cast to int
        coords = box.xyxy[0].cpu().numpy().astype(int)
        x1, y1, x2, y2 = coords
        
        # 2. Add a tiny bit of padding (optional but better for OCR)
        pad = 5
        # Ensure we don't go outside the image boundaries
        h, w, _ = img.shape
        y1_p, y2_p = max(0, y1-pad), min(h, y2+pad)
        x1_p, x2_p = max(0, x1-pad), min(w, x2+pad)

        # 3. Crop using NumPy slicing
        crop = img[y1_p:y2_p, x1_p:x2_p]

        width = 800
        ratio = width / float(crop.shape[1])
        height = int(crop.shape[0] * ratio)
        new_size = (width, height)

        # 2. Applica il Resize (INTER_CUBIC è ideale per l'ingrandimento)
        resized = cv2.resize(crop, new_size, interpolation=cv2.INTER_CUBIC)

        # 3. (Opzionale) Conversione in scala di grigi per pulire ulteriormente
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        _, thresh = cv2.adaptiveThreshold(
            blurred, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )

        ocr(thresh)
        ocr_paddle(thresh)

        comparison = np.hstack((gray, thresh))

        # 3. Salviamo il file nella cartella del progetto
        output_path = "debug_preprocessing.jpg"
        cv2.imwrite(output_path, comparison)

        
        # 5. Display the result
        crop_rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        filename = f"resized_crop.jpg"
        cv2.imwrite(filename, crop_rgb)
        crop_rgb = cv2.cvtColor(thresh, cv2.COLOR_BGR2RGB)
        filename = f"gray_crop.jpg"
        cv2.imwrite(filename, crop_rgb)

