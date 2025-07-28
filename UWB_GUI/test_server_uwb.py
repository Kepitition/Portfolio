from flask import Flask, request, jsonify
from threading import Lock

app = Flask(__name__)
latest_data = []
lock = Lock()

@app.route('/send', methods=['POST'])
def receive_data():
    global latest_data
    try:
        data = request.get_json()
        with lock:
            latest_data = data.get("distances", [])
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/get', methods=['GET'])
def send_latest():
    with lock:
        return jsonify({"distances": latest_data})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


