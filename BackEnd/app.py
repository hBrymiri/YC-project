import sys
import os
from flask import Flask, jsonify

#app.py connects the camera/input, the recognition logic, and the database, then runs the app.

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Ensure the BackWeb package is in the PYTHONPATH
base_dir = os.path.dirname(os.path.abspath(__file__)) # Get the base directory of the current file
if not os.path.isdir(base_dir):# Check if the base directory exists
    raise ImportError("BackEnd package not found.") # Ensure the BackEnd package is in the PYTHONPATH



base_dir=os.path.dirname(os.path.abspath(__file__)) # Get the base directory of the current file
# Check if the BackEnd package is correctly structured
if not os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'BackEnd')):
    raise ImportError("BackEnd package not found.")

# Initialize Flask app
app = Flask(__name__, static_folder='../frontEnd', static_url_path='/')

# Import camera functions
from webcame import click_button_camera

@app.route('/start-camera', methods=['POST'])
def start_camera():
    try:
        click_button_camera()
        return jsonify({'message': 'Camera started successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
