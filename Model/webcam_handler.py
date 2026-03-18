from lpr_model import*

CAMERA_INDEX = 0    # 0 = integrata, 1 = USB
OCR_EVERY_N  = 10    # esegui OCR solo ogni N frame (alleggerisce il carico)

def run_webcam():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print(f"[error] Impossibile aprire la camera (index={CAMERA_INDEX})")
        return

    print("[webcam] Avviato — premi Q per uscire, S per salvare il frame.")

    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[error] Frame non ricevuto.")
            break

        frame_count += 1

        if frame_count % OCR_EVERY_N == 0:
            process_image(frame)


        # ── HUD ─────────────────────────────────────────────────────
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