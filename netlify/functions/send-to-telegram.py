#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import requests
import re
from typing import Dict, Any, Optional

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
    
    def send_message(self, text: str) -> Dict[str, Any]:
        """Отправка сообщения"""
        response = requests.post(
            f"{self.base_url}/sendMessage",
            json={"chat_id": self.chat_id, "text": text},
            timeout=TELEGRAM_API_TIMEOUT
        )
        response.raise_for_status()
        return response.json()

# Инициализация Telegram API
telegram_api = TelegramAPI(BOT_TOKEN, CHAT_ID)

def create_response(status_code: int, body: Dict[str, Any], headers: Dict[str, str] = None) -> Dict[str, Any]:
    """Создание ответа для Netlify"""
    response = {
        "statusCode": status_code,
        "body": json.dumps(body, ensure_ascii=False),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Max-Age": "86400"
        }
    }
    if headers:
        response["headers"].update(headers)
    return response

def handler(event, context):
    """Функция для отправки сообщения в Telegram"""
    
    # Обработка CORS preflight запросов
    if event.get('httpMethod') == 'OPTIONS':
        return create_response(200, {"message": "OK"})
    
    # Только POST запросы
    if event.get('httpMethod') != 'POST':
        return create_response(405, {"error": "Метод не поддерживается"})
    
    try:
        data = json.loads(event.get('body', '{}'))
        
        # Валидация обязательных полей
        required_fields = ['name', 'message', 'phone']
        validation_error = validate_required_fields(data, required_fields)
        if validation_error:
            return create_response(400, {"error": validation_error})
        
        # Валидация длины полей
        length_validations = [
            ('name', MAX_NAME_LENGTH),
            ('message', MAX_MESSAGE_LENGTH)
        ]
        for field, max_length in length_validations:
            length_error = validate_field_length(data, field, max_length)
            if length_error:
                return create_response(400, {"error": length_error})
        
        # Валидация телефона
        phone = data.get('phone', '').strip()
        if not validate_phone(phone):
            return create_response(400, {"error": "Пожалуйста, введите корректный номер телефона (например, +79991112233 или 89991112233)."})
        
        # Формирование сообщения
        email_text = f"\n📧 Email: {data.get('email', '')}" if data.get('email') else ""
        telegram_message = f"""📝 Новое сообщение с сайта L'ÎLE DE RÊVE

👤 Имя: {data.get('name', '')}{email_text}
📱 Телефон: {phone}
💬 Сообщение: {data.get('message', '')}

---
Отправлено: {data.get('timestamp', 'не указано')}"""
        
        result = telegram_api.send_message(telegram_message)
        
        return create_response(200, {
            "success": True,
            "message": "Сообщение успешно отправлено!",
            "telegram_response": result
        })
        
    except json.JSONDecodeError:
        return create_response(400, {"error": "Неверный формат JSON"})
    except Exception as e:
        return create_response(500, {"error": f"Ошибка при отправке сообщения: {str(e)}"}) 