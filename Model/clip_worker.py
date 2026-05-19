from ultralytics import YOLO
import queue

MODEL_PATH   = 'Model/yolov11x-license-plate.pt'

def clip_worker(worker_name, input_queue, entrance_queue, exit_queue):
    class Model:
        def __init__(self):
            print("[init] Loading YOLO model")
            self.yolo_model = YOLO(MODEL_PATH, verbose=False)
        
        def predict_batch(self, entrance_half, exit_half):
            batch = [entrance_half, exit_half]
            res = self.yolo_model.predict(source=batch, verbose=False)
            return res[0], res[1]
    
    model = Model()
    print(f"[worker] {worker_name} is ready")
    
    while True:
        task = input_queue.get()
        
        if task is None:
            print(f"[{worker_name}]: Shutting down.")
            input_queue.task_done()
            break
            
        entrance_frame, exit_frame = task
        
        # entrance_resized = cv2.resize(entrance_frame, (224, 224))
        # exit_resized = cv2.resize(exit_frame, (224, 224))
        
        # processed_entrance, processed_exit = model.predict_batch(entrance_resized, exit_resized)
        processed_entrance, processed_exit = model.predict_batch(entrance_frame, exit_frame)
        
        try:
            entrance_queue.put_nowait(([processed_entrance], entrance_frame))
        except queue.Full:
            print("\tWorker entrance is full")
                
        try:
            exit_queue.put_nowait(([processed_exit], exit_frame))
        except queue.Full:
            print("\tWorker exit is full")
            
        input_queue.task_done()