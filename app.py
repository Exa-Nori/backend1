from flask import Flask, request, jsonify, send_from_directory
import requests
import logging
from functools import wraps

app = Flask(__name__)

# Настройка логов
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфиг Telegram
TELEGRAM_BOT_TOKEN = "7585621279:AAFLcwzw-lrh5PCHvgGZqZ6lG-TIPlwXZZo"
TELEGRAM_CHAT_ID = "719874188"

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

@app.route('/')# Главная страница
def index():
    return send_from_directory(app.static_folder, 'index.html')

# API роут
@app.route('/api/services', methods=['GET'])
def services():
    return jsonify({
        'services': [
            "Уход за пожилыми",
            "Медицинский уход",
            "Бытовая помощь",
            "Психологическая поддержка"
        ]
    })

@app.route('/send_message', methods=['POST'])
@json_response
def send_message():
    data = request.get_json() if request.is_json else request.form
    
    # Проверка полей
    required = ['name', 'email', 'message']
    if not all(k in data for k in required):
        raise ValueError("Не заполнены все поля")

    # Отправка в Telegram
    text = f"""
    📩 Новое сообщение:
    Имя: {data['name']}
    Email: {data['email']}
    Сообщение: {data['message']}
    """
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    response = requests.post(url, json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text
    }, timeout=10)
    
    response.raise_for_status()
    return {"message": "Сообщение отправлено"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


    