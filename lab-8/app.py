from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import json
import os

app = Flask(__name__)


# Настройка Flask-Limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per day"],     # общее ограничение: 100 запросов в сутки
    storage_uri="memory://"     # счётчики хранятся в оперативной памяти приложения
)


# Key-Value хранилище
DATA_FILE = "data.json"
data = {}

def load_data():    # Загрузка данных из файла при старте
    global data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}

def save_data():    # Сохранение данных в файл после каждой операции
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Загружаем данные при старте приложения
load_data()


# Маршруты API
@app.post("/set")
@limiter.limit("10 per minute")     # отдельный лимит для /set
def set_value():
    body = request.get_json()

    if not body or "key" not in body or "value" not in body:
        return jsonify({"error": "Нужно передать key и value"}), 400

    key = str(body["key"])
    value = body["value"]

    data[key] = value
    save_data()

    return jsonify({
        "message": "Значение сохранено",
        "key": key,
        "value": value
    }), 200


@app.get("/get/<key>")
@limiter.limit("100 per day")
def get_value(key):
    if key not in data:
        return jsonify({"error": "Ключ не найден"}), 404

    return jsonify({
        "key": key,
        "value": data[key]
    }), 200


@app.delete("/delete/<key>")
@limiter.limit("10 per minute")     # отдельный лимит для /delete
def delete_value(key):
    if key not in data:
        return jsonify({"error": "Ключ не найден"}), 404

    del data[key]
    save_data()

    return jsonify({
        "message": "Ключ удалён",
        "key": key
    }), 200


@app.get("/exists/<key>")
@limiter.limit("100 per day")
def exists_key(key):
    exists = key in data
    return jsonify({
        "key": key,
        "exists": exists
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)