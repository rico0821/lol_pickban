from flask import Flask, jsonify
from backend.utils.lol_api import LoLDataDragonAPI

app = Flask(__name__)
lol_api = LoLDataDragonAPI()

@app.route('/api/data')
def get_data():
    return jsonify({'message': 'Hello from Flask!'})

@app.route('/api/champions')
def get_champions():
    try:
        champions_data = lol_api.get_champions()
        return jsonify(champions_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 