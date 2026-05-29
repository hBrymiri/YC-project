import subprocess

import cv2
from flask import Flask, jsonify,exception
app=Flask(__name__)

def webcam_acess(camera):
    def start_camera(button_pressed, click_button):
        if button_pressed == "camera":
            subprocess.Popen(["python3", "Frontend/project.py"])

def start_camera_and_record():
    cap = cv2.VideoCapture(0)
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
        if battery_status <= "20%":
            print("Battery to low , camera is disabled.")
            return

# Main function called when camera button is clicked
def click_button_camera():
    """Start the camera when the button is clicked"""
    subprocess.Popen(["python3", "Frontend/project.py"])
    
    

@app.route('/start-camera',methods=['POST'])
def start_camera():
  try :
    click_button_camera()
    return jsonify({'message': 'camera is live '})
  except exception as e:
    return jsonify({'error':str(e)}),500   