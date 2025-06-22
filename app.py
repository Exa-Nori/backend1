from flask import Flask, send_from_directory, request, jsonify
import requests
import logging
from flask_compress import Compress

app = Flask(__name__, static_folder="public")
Compress(app)
logging.basicConfig(level=logging.DEBUG)

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route('/api/send-to-telegram', methods=['POST'])
def send_to_telegram():
    bot_token = "6847127004:AAHJ8N5td3PAm40KJh2kY_2rMoCI72th4qg"
    chat_id = "719874188"

    data = request.get_json()
    if not data or 'name' not in data or 'message' not in data:
        return jsonify({"error": "Пожалуйста, заполните name и message"}), 400

    telegram_message = f"""📝 Новое сообщение
👤 Имя: {data['name']}
💬 Сообщение: {data['message']}
"""
    response = requests.post(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        json={"chat_id": chat_id, "text": telegram_message}
    )
    # Логируем ответ Телеграма
    logging.debug(f"Telegram API Response: {response.status_code}, {response.text}")
    # Возвращаем текст ответа Telegram в error для отладки
    if response.status_code == 200:
        return jsonify({"success": True})
    else:
        return jsonify({"error": response.text}), 500

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, path)