import sys
import os
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
import subprocess
#app.py connects the camera/input, the recognition logic, and the database, then runs the app.

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Ensure the BackWeb package is in the PYTHONPATH
base_dir = os.path.dirname(os.path.abspath(__file__)) # Get the base directory of the current file
if not os.path.isdir(base_dir):
    raise ImportError("BackEnd package not found.")

app = Flask(__name__, static_folder='../frontEnd', static_url_path='/')

PROJECT_ROOT = Path(__file__).resolve().parent.parent
UNKNOWN_DIR = PROJECT_ROOT / 'SubDocu' / 'UnknownFolder'
KNOWN_DIR = PROJECT_ROOT / 'SubDocu' / 'KnownFolder'
APPROVED_DIR = KNOWN_DIR / 'Approved'

@app.route('/', methods=['GET'])
@app.route('/project.html', methods=['GET'])
@app.route('/cameraRun.py', methods=['GET'])
def index():
    return app.send_static_file('project.html')

@app.route('/new-users')
def new_users():
    return app.send_static_file('NewUsers.html')

@app.route('/start-camera', methods=['POST'])
def start_camera():
    script_path = os.path.join(os.path.dirname(__file__), 'cameraRUn.py')
    subprocess.Popen(["python3", script_path])
    return jsonify({'message': 'Camera started successfully'})

@app.route('/api/new-users')
def api_new_users():
    files = []
    if UNKNOWN_DIR.exists():
        files = [p.name for p in sorted(UNKNOWN_DIR.iterdir()) if p.is_file() and p.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp'}]
    return jsonify({'items': files})

@app.route('/api/verified-users')
def api_verified_users():
    files = []
    if APPROVED_DIR.exists():
        files = [p.name for p in sorted(APPROVED_DIR.iterdir()) if p.is_file() and p.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp'}]
    return jsonify({'items': files})

@app.route('/api/approve-user', methods=['POST'])
def api_approve_user():
    data = request.get_json() or {}
    filename = data.get('filename')
    if not filename:
        return jsonify({'error': 'filename required'}), 400
    src = UNKNOWN_DIR / filename
    if not src.exists():
        return jsonify({'error': 'file not found'}), 404
    APPROVED_DIR.mkdir(parents=True, exist_ok=True)
    dest = APPROVED_DIR / filename
    src.rename(dest)
    return jsonify({'success': True})

@app.route('/images/unknown/<path:filename>')
def unknown_image(filename):
    return send_from_directory(str(UNKNOWN_DIR), filename)

@app.route('/images/verified/<path:filename>')
def verified_image(filename):
    return send_from_directory(str(APPROVED_DIR), filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
    
@app.route("/camera",methods=["POST"]) # type: ignore
def camera(Start_camera,Stop_camera):
    action=request.form.get("cameraButton")
    if action=="Stop Camera":
      Stop_camera()
    return "Camera Stopped"
    return " No Action Takken"
    