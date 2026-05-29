import subprocess
from flask import Flask

def webcam_acess(camera):
    def start_camera(button_pressed, click_button):
        if button_pressed == "camera":
            subprocess.Popen(["python3", "Frontend/project.py"])
    
    
    def low_battery_check(battery_status):
        if battery_status <= "20%":
            print("Battery to low , camera is disabled.")
            return
    
    def click_button_camera():
        subprocess.Popen(["python3", "Frontend/project.py"])

# Main function called when camera button is clicked
def click_button_camera():
    """Start the camera when the button is clicked"""
    subprocess.Popen(["python3", "Frontend/project.py"])

@app.route('/start-camera',methods=['POST'])
  try :
    click-button()
    return jsonify({'message': 'camera is live '})
except exceptin as e:
    return jsonify({'error':stre(e)}),500