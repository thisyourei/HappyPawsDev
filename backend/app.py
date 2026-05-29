from flask import Flask, send_from_directory
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, '..', 'home')

app = Flask(__name__, static_folder=None)

@app.route('/')
def index():
    return send_from_directory(STATIC_DIR, 'index.html')

@app.route('/assets/<path:filename>')
def assets(filename):
    return send_from_directory(os.path.join(STATIC_DIR, 'assets'), filename)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
