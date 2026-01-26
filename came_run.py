
import os
import time

import math
import subprocess
from pathlib import Path
from datetime import datetime

import cv2
import numpy as np
from insightface.app import FaceAnalysis
from pathlib import Path

KNOWN_DIR = Path("SubDocu/KnownFolder")
UNKNOWN_DIR = Path("SubDocu/UnknownFolder")

MAX_PICTURES=5 # limit number of pictures taken
pictures_taken=0
MAX_VidLen=180 # limit video length in seconds
vid_taken=0
# ----------------------------
# Config
# ----------------------------
print("SubDocu/KnownFolder:", KNOWN_DIR.resolve())
print("SubDocu/UnknownFolder:", UNKNOWN_DIR.resolve())

CAM_INDEX = 0
FRAME_SCALE = 1.0  # set to 0.75 or 0.5 if you need speed

# Cosine similarity threshold: higher = stricter
# Typical range: 0.30–0.55 depending on your data; start here and tune.
MATCH_THRESHOLD = 0.45

# Unknown capture settings
UNKNOWN_COOLDOWN_SEC = 8       # avoid saving the same unknown every frame
UNKNOWN_VIDEO_SECONDS = 4      # clip length
UNKNOWN_FPS = 20              # video fps
UNKNOWN_MIN_FACE_SIZE = 60     # ignore tiny faces

# Speak cooldown per identity
SPEAK_COOLDOWN_SEC = 3

# ----------------------------
# Helpers
# ----------------------------
def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    a = a / (np.linalg.norm(a) + 1e-9)
    b = b / (np.linalg.norm(b) + 1e-9)
    return float(np.dot(a, b))

def mac_say(text: str):
    # Non-blocking-ish call (still spawns process)
    try:
        subprocess.Popen(["say", text])
    except Exception:
        pass

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def now_stamp():
    dt = datetime.now()
    date_dir = dt.strftime("%Y-%m-%d")
    ts = dt.strftime("%H%M%S")
    return date_dir, ts

# ----------------------------
# Load face model
# ----------------------------
# providers: CPU is simplest. If you later want speedups, you can explore CoreML/Metal options.
app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
app.prepare(ctx_id=0, det_size=(640, 640))

# ----------------------------
# Build known embeddings database
# ----------------------------
def build_known_db():
    known = []  # list of (name, embedding)
    if not KNOWN_DIR.exists():
        print(f"Known dir not found: {KNOWN_DIR.resolve()}")
        return known

    for person_dir in KNOWN_DIR.iterdir():
        if not person_dir.is_dir():
            continue
        name = person_dir.name
        for img_path in person_dir.glob("*"):
            if img_path.suffix.lower() not in [".jpg", ".jpeg", ".png", ".webp"]:
                continue
            img = cv2.imread(str(img_path))
            if img is None:
                continue
            faces = app.get(img)
            if not faces:
                print(f"[WARN] No face found in {img_path}")
                continue
            # Take the largest face
            face = max(faces, key=lambda f: (f.bbox[2]-f.bbox[0])*(f.bbox[3]-f.bbox[1]))
            emb = face.embedding.astype(np.float32)
            known.append((name, emb))
    print(f"Loaded {len(known)} known face embeddings.")
    return known

known_db = build_known_db()

if not known_db:
    print("\nNo known faces loaded. Add images to known/<Name>/ and rerun.\n")

# ----------------------------
# Webcam loop
# ----------------------------
cap = cv2.VideoCapture(CAM_INDEX)
if not cap.isOpened():
    raise RuntimeError("Could not open webcam.")

last_unknown_saved_at = 0.0
last_spoken_at = {}  # name -> time

def recognize_face(emb: np.ndarray):
    """Return (best_name, best_sim) or (None, best_sim) if no match."""
    best_name = None
    best_sim = -1.0
    for name, kemb in known_db:
        sim = cosine_sim(emb, kemb)
        if sim > best_sim:
            best_sim = sim
            best_name = name
    if best_sim >= MATCH_THRESHOLD:
        return best_name, best_sim
    return None, best_sim

def record_unknown_video(out_path: Path, frame_size, fps=20, seconds=4):
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    vw = cv2.VideoWriter(str(out_path), fourcc, fps, frame_size)
    if not vw.isOpened():
        print("[WARN] Could not open video writer.")
        return
    start = time.time()
    while time.time() - start < seconds:
        ok, fr = cap.read()
        if not ok:
            break
        if FRAME_SCALE != 1.0:
            fr = cv2.resize(fr, (0, 0), fx=FRAME_SCALE, fy=FRAME_SCALE)
        vw.write(fr)
    vw.release()

while True:
    ok, frame = cap.read()
    if not ok:
        break

    if FRAME_SCALE != 1.0:
        frame = cv2.resize(frame, (0, 0), fx=FRAME_SCALE, fy=FRAME_SCALE)

    faces = app.get(frame)

    for f in faces:
        x1, y1, x2, y2 = map(int, f.bbox)
        w, h = x2 - x1, y2 - y1
        if w < UNKNOWN_MIN_FACE_SIZE or h < UNKNOWN_MIN_FACE_SIZE:
            continue

        emb = f.embedding.astype(np.float32)
        name, sim = recognize_face(emb)

        if name is not None: # known face
            label = f"{name} ({sim:.2f})"
            # speak name with cooldown
            t = time.time()
            if t - last_spoken_at.get(name, 0.0) > SPEAK_COOLDOWN_SEC:
                mac_say(name)
                last_spoken_at[name] = t
        else:
            
            label = f"Unknown ({sim:.2f})" # unknown face
            t = time.time()
            if pictures_taken<MAX_PICTURES: # limit number of pictures taken
                cv2.writte(str(img_path), frame)
                pictures_taken+=1
            if  t - last_unknown_saved_at > UNKNOWN_COOLDOWN_SEC:# save unknown with cooldown
                date_dir, ts = now_stamp()
                out_dir = UNKNOWN_DIR / date_dir
                ensure_dir(out_dir)

                # Save full frame photo
                img_path = out_dir / f"{ts}_unknown.jpg"
                cv2.imwrite(str(img_path), frame)
                

                # Save face crop too (helpful for review)
                face_crop = frame[max(0,y1):max(0,y2), max(0,x1):max(0,x2)]
                crop_path = out_dir / f"{ts}_face.jpg"
                if face_crop.size > 0:
                    cv2.imwrite(str(crop_path), face_crop)

                # Record short clip
                h0, w0 = frame.shape[:2]
                if vid_taken>0:
                    MAX_VidLen =min(UNKNOWN_VIDEO_SECONDS,vid_taken)
                vid_path = out_dir / f"{ts}_unknown.mp4"
                
                record_unknown_video(vid_path, frame_size=(w0, h0), fps=UNKNOWN_FPS, seconds=MAX_VidLen)
                vid_taken+=MAX_VidLen
            else:
                print(f"[SAVED] Unknown -> {img_path.name}, {vid_path.name}")
                last_unknown_saved_at = t

        # draw box + label
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0) if name else (0, 0, 255), 2)
        cv2.putText(frame, label, (x1, max(0, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

    cv2.imshow("Face Recognizer (q to quit)", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()