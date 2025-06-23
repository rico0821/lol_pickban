import os
import sys
if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    from utils.lol_api import LoLDataDragonAPI
else:
    from backend.utils.lol_api import LoLDataDragonAPI
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
lol_api = LoLDataDragonAPI()

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
    port = int(os.environ.get("LOL_PICKBAN_PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port) 