from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

DATA_FILES = {
    'zlecenia': 'zlecenia.json',
    'kontrahenci': 'kontrahenci.json',
    'kierowcy': 'kierowcy.json',
    'ciezarowki': 'ciezarowki.json',
    'naczepy': 'naczepy.json',
    'transport': 'transport_data.json'
}

def init_data_files():
    for file in DATA_FILES.values():
        if not os.path.exists(file):
            with open(file, 'w') as f:
                json.dump([], f)

init_data_files()

@app.route('/ping', methods=['GET'])
def ping():
    return "OK", 200

@app.route('/<module>', methods=['GET'])
def get_data(module):
    if module not in DATA_FILES:
        return jsonify({'error': 'Nieprawidłowy moduł'}), 404
    try:
        with open(DATA_FILES[module], 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        data = []
    return jsonify(data)

@app.route('/<module>', methods=['POST'])
def add_data(module):
    if module not in DATA_FILES:
        return jsonify({'error': 'Nieprawidłowy moduł'}), 404
    new_data = request.json
    try:
        with open(DATA_FILES[module], 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        data = []

    # ✅ Automatyczne nadanie unikalnego lp tylko dla zleceń
    if module == 'zlecenia':
        max_lp = max((item.get("lp", 0) for item in data if isinstance(item.get("lp", 0), int)), default=0)
        new_data["lp"] = max_lp + 1

    data.append(new_data)
    with open(DATA_FILES[module], 'w') as f:
        json.dump(data, f, indent=2)
    return jsonify({'status': 'success'}), 201

@app.route('/<module>/<int:lp>', methods=['PUT'])
def update_data(module, lp):
    if module not in DATA_FILES:
        return jsonify({'error': 'Nieprawidłowy moduł'}), 404
    updated = request.json
    try:
        with open(DATA_FILES[module], 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return jsonify({'error': 'Uszkodzony plik danych'}), 500
    for i, item in enumerate(data):
        if str(item.get("lp")) == str(lp):
            data[i] = updated
            with open(DATA_FILES[module], 'w') as f:
                json.dump(data, f, indent=2)
            return jsonify({'status': 'updated'})
    return jsonify({'error': f'Nie znaleziono rekordu o lp = {lp}'}), 404

@app.route('/<module>/<int:lp>', methods=['DELETE'])
def delete_data(module, lp):
    if module not in DATA_FILES:
        return jsonify({'error': 'Nieprawidłowy moduł'}), 404
    try:
        with open(DATA_FILES[module], 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return jsonify({'error': 'Uszkodzony plik danych'}), 500
    for i, item in enumerate(data):
        if str(item.get("lp")) == str(lp):
            data.pop(i)
            with open(DATA_FILES[module], 'w') as f:
                json.dump(data, f, indent=2)
            return jsonify({'status': 'deleted'})
    return jsonify({'error': f'Nie znaleziono rekordu o lp = {lp}'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
