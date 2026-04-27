from lpr_model import *
from enum import Enum
import requests

import re

CAMERA_INDEX = 0    # 0 = integrata, 1 = USB
OCR_EVERY_N  = 10    # esegui OCR solo ogni N frame (alleggerisce il carico)

N_STABLE_FRAMES = 8
STABLE_PIXEL_THRESH = 8
#MIN_SHARPNESS
COOLDOWN_FRAMES = 30

BASE_URL = "http://127.0.0.1:8000/v1"
PARKING_ID = 1

session = requests.Session()

class State(Enum):
    EMPTY = "EMPTY"
    APPROACHING = "APPROACHING"
    STOP = "STOP"
    ANALYSIS = "ANALYSIS"


def bbox_is_stable(a, b, thresh):
    return all(abs(x - y) < thresh for x, y in zip(a, b))


def run_webcam():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print(f"[error] Impossibile aprire la camera (index={CAMERA_INDEX})")
        return

    print("[webcam] Avviato — premi Q per uscire, S per salvare il frame.")

    frame_count = 0
    state = State.EMPTY
    last_bbox = None
    stable_count = 0
    best_crop = None
    cooldown = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[error] Frame non ricevuto.")
            break

        frame_count += 1

        # se non in cooldown verifica se una targa è entrata all'interno del frame e salva le coordinate
        if cooldown > 0:
            cooldown -= 1
        else:
            results = yolo_model.predict(source=frame)
            found_boxes = []
            for result in results:
                if result.boxes == None:
                    continue
                for box in result.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                    found_boxes.append((x1, y1, x2, y2))
            
            plate_detected = len(found_boxes) > 0


            # macchina a stati

            if state == State.EMPTY:
                if plate_detected:
                    print("EMPTY -> APPROACHING")
                    state = State.APPROACHING
                    last_bbox = found_boxes[0]
                    stable_count = 0
            
            elif state == State.APPROACHING:
                if not plate_detected:
                    print("APPROACHING -> EMPTY (lost plate)")
                    state = State.EMPTY
                else:
                    x1, y1, x2, y2 = found_boxes[0]

                    if last_bbox and bbox_is_stable(found_boxes[0], last_bbox, STABLE_PIXEL_THRESH):
                        stable_count += 1
                    else:
                        stable_count = 0
                    
                    last_bbox = found_boxes[0]

                    if stable_count >= N_STABLE_FRAMES:
                        print("APPROACHING -> STOP")
                        state = State.STOP
            
            elif state == State.STOP:
                print("STOP -> ANALYSIS")
                state = State.ANALYSIS
            
            elif state == State.ANALYSIS:
                
                plate_text = process_image(frame)

                # Check format (AA 000 AA)
                if not re.findall("[A-Z]{2}[0-9]{3}[A-Z]{2}", plate_text):
                    print(f"\t--> Incorrect format (AA000AA): {plate_text}")
                    break

                # Check database for the plate
                plate = session.get(f"{BASE_URL}/plate", params={"plate_text": plate_text})
                
                if plate.status_code != 200:
                    print(f"\t--> The plate {plate_text} was not found")
                    break
                
                plate = plate.json()

                # Check if active
                if not plate["active"]:
                    print(f"\t--> The plate {plate_text} is not active")
                    break

                # Check for payment
                payment = session.get(f"{BASE_URL}/user/payment", params={"account_id": plate["account_id"]})

                if payment.status_code != 200:
                    print(f"\t--> The payment method linked to the plate {plate_text} was not found")
                    break

                # Create new session
                payload = {
                    "account_id": plate["account_id"],
                    "parking_id": PARKING_ID,
                    "plate_number": plate_text
                }
                
                res = session.post(f"{BASE_URL}/paying", json=payload)
                if res.status_code in [200, 201]:
                    print(f"Success! Session started for plate {plate_text}")
                else:
                    print(f"Failed to create session: {res.text}")
                
                print("ANALYSIS -> EMPTY")
                state = State.EMPTY
                cooldown = COOLDOWN_FRAMES

            
        # ── HUD ─────────────────────────────────────────────────────
        cv2.putText(frame, f"Stato: {state.value}  Cooldown: {cooldown}",
                    (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)
        cv2.putText(frame, "Q=esci  S=salva",
                    (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)
        cv2.imshow("Webcam — License Plate Detector", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            path = f"Debug/frame_{frame_count:05d}.jpg"
            cv2.imwrite(path, frame)
            print(f"[save] Frame salvato → {path}")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    run_webcam()