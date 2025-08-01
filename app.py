from flask import Flask, send_from_directory, request, jsonify
import requests
import logging
from flask_compress import Compress
import os
import re
from functools import wraps
from typing import Dict, Any, Optional
from config import get_config

# Получение конфигурации
Config = get_config()

app = Flask(__name__, static_folder="/www/lile-des-reves.com/")
Compress(app)

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Валидаторы
def validate_phone(phone: str) -> bool:
    """Валидация российского номера телефона"""
    phone = phone.strip()
    return bool(re.match(r'^\+?7[0-9]{10}$|^8[0-9]{10}$', phone))

def validate_required_fields(data: Dict[str, Any], required_fields: list) -> Optional[str]:
    """Валидация обязательных полей"""
    for field in required_fields:
        if not data.get(field):
            return f"Поле '{field}' обязательно для заполнения"
    return None

def validate_field_length(data: Dict[str, Any], field: str, max_length: int) -> Optional[str]:
    """Валидация длины поля"""
    value = data.get(field, '')
    if len(str(value)) > max_length:
        return f"Поле '{field}' не должно превышать {max_length} символов"
    return None

# Декораторы
def handle_telegram_errors(f):
    """Декоратор для обработки ошибок Telegram API"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error in {f.__name__}: {str(e)}")
            return jsonify({"error": "Ошибка сети при обращении к Telegram API"}), 500
        except Exception as e:
            logger.error(f"Unexpected error in {f.__name__}: {str(e)}")
            return jsonify({"error": "Внутренняя ошибка сервера"}), 500
    return decorated_function

# Telegram API функции
class TelegramAPI:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def get_bot_info(self) -> Dict[str, Any]:
        """Получение информации о боте"""
        response = requests.get(
            f"{self.base_url}/getMe",
            timeout=Config.TELEGRAM_API_TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    
    def send_message(self, text: str) -> Dict[str, Any]:
        """Отправка сообщения"""
        response = requests.post(
            f"{self.base_url}/sendMessage",
            json={"chat_id": self.chat_id, "text": text},
            timeout=Config.TELEGRAM_API_TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    
    def get_updates(self) -> Dict[str, Any]:
        """Получение обновлений"""
        response = requests.get(
            f"{self.base_url}/getUpdates",
            timeout=Config.TELEGRAM_API_TIMEOUT
        )
        response.raise_for_status()
        return response.json()

# Инициализация Telegram API
telegram_api = TelegramAPI(Config.BOT_TOKEN, Config.CHAT_ID)

# Маршруты
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/sitemap.xml")
def sitemap():
    return send_from_directory(app.static_folder, "sitemap.xml", mimetype='application/xml')

@app.route("/robots.txt")
def robots():
    return send_from_directory(app.static_folder, "robots.txt", mimetype='text/plain')

@app.route('/api/test-telegram', methods=['GET'])
@handle_telegram_errors
def test_telegram():
    """Тестовый endpoint для проверки работы Telegram бота"""
    # Получение информации о боте
    bot_info = telegram_api.get_bot_info()
    
    # Отправка тестового сообщения
    test_message = "🔧 Тест соединения с ботом L'ÎLE DE RÊVE\n\nЕсли вы видите это сообщение, бот работает корректно!"
    send_result = telegram_api.send_message(test_message)
    
    return jsonify({
        "success": True,
        "message": "Тестовое сообщение успешно отправлено!",
        "bot_info": bot_info.get('result', {}),
        "chat_id": Config.CHAT_ID
    })

@app.route('/api/get-chat-id', methods=['GET'])
@handle_telegram_errors
def get_chat_id():
    """Получение доступных chat ID"""
    updates_data = telegram_api.get_updates()
    updates = updates_data.get('result', [])
    
    chat_ids = []
    for update in updates[-10:]:  # Последние 10 обновлений
        if 'message' in update:
            chat = update['message']['chat']
            chat_ids.append({
                'chat_id': chat['id'],
                'chat_type': chat['type'],
                'title': chat.get('title', ''),
                'username': chat.get('username', ''),
                'first_name': chat.get('first_name', ''),
                'last_name': chat.get('last_name', '')
            })
    
    return jsonify({
        "success": True,
        "current_chat_id": Config.CHAT_ID,
        "available_chats": chat_ids,
        "total_updates": len(updates)
    })

@app.route('/api/send-order-to-telegram', methods=['POST'])
@handle_telegram_errors
def send_order_to_telegram():
    """Отправка данных заказа в Telegram"""
    data = request.get_json()
    
    # Валидация обязательных полей для заказа
    required_fields = ['serviceTitle', 'servicePrice', 'duration', 'date', 'name', 'phone']
    validation_error = validate_required_fields(data, required_fields)
    if validation_error:
        return jsonify({"error": validation_error}), 400
    
    # Валидация длины полей
    length_validations = [
        ('name', Config.MAX_NAME_LENGTH),
        ('comments', Config.MAX_MESSAGE_LENGTH)  # комментарии могут быть длинными
    ]
    
    for field, max_length in length_validations:
        if field in data:  # комментарии опциональны
            length_error = validate_field_length(data, field, max_length)
            if length_error:
                return jsonify({"error": length_error}), 400
    
    # Валидация телефона
    phone = data.get('phone', '').strip()
    if not validate_phone(phone):
        return jsonify({
            "error": "Пожалуйста, введите корректный номер телефона (например, +79991112233 или 89991112233)."
        }), 400
    
    # Валидация даты
    date_value = data.get('date', '').strip()
    if not date_value:
        return jsonify({"error": "Пожалуйста, укажите дату начала услуги"}), 400
    
    # Валидация длительности
    try:
        duration = int(data.get('duration', 0))
        if duration <= 0:
            return jsonify({"error": "Длительность должна быть больше 0"}), 400
    except ValueError:
        return jsonify({"error": "Неверный формат длительности"}), 400
    
    # Формирование сообщения о заказе
    comments_text = f"\n💬 Комментарии: {data['comments']}" if data.get('comments') else ""
    email_text = f"\n📧 Email: {data['email']}" if data.get('email') else ""
    
    # Расчет общей стоимости (базовая цена * длительность)
    try:
        # Извлекаем число из строки цены
        price_str = data['servicePrice'].replace('₽', '').replace(' ', '').replace(',', '')
        base_price = float(price_str)
        total_price = base_price * duration
        total_text = f"\n💰 Общая стоимость: {total_price:,.0f} ₽"
    except (ValueError, AttributeError):
        total_text = f"\n💰 Цена за единицу: {data['servicePrice']}"
    
    telegram_message = f"""🛒 НОВЫЙ ЗАКАЗ с сайта L'ÎLE DE RÊVE

📋 ДЕТАЛИ ЗАКАЗА:
• Услуга: {data['serviceTitle']}
• Цена за единицу: {data['servicePrice']}
• Длительность: {duration} ед.{total_text}
• Дата начала: {date_value}

👤 ДАННЫЕ КЛИЕНТА:
• Имя: {data['name']}
• Телефон: {phone}{email_text}{comments_text}

---
📅 Заказ оформлен: {data.get('timestamp', 'не указано')}
🔔 Требуется подтверждение заказа и связь с клиентом!"""
    
    # Отправка сообщения
    result = telegram_api.send_message(telegram_message)
    
    return jsonify({
        "success": True,
        "message": "Заказ успешно отправлен! Мы свяжемся с вами в ближайшее время для подтверждения.",
        "telegram_response": result
    })

@app.route('/api/send-to-telegram', methods=['POST'])
@handle_telegram_errors
def send_to_telegram():
    """Отправка сообщения в Telegram"""
    data = request.get_json()
    
    # Валидация обязательных полей
    required_fields = ['name', 'message', 'phone']
    validation_error = validate_required_fields(data, required_fields)
    if validation_error:
        return jsonify({"error": validation_error}), 400
    
    # Валидация длины полей
    length_validations = [
        ('name', Config.MAX_NAME_LENGTH),
        ('message', Config.MAX_MESSAGE_LENGTH)
    ]
    
    for field, max_length in length_validations:
        length_error = validate_field_length(data, field, max_length)
        if length_error:
            return jsonify({"error": length_error}), 400
    
    # Валидация телефона
    phone = data.get('phone', '').strip()
    if not validate_phone(phone):
        return jsonify({
            "error": "Пожалуйста, введите корректный номер телефона (например, +79991112233 или 89991112233)."
        }), 400
    
    # Формирование сообщения
    email_text = f"\n📧 Email: {data['email']}" if data.get('email') else ""
    phone_text = f"\n📱 Телефон: {phone}"
    telegram_message = f"""📝 Новое сообщение с сайта L'ÎLE DE RÊVE

👤 Имя: {data['name']}{email_text}{phone_text}
💬 Сообщение: {data['message']}

---
Отправлено: {data.get('timestamp', 'не указано')}"""
    
    # Отправка сообщения
    result = telegram_api.send_message(telegram_message)
    
    return jsonify({
        "success": True,
        "message": "Сообщение успешно отправлено!",
        "telegram_response": result
    })

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    app.run(debug=Config.DEBUG)