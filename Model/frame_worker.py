from enum import Enum
import queue

CONF_THRESH         = 0.65
STABLE_PIXEL_THRESH = 8
N_STABLE_FRAMES     = 8

class State(Enum):
    EMPTY       = "EMPTY"
    APPROACHING = "APPROACHING"
    STOP        = "STOP"
    ANALYSIS    = "ANALYSIS"
    
    
def bbox_is_stable(a, b, thresh):
    return all(abs(x - y) < thresh for x, y in zip(a, b))


def frame_worker(worker_name, frame_queue, ocr_queue, output_queue):
    state        = State.EMPTY
    last_bbox    = None
    stable_count = 0
    
    print(f"[worker] {worker_name} is ready")
    
    while True:
        task = frame_queue.get()
        
        if task is None:
            print(f"{worker_name}: Shutting down.")
            frame_queue.task_done()
            break
        
        detection, frame = task
        
        found_boxes = [] 
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
            
            reply_queue = queue.Queue(maxsize=1)
            
            try:
                ocr_queue.put_nowait((plate_crop, reply_queue))
                
                plate_text = reply_queue.get()
                
                if plate_text is not None:
                    print("ANALYSIS -> EMPTY")
                    state    = State.EMPTY
                    
                    try:
                        output_queue.put_nowait((plate_crop, worker_name, plate_text))
                    except queue.Full:
                        pass
                
            except queue.Full:
                print(f"{worker_name}: OCR queue is full, skipping analysis.")
                plate_text = None
                        
        
        frame_queue.task_done()