from flask import Flask, send_from_directory, request, jsonify
import requests

app = Flask(__name__, static_folder="public")

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")
@app.route('/api/send-to-telegram', methods=['POST'])
def send_to_telegram():
    bot_token = "6847127004:AAHJ8N5td3PAm40KJh2kY_2rMoCI72th4qg"
    chat_id = "719874188"

    data = request.json
    if not data or 'name' not in data or 'message' not in data:
        return jsonify({"error": "Пожалуйста, заполните name и message"}), 400

    telegram_message = f"""
    📝 Новое сообщение
    👤 Имя: {data['name']}
    💬 Сообщение: {data['message']}
    """
    response = requests.post(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        json={"chat_id": chat_id, "text": telegram_message}
    )
    return jsonify({"success": True}) if response.status_code == 200 else jsonify({"error": "Ошибка отправки!"}), 500

from flask_compress import Compress

Compress(app)

import logging
logging.basicConfig(level=logging.DEBUG)
