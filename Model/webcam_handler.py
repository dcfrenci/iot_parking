from lpr_model import *
from enum import Enum
import requests
import re
import threading

CAMERA_INDEX        = 0   # 0 = integrata, 1 = USB
N_STABLE_FRAMES     = 8
STABLE_PIXEL_THRESH = 8
COOLDOWN_FRAMES     = 30

BASE_URL   = "http://127.0.0.1:8000/v1"
PARKING_ID = 1

session = requests.Session()

# Regex con fullmatch: l'intera stringa deve essere AA000AA, niente di più
PLATE_PATTERN = re.compile(r"[A-Z]{2}[0-9]{3}[A-Z]{2}")
CONF_THRESH = 0.65

class State(Enum):
    EMPTY       = "EMPTY"
    APPROACHING = "APPROACHING"
    STOP        = "STOP"
    ANALYSIS    = "ANALYSIS"


def bbox_is_stable(a, b, thresh):
    return all(abs(x - y) < thresh for x, y in zip(a, b))


def analyze(crop, entering):
    plate_text = process_crop_image(crop)
    
    if not plate_text:
        print("\t--> Analysis aborted: No valid plate text extracted.")
        return
    
    try:
        # Verifica targa nel DB
        resp = session.get(f"{BASE_URL}/plate", params={"plate_text": plate_text})
        if resp.status_code != 200:
            print(f"\t--> Targa {plate_text} non trovata")
            return

        plate = resp.json()
        # FIX 3: campo corretto è is_active, non active
        if not plate["is_active"]:
            print(f"\t--> Targa {plate_text} not active")
            return

        # Verifica metodo di pagamento
        payment = session.get(
            f"{BASE_URL}/user/payment",
            params={"account_id": plate["account_id"]}
        )
        if payment.status_code != 200:
            print(f"\t--> Payment method not found for: {plate_text}")

        # FIX 4: call gate/entry (non /paying direttamente)
        # gate/entry gestisce MQTT, contatori disabili e doppio ingresso
        res = session.post(
            f"{BASE_URL}/gate/entry",
            json={"plate_text": plate_text}
        )
        if res.status_code == 200:
            data = res.json()
            msg  = f"Success! Session started for plate {plate_text}"
            if data.get("used_disabled_slot"):
                msg += " [disabled slot]"
            print(f"\t--> {msg}")
        else:
            print(f"\t--> Gate entry failed: {res.text}")  
     
    except Exception as e:
        print(f"\t--> Network error during analysis: {e}")
                  

def run_webcam_old():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print(f"[error] Not able to open the camera (index={CAMERA_INDEX})")
        return

    print("[webcam] Started — Press Q to exit, S to save the frame.")

    frame_count  = 0
    state        = State.EMPTY
    last_bbox    = None
    stable_count = 0
    cooldown     = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[error] Frame not received.")
            break

        frame_count += 1

        if cooldown > 0:
            cooldown -= 1
        else:
            results     = yolo_model.predict(source=frame, verbose=False)
            found_boxes = []
            for result in results:
                if result.boxes is None:
                    continue
                for box in result.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                    found_boxes.append((x1, y1, x2, y2))

            plate_detected = len(found_boxes) > 0

            # --- Macchina a stati ---

            if state == State.EMPTY:
                if plate_detected:
                    print("EMPTY -> APPROACHING")
                    state        = State.APPROACHING
                    last_bbox    = found_boxes[0]
                    stable_count = 0

            elif state == State.APPROACHING:
                if not plate_detected:
                    print("APPROACHING -> EMPTY (lost plate)")
                    state = State.EMPTY
                else:
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

                # FIX 1: fullmatch invece di findall — evita match parziali
                if not plate_text or not PLATE_PATTERN.fullmatch(plate_text):
                    print(f"\t--> Not valid plate format: {plate_text!r}")
                    # FIX 2: NON fare break — torna a EMPTY e continua la webcam
                    state    = State.EMPTY
                    cooldown = COOLDOWN_FRAMES
                    continue

                # Verifica targa nel DB
                resp = session.get(f"{BASE_URL}/plate", params={"plate_text": plate_text})
                if resp.status_code != 200:
                    print(f"\t--> Targa {plate_text} non trovata")
                    state    = State.EMPTY
                    cooldown = COOLDOWN_FRAMES
                    continue

                plate = resp.json()

                # FIX 3: campo corretto è is_active, non active
                if not plate["is_active"]:
                    print(f"\t--> Targa {plate_text} not active")
                    state    = State.EMPTY
                    cooldown = COOLDOWN_FRAMES
                    continue

                # Verifica metodo di pagamento
                payment = session.get(
                    f"{BASE_URL}/user/payment",
                    params={"account_id": plate["account_id"]}
                )
                if payment.status_code != 200:
                    print(f"\t--> Payment method not found for: {plate_text}")
                    state    = State.EMPTY
                    cooldown = COOLDOWN_FRAMES
                    continue

                # FIX 4: call gate/entry (non /paying direttamente)
                # gate/entry gestisce MQTT, contatori disabili e doppio ingresso
                res = session.post(
                    f"{BASE_URL}/gate/entry",
                    json={"plate_text": plate_text}
                )
                if res.status_code == 200:
                    data = res.json()
                    msg  = f"Success! Session started for plate {plate_text}"
                    if data.get("used_disabled_slot"):
                        msg += " [disabled slot]"
                    print(f"\t--> {msg}")
                else:
                    print(f"\t--> Gate entry failed: {res.text}")

                print("ANALYSIS -> EMPTY")
                state    = State.EMPTY
                cooldown = COOLDOWN_FRAMES

        # --- HUD ---
        cv2.putText(frame, f"Stato: {state.value}  Cooldown: {cooldown}",
                    (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)
        cv2.putText(frame, "Q=esci  S=salva",
                    (10, 48), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)
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

def run_webcam_gemini():
    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_V4L2)
    if not cap.isOpened():
        print(f"[error] Not able to open the camera (index={CAMERA_INDEX})")
        return

    print("[webcam] Started — Press Q to exit, S to save the frame.")

    # Force the window to initialize properly before the heavy loop starts
    cv2.namedWindow("Webcam — License Plate Detector", cv2.WINDOW_AUTOSIZE)

    frame_count  = 0
    state        = State.EMPTY
    last_bbox    = None
    stable_count = 0
    cooldown     = 0
    
    # Store found boxes so they persist during skipped frames
    found_boxes  = [] 

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[error] Frame not received.")
            break

        frame_count += 1

        if cooldown > 0:
            cooldown -= 1
        else:
            # FIX 1: Run YOLO only every 3rd frame to prevent the GUI from freezing
            if frame_count % 3 == 0:
                detection = yolo_model.predict(source=frame, verbose=False)
                found_boxes = [] # Reset and update boxes
                for result in detection:
                    if result.boxes is None:
                        continue
                    for box in result.boxes:
                        if box.conf.item() > CONF_THRESH:
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                            found_boxes.append((x1, y1, x2, y2))

            plate_detected = len(found_boxes) > 0

            # --- Macchina a stati ---

            if state == State.EMPTY:
                if plate_detected:
                    print("EMPTY -> APPROACHING")
                    state        = State.APPROACHING
                    last_bbox    = found_boxes[0]
                    stable_count = 0

            elif state == State.APPROACHING:
                if not plate_detected:
                    print("APPROACHING -> EMPTY (lost plate)")
                    state = State.EMPTY
                else:
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
                x1, y1, x2, y2 = last_bbox
                
                plate_crop = frame[y1:y2, x1:x2]
                
                analyze(plate_crop, True)
                # threading.Thread(target=analyze, args=(plate_crop.copy(), True), daemon=True).start()
                print("ANALYSIS -> EMPTY")
                state    = State.EMPTY
                cooldown = COOLDOWN_FRAMES

        # --- HUD ---
        cv2.putText(frame, f"State: {state.value}  Cooldown: {cooldown}",
                    (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (250, 250, 250), 2)
        cv2.putText(frame, "Q=Exit  S=Save",
                    (10, 48), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (250, 250, 250), 2)
        
        cv2.line(frame, (frame.shape[1] // 2, 0), (frame.shape[1] // 2, frame.shape[0]), 
                    (250, 250, 250), 2)
        cv2.putText(frame, "Entrance", (0, frame.shape[0] - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 236, 155), 2)        
        cv2.putText(frame, "Exit", (frame.shape[1] // 2 + 10, frame.shape[0] - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (77, 0, 255), 2)        
        
        cv2.imshow("Webcam — License Plate Detector", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            path = f"Debug/frame_{frame_count:05d}.jpg"
            cv2.imwrite(path, frame)
            print(f"[save] Frame salvato -> {path}")
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    run_webcam_gemini()
