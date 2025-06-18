from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS  # Импорт CORS
import requests
import logging
from functools import wraps
import os

app = Flask(__name__, static_folder='static')
CORS(app)  # Включение CORS для всех доменов

# Настройка логов
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфиг Telegram
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_TOKEN', '7585621279:AAFLcwzw-lrh5PCHvgGZqZ6lG-TIPlwXZZo')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '719874188')

def json_response(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
            return jsonify({"status": "success", **result})
        except Exception as e:
            logger.error(f"Ошибка: {str(e)}")
            return jsonify({"status": "error", "message": str(e)}), 500
    return wrapper

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/services', methods=['GET'])
def get_services():
    return jsonify({
        'services': [
            "Уход за пожилыми",
            "Медицинский уход",
            "Бытовая помощь",
            "Психологическая поддержка"
        ]
    })

@app.route('/api/send_message', methods=['POST'])
@json_response
def send_message():
    # Разрешаем JSON и form-data
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    # Проверка полей
    required = ['name', 'email', 'message']
    if not all(k in data for k in required):
        raise ValueError("Не заполнены все обязательные поля")

    # Отправка в Telegram
    text = f"""
    📩 Новое сообщение:
    Имя: {data['name']}
    Email: {data['email']}
    Сообщение: {data['message']}
    """
    
    try:
        response = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": text,
                "parse_mode": "HTML"
            },
            timeout=10
        )
        response.raise_for_status()
        return {"message": "Сообщение успешно отправлено"}
    except requests.exceptions.RequestException as e:
        logger.error(f"Telegram API error: {str(e)}")
        raise Exception("Ошибка при отправке сообщения в Telegram")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

    