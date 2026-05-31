import subprocess
import cv2

def start_camera_and_record():
    """Start camera and record video to output.avi"""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Cannot open camera")
    
    fourcc = cv2.VideoWriter_fourcc(*'XVID') # type: ignore
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)
        cv2.imshow('Recording', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

def low_battery_check(battery_status):
    """Check battery and disable camera if too low"""
    if battery_status <= "20%":
        print("Battery too low, camera is disabled.")
        return

    