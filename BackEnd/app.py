import sys
import os
from pathlib import Path
from time import time
from flask import Flask, jsonify, request, send_from_directory
import subprocess
from datetime import timedelta
import sqlite3
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

@app.route("/camera", methods=["POST"])
def camera():
    action = request.form.get("cameraButton")
    if action == "Stop Camera":
        return "Camera Stopped"
    return "No Action Taken"

@app.route("/loadUnverifiedUsers", methods=["POST"])
def load_unverified_users():
    status = "Pending"
    # this is where the unverified users will come from
    TheRavenDb()
    return jsonify({"status": status})

def TheRavenDb():
    # and this is where the unverified users will be stored.
    conn = sqlite3.connect('/Users/hbrymiri/YC project/BackEnd/storage.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    row = cursor.fetchone()
    print(row[0])
     
    return conn

if __name__ == '__main__':
    app.run(debug=True, port=5000)






