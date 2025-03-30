import os
import socket
import threading
from flask import Flask, request, send_from_directory, render_template, jsonify
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "shared_files"
HOST = '0.0.0.0'
PORT = 5001
BROADCAST_PORT = 5002

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
socketio = SocketIO(app, cors_allowed_origins="*")

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Auto-discovery Broadcast
def broadcast_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        while True:
            s.sendto(b"FILE_SERVER", ("255.255.255.255", BROADCAST_PORT))
            threading.Event().wait(5)  # Broadcast every 5 seconds

# Home Page - File List & Upload Form
@app.route('/')
def index():
    files = os.listdir(UPLOAD_FOLDER)
    return render_template('index.html', files=files)

# File Upload Route
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    socketio.emit('file_updated', filename)  # Notify clients
    return "File uploaded successfully", 200

# File Download Route
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# File Delete Route
@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        socketio.emit('file_deleted', filename)  # Notify clients
        return jsonify({"message": "File deleted"}), 200
    else:
        return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    threading.Thread(target=broadcast_server, daemon=True).start()
    socketio.run(app, host=HOST, port=PORT)
