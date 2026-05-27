import requests
import threading
import queue
import cv2

from paddle_worker import paddle_worker
from clip_worker import clip_worker
from frame_worker import frame_worker


CAMERA_INDEX    = 0   # 0 = integrata, 1 = USB
BASE_URL        = "http://127.0.0.1:8000/v1"
PARKING_ID      = 1
ENTRANCE_WORKER = "Entrance worker"
EXIT_WORKER     = "Exit worker"

session = requests.Session()


def analyze(plate_text, entering):
    
    if not plate_text:
        print("\t--> Analysis aborted: No valid plate text extracted.")
        return None
    
    try:
        resp = session.get(f"{BASE_URL}/plate", params={"plate_text": plate_text})
        if resp.status_code != 200:
            print(f"\t--> Targa {plate_text} non trovata")
            return None

        plate = resp.json()
        if not plate["is_active"]:
            print(f"\t--> Targa {plate_text} not active")
            return None

        payment = session.get(
            f"{BASE_URL}/user/payment",
            params={"account_id": plate["account_id"]}
        )
        if payment.status_code != 200:
            print(f"\t--> Payment method not found for: {plate_text}")

        if entering:
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
        else:
            res = session.post(
                f"{BASE_URL}/gate/exit",
                json={"plate_text": plate_text}
            )
            if res.status_code == 200:
                data = res.json()
                msg  = f"Success! Session ended for plate {plate_text}"
                if data.get("used_disabled_slot"):
                    msg += " [disabled slot]"
                print(f"\t--> {msg}")
            else:
                print(f"\t--> Gate exit failed: {res.text}")
     
    except Exception as e:
        print(f"\t--> Network error during analysis of {plate_text}: {e}")
                  
                  
def run_webcam():
    """Run the webcam and split the input between entrance and exit thread."""
    
    print("\nStarting all worker -----------------------------")
    
    input_queue = queue.Queue(maxsize=20)
    ocr_queue = queue.Queue(maxsize=20)
    entrance_queue = queue.Queue(maxsize=10)
    exit_queue = queue.Queue(maxsize=10)
    output_queue = queue.Queue(maxsize=20)
    
    clip_thread = threading.Thread(target=clip_worker, args=("Clip Worker", input_queue, entrance_queue, exit_queue, output_queue)).start()
    paddle_thread = threading.Thread(target=paddle_worker, args=("Paddle Worker", ocr_queue, output_queue), daemon=True).start()
    entrance_thread = threading.Thread(target=frame_worker, args=(ENTRANCE_WORKER, entrance_queue, ocr_queue, output_queue), daemon=True).start()
    exit_thread = threading.Thread(target=frame_worker, args=(EXIT_WORKER, exit_queue, ocr_queue, output_queue), daemon=True).start()
    
    for _ in range(4):
        output_queue.get()
        
    print("\n\nStarting webcam input ---------------------------")
    
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print(f"[error] Not able to open the camera (index={CAMERA_INDEX})")
        return

    print("[webcam] Started — Press Q to exit, S to save the frame.")

    cv2.namedWindow("Webcam — License Plate Detector", cv2.WINDOW_AUTOSIZE)
    
    frame_count  = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[error] Frame not received.")
            break

        frame_count += 1
        
        height, width, _ = frame.shape
        middle = width // 2

        if frame_count % 3 == 0:
            
            entrance_half = frame[:, :middle]
            exit_half = frame[:, middle:]
            
            try:
                input_queue.put_nowait((entrance_half, exit_half))
            except queue.Full:
                print("\tClip worker is full")
                
                
            while not output_queue.empty():
                try:
                    task = output_queue.get_nowait()
                    
                    plate_crop, worker_name, plate_text = task
                    
                    analyze(plate_text, worker_name == ENTRANCE_WORKER)
                        
                    cv2.imshow(worker_name + plate_text, plate_crop)
                except queue.Empty:
                    break
            
        
        cv2.line(frame, (middle, 0), (middle, height), (250, 250, 250), 2)
        cv2.putText(frame, "Entrance", (0, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 236, 155), 2)        
        cv2.putText(frame, "Exit", (middle + 10, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (77, 0, 255), 2)        
        
        cv2.imshow("Webcam — License Plate Detector", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("\n\nShutting down all worker ------------------------")
            try:
                input_queue.put(None, timeout=2)
                ocr_queue.put(None, timeout=2)
                entrance_queue.put(None, timeout=2)
                exit_queue.put(None, timeout=2)
            except queue.Full:
                print("[main] Warning: Queues are completely blocked during shutdown.")
            break
        elif key == ord('s'):
            path = f"Debug/frame_{frame_count:05d}.jpg"
            cv2.imwrite(path, frame)
            print(f"[save] Frame salvato -> {path}")
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    run_webcam()
