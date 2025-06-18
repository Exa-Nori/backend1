from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import logging
from functools import wraps
import os
import requests

# Инициализация приложения
app = Flask(__name__, static_folder='static')
CORS(app)  # Разрешаем CORS для всех доменов (в разработке)

# Конфигурация
app.config.update(
    SECRET_KEY=os.getenv('FLASK_SECRET_KEY', 'dev-secret-key'),
    TELEGRAM_BOT_TOKEN=os.getenv('TELEGRAM_BOT_TOKEN'),
    TELEGRAM_CHAT_ID=os.getenv('TELEGRAM_CHAT_ID')
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def json_response(f):
    """Декоратор для стандартизации JSON-ответов"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
            return jsonify({
                "status": "success",
                "data": result
            })
        except ValueError as e:
            logger.warning(f"Ошибка валидации: {str(e)}")
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 400
        except Exception as e:
            logger.error(f"Ошибка сервера: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "Internal server error"
            }), 500
    return wrapper

@app.route('/')
def serve_index():
    """Главная страница"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/health')
def health_check():
    """Проверка работоспособности API"""
    return jsonify({"status": "healthy"})

@app.route('/api/services', methods=['GET'])
@json_response
def get_services():
    """Получение списка услуг"""
    return {
        "services": [
            {"id": 1, "name": "Уход за пожилыми", "icon": "elderly"},
            {"id": 2, "name": "Медицинский уход", "icon": "medical_services"},
            {"id": 3, "name": "Бытовая помощь", "icon": "home"},
            {"id": 4, "name": "Психологическая поддержка", "icon": "psychology"}
        ]
    }

@app.route('/api/contact', methods=['POST'])
@json_response
def send_contact_message():
    """Обработка контактной формы"""
    # Получаем данные в формате JSON или form-data
    data = request.get_json() if request.is_json else request.form
    
    # Валидация
    required_fields = ['name', 'email', 'message']
    if not all(field in data for field in required_fields):
        raise ValueError("Не заполнены все обязательные поля")

    # Отправка в Telegram
    text = f"""
    📩 Новый контакт с сайта:
    ├ Имя: {data['name']}
    ├ Email: {data['email']}
    └ Сообщение: {data['message']}
    """
    
    telegram_url = f"https://api.telegram.org/bot{app.config['TELEGRAM_BOT_TOKEN']}/sendMessage"
    response = requests.post(
        telegram_url,
        json={
            "chat_id": app.config['TELEGRAM_CHAT_ID'],
            "text": text,
            "parse_mode": "HTML"
        },
        timeout=10
    )
    response.raise_for_status()

    return {"message": "Ваше сообщение успешно отправлено"}

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "status": "error",
        "message": "Ресурс не найден"
    }), 404

if __name__ == '__main__':
    # Запуск сервера
    app.run(
        host=os.getenv('FLASK_HOST', '0.0.0.0'),
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=os.getenv('FLASK_DEBUG', 'False') == 'True'
    )

    