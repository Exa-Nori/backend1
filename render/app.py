#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
import os
from functools import wraps
from typing import Dict, Any, Optional

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для всех доменов

# Конфигурация
BOT_TOKEN = os.environ.get('BOT_TOKEN', '7585621279:AAFLcwzw-lrh5PCHvgGZqZ6lG-TIPlwXZZo')
CHAT_ID = os.environ.get('CHAT_ID', '5682979333')
TELEGRAM_API_TIMEOUT = 30
MAX_NAME_LENGTH = 100
MAX_MESSAGE_LENGTH = 1000

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

# Telegram API
class TelegramAPI:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def get_bot_info(self) -> Dict[str, Any]:
        """Получение информации о боте"""
        response = requests.get(
            f"{self.base_url}/getMe",
            timeout=TELEGRAM_API_TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    
    def send_message(self, text: str) -> Dict[str, Any]:
        """Отправка сообщения"""
        response = requests.post(
            f"{self.base_url}/sendMessage",
            json={"chat_id": self.chat_id, "text": text},
            timeout=TELEGRAM_API_TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    
    def get_updates(self) -> Dict[str, Any]:
        """Получение обновлений"""
        response = requests.get(
            f"{self.base_url}/getUpdates",
            timeout=TELEGRAM_API_TIMEOUT
        )
        response.raise_for_status()
        return response.json()

# Инициализация Telegram API
telegram_api = TelegramAPI(BOT_TOKEN, CHAT_ID)

# Декораторы
def handle_telegram_errors(f):
    """Декоратор для обработки ошибок Telegram API"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except requests.exceptions.RequestException as e:
            return jsonify({"error": "Ошибка сети при обращении к Telegram API"}), 500
        except Exception as e:
            return jsonify({"error": "Внутренняя ошибка сервера"}), 500
    return decorated_function

# API маршруты
@app.route('/api/test-telegram', methods=['GET'])
@handle_telegram_errors
def test_telegram():
    """Тест Telegram API"""
    bot_info = telegram_api.get_bot_info()
    test_message = "🔧 Тест соединения с ботом L'ÎLE DE RÊVE\n\nЕсли вы видите это сообщение, бот работает корректно!"
    send_result = telegram_api.send_message(test_message)
    
    return jsonify({
        "success": True,
        "message": "Тестовое сообщение успешно отправлено!",
        "bot_info": bot_info.get('result', {}),
        "chat_id": CHAT_ID
    })

@app.route('/api/get-chat-id', methods=['GET'])
@handle_telegram_errors
def get_chat_id():
    """Получение chat ID"""
    updates_data = telegram_api.get_updates()
    updates = updates_data.get('result', [])
    
    chat_ids = []
    last_updates = updates[-10:] if len(updates) > 10 else updates
    
    for update in last_updates:
        if 'message' in update and 'chat' in update['message']:
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
        "current_chat_id": CHAT_ID,
        "available_chats": chat_ids,
        "total_updates": len(updates)
    })

@app.route('/api/send-order-to-telegram', methods=['POST'])
@handle_telegram_errors
def send_order_to_telegram():
    """Отправка заказа в Telegram"""
    data = request.get_json()
    
    # Валидация обязательных полей
    required_fields = ['serviceTitle', 'servicePrice', 'duration', 'date', 'name', 'phone']
    validation_error = validate_required_fields(data, required_fields)
    if validation_error:
        return jsonify({"error": validation_error}), 400
    
    # Валидация длины полей
    length_validations = [
        ('name', MAX_NAME_LENGTH),
        ('comments', MAX_MESSAGE_LENGTH)
    ]
    for field, max_length in length_validations:
        if field in data:
            length_error = validate_field_length(data, field, max_length)
            if length_error:
                return jsonify({"error": length_error}), 400
    
    # Валидация телефона
    phone = data.get('phone', '').strip()
    if not validate_phone(phone):
        return jsonify({"error": "Пожалуйста, введите корректный номер телефона (например, +79991112233 или 89991112233)."}), 400
    
    # Валидация даты
    date_value = data.get('date', '').strip()
    if not date_value:
        return jsonify({"error": "Пожалуйста, укажите дату начала услуги"}), 400
    
    # Валидация длительности
    duration = int(data.get('duration', 0))
    if duration <= 0:
        return jsonify({"error": "Длительность должна быть больше 0"}), 400
    
    # Формирование сообщения
    comments_text = f"\n💬 Комментарии: {data.get('comments', '')}" if data.get('comments') else ""
    email_text = f"\n📧 Email: {data.get('email', '')}" if data.get('email') else ""
    
    # Расчет стоимости
    price_str = str(data.get('servicePrice', '0')).replace('₽', '').replace(' ', '').replace(',', '')
    base_price = float(price_str)
    total_price = base_price * duration
    total_text = f"\n💰 Общая стоимость: {total_price:,.0f} ₽"
    
    telegram_message = f"""🛒 НОВЫЙ ЗАКАЗ с сайта L'ÎLE DE RÊVE

📋 ДЕТАЛИ ЗАКАЗА:
• Услуга: {data.get('serviceTitle', '')}
• Цена за единицу: {data.get('servicePrice', '')}
• Длительность: {duration} ед.{total_text}
• Дата начала: {date_value}

👤 ДАННЫЕ КЛИЕНТА:
• Имя: {data.get('name', '')}
• Телефон: {phone}{email_text}{comments_text}

---
📅 Заказ оформлен: {data.get('timestamp', 'не указано')}
🔔 Требуется подтверждение заказа и связь с клиентом!"""
    
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
        ('name', MAX_NAME_LENGTH),
        ('message', MAX_MESSAGE_LENGTH)
    ]
    for field, max_length in length_validations:
        length_error = validate_field_length(data, field, max_length)
        if length_error:
            return jsonify({"error": length_error}), 400
    
    # Валидация телефона
    phone = data.get('phone', '').strip()
    if not validate_phone(phone):
        return jsonify({"error": "Пожалуйста, введите корректный номер телефона (например, +79991112233 или 89991112233)."}), 400
    
    # Формирование сообщения
    email_text = f"\n📧 Email: {data.get('email', '')}" if data.get('email') else ""
    telegram_message = f"""📝 Новое сообщение с сайта L'ÎLE DE RÊVE

👤 Имя: {data.get('name', '')}{email_text}
📱 Телефон: {phone}
💬 Сообщение: {data.get('message', '')}

---
Отправлено: {data.get('timestamp', 'не указано')}"""
    
    result = telegram_api.send_message(telegram_message)
    
    return jsonify({
        "success": True,
        "message": "Сообщение успешно отправлено!",
        "telegram_response": result
    })

@app.route('/')
def health_check():
    """Проверка здоровья API"""
    return jsonify({
        "status": "ok",
        "message": "L'ÎLE DE RÊVE API работает на Render",
        "version": "1.0.0"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 