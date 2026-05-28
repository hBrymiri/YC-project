import subprocess
def webcam_acess(camera):
    from flask import Flask
    import subprocess 
    
    
    def start_camera(button_pressed,click_button):
        
      if button_pressed == "camera":
       subprocess.Popen(["python3", "Frontend/project.py"])
      
   def low_battery_check(battery-status):
       if battery-status <="20%":
          print("Battery to low , camera is disabled.")
          return 
      if click_button== "camera":
          subprocess.Popen(["python3", "Frontend/project.py"])