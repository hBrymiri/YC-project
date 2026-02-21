import cv2
import mediapipe as mp
import os
from datetime import datetime
import audioReg
import shutil
import numpy as np
# Enrollment (add new person) settings
from pathlib import Path                 # number of images to capture for angles
ENROLL_INTERVAL_SEC = 0.25        # time between shots
ENROLL_MIN_FACE_SIZE = 80         # ignore tiny faces during enroll
KNOWN_DIR = Path("SubDocu/KnownFolder")
UNKNOWN_DIR = Path("SubDocu/UnknownFolder")
ENROLL_SHOTS = 5
pending_unknown_face = None       # will store last unknown face bbox/emb

person_dir = UNKNOWN_DIR("unknowns")  # Define person_dir
name = person_dir


class UnknownFaceCapture:
    def __init__(self, video_dir="videos", snapshot_dir="snapshots"):
        self.video_dir = video_dir
        self.snapshot_dir = snapshot_dir
        os.makedirs(self.video_dir, exist_ok=True) # Create video directory if it doesn't exist
        os.makedirs(self.snapshot_dir, exist_ok=True) # Create snapshot directory if it doesn't exist
        

    def capture(self, image):
        ts=datetime.now().strftime("%Y%m%d_%H%M%S") # Timestamp for unique filenames
        path=os.path.join(self.snapshot_dir, f"unknown_{ts}.jpg") # Path for saving the snapshot
        cv2.imwrite(path, image) # Save the image to the specified path
        return "unknown saved to file"
    

class Face_reg: # Face recognition and unknown face capture
    def __init__(self): # Initialize the face detector and unknown face capture
        self.face_detector = mp.solutions.face_detection.FaceDetection(
            model_selection=0,
            min_detection_confidence=0.5
        )
        self.unknown_capture = UnknownFaceCapture(video_dir="videos", snapshot_dir="snapshots")

    def detect_faces(self, image): # Detect faces in the given image
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_detector.process(image_rgb)
        return results.detections or []

    def has_face(self, image) -> bool: # Check if there is at least one face in the image 
        return len(self.detect_faces(image)) > 0
    
    def Add_unknown(self, image): # Capture and save unknown face
        person_dir = UNKNOWN_DIR  / "unknowns"
        ensure_dir=(person_dir)
        
        print(f"\n[ENROLL] Look at camera and slowly turn your head in all directions{ENROLL_SHOTS} shots for{name}..\n")
        shots=0
        last=0
        
        def liten_for_known_voice(know_name):
            r = sr.Recognizer()
            with sr.Microphone() as source:
                print(f"listening..")
                audio = audioReg.Listen(source)
                
                try:
                    text=r.recognize_google(audio).lower()
                    print(f" confimed {name} is known")
                    
                    for names in known_names:
                        if names.lower() in spoken:
                            print(f"confirmed {name} is known")
                            return name
                
    
        
    
    
