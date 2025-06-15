from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

# Ścieżka do folderu AppData\Local\Spedycja
if os.name == 'nt':  # Windows
    APPDATA_DIR = os.path.join(os.getenv('LOCALAPPDATA'), 'Spedycja')
else:  # Linux (Render)
    APPDATA_DIR = '/data'

os.makedirs(APPDATA_DIR, exist_ok=True)


# Pełne ścieżki do plików danych
DATA_FILES = {
    'zlecenia': os.path.join(APPDATA_DIR, 'zlecenia.json'),
    'kontrahenci': os.path.join(APPDATA_DIR, 'kontrahenci.json'),
    'kierowcy': os.path.join(APPDATA_DIR, 'kierowcy.json'),
    'ciezarowki': os.path.join(APPDATA_DIR, 'ciezarowki.json'),
    'naczepy': os.path.join(APPDATA_DIR, 'naczepy.json'),
    'transport': os.path.join(APPDATA_DIR, 'transport_data.json')
}

# Tworzenie pustych plików, jeśli nie istnieją
def init_data_files():
    for file_path in DATA_FILES.values():
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                json.dump([], f)

init_data_files()

# Endpoint zdrowia serwera
@app.route('/ping', methods=['GET'])
def ping():
    return "OK", 200

# Pobieranie danych
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

# Dodawanie danych
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

    # Automatyczne nadanie lp dla zlecenia
    if module == 'zlecenia':
        max_lp = max((item.get("lp", 0) for item in data), default=0)
        new_data["lp"] = max_lp + 1

    data.append(new_data)
    with open(DATA_FILES[module], 'w') as f:
        json.dump(data, f, indent=2)
    return jsonify({'status': 'success'}), 201

# Aktualizacja danych po polu lp
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

# Usuwanie danych po polu lp
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

# Nowa funkcja – zamiana całej listy danych
@app.route('/<module>', methods=['PUT'])
def replace_all_data(module):
    if module not in DATA_FILES:
        return jsonify({'error': 'Nieprawidłowy moduł'}), 404
    new_data = request.json
    if not isinstance(new_data, list):
        return jsonify({'error': 'Dane muszą być listą'}), 400
    with open(DATA_FILES[module], 'w') as f:
        json.dump(new_data, f, indent=2)
    return jsonify({'status': 'replaced'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
