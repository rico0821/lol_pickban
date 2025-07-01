import os
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS
import traceback
if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    from utils.lol_api import LoLDataDragonAPI
else:
    from backend.utils.lol_api import LoLDataDragonAPI

app = Flask(__name__)
CORS(app)
lol_api = LoLDataDragonAPI()

@app.before_request
def log_request_info():
    print(f"[backend] {request.method} {request.path}")

@app.route('/api/data')
def get_data():
    return jsonify({'message': 'Hello from Flask!'})

@app.route('/api/champions')
def get_champions():
    try:
        champions_data = lol_api.get_champions()
        return jsonify({
            "success": True,
            "champions": champions_data["champions"],
            "count": champions_data["count"]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    try:
        port = 5001  # Hardcoded for integration/test
        print(f"[backend] FORCED: Flask app will always run on port {port} (cwd={os.getcwd()})")
        app.run(debug=True, host='0.0.0.0', port=port)
    except Exception as e:
        print(f"[backend] FATAL ERROR: {e}")
        traceback.print_exc()
        sys.exit(2) 