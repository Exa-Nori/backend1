from flask import Flask, send_from_directory, request, jsonify
import requests

app = Flask(__name__, static_folder="public")

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")
import json
from flask import Flask, request, jsonify
import requests

# Загрузка конфигурации из JSON
with open('config.json') as config_file:
    config = json.load(config_file)

BOT_TOKEN = config['telegram_token']
CHAT_ID = config['chat_id']

app = Flask(__name__)

@app.route('/api/send-to-telegram', methods=['POST'])
def send_to_telegram():
    data = request.json
    if not data or 'name' not in data or 'message' not in data:
        return jsonify({"error": "Поля name и message обязательны"}), 400

    telegram_message = f"📝 Новое сообщение\n👤 Имя: {data['name']}\n💬 Сообщение: {data['message']}"
    response = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": telegram_message}
    )

    if response.status_code == 200:
        return jsonify({"success": True}), 200
    else:
        return jsonify({"error": "Не удалось отправить сообщение"}), 500

if __name__ == '__main__':
    app.run()
    
from flask_compress import Compress

Compress(app)

import logging
logging.basicConfig(level=logging.DEBUG)

