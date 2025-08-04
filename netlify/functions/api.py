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

def test_telegram(event, context):
    """Тест Telegram API"""
    try:
        bot_info = telegram_api.get_bot_info()
        test_message = "🔧 Тест соединения с ботом L'ÎLE DE RÊVE\n\nЕсли вы видите это сообщение, бот работает корректно!"
        send_result = telegram_api.send_message(test_message)
        
        return create_response(200, {
            "success": True,
            "message": "Тестовое сообщение успешно отправлено!",
            "bot_info": bot_info.get('result', {}),
            "chat_id": CHAT_ID
        })
    except Exception as e:
        return create_response(500, {"error": f"Ошибка при обращении к Telegram API: {str(e)}"})

def get_chat_id(event, context):
    """Получение chat ID"""
    try:
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
        
        return create_response(200, {
            "success": True,
            "current_chat_id": CHAT_ID,
            "available_chats": chat_ids,
            "total_updates": len(updates)
        })
    except Exception as e:
        return create_response(500, {"error": f"Ошибка при получении chat ID: {str(e)}"})

def send_order_to_telegram(event, context):
    """Отправка заказа в Telegram"""
    try:
        data = json.loads(event.get('body', '{}'))
        
        # Валидация обязательных полей
        required_fields = ['serviceTitle', 'servicePrice', 'duration', 'date', 'name', 'phone']
        validation_error = validate_required_fields(data, required_fields)
        if validation_error:
            return create_response(400, {"error": validation_error})
        
        # Валидация длины полей
        length_validations = [
            ('name', MAX_NAME_LENGTH),
            ('comments', MAX_MESSAGE_LENGTH)
        ]
        for field, max_length in length_validations:
            if field in data:
                length_error = validate_field_length(data, field, max_length)
                if length_error:
                    return create_response(400, {"error": length_error})
        
        # Валидация телефона
        phone = data.get('phone', '').strip()
        if not validate_phone(phone):
            return create_response(400, {"error": "Пожалуйста, введите корректный номер телефона (например, +79991112233 или 89991112233)."})
        
        # Валидация даты
        date_value = data.get('date', '').strip()
        if not date_value:
            return create_response(400, {"error": "Пожалуйста, укажите дату начала услуги"})
        
        # Валидация длительности
        duration = int(data.get('duration', 0))
        if duration <= 0:
            return create_response(400, {"error": "Длительность должна быть больше 0"})
        
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
        
        return create_response(200, {
            "success": True,
            "message": "Заказ успешно отправлен! Мы свяжемся с вами в ближайшее время для подтверждения.",
            "telegram_response": result
        })
        
    except json.JSONDecodeError:
        return create_response(400, {"error": "Неверный формат JSON"})
    except Exception as e:
        return create_response(500, {"error": f"Ошибка при отправке заказа: {str(e)}"})

def send_to_telegram(event, context):
    """Отправка сообщения в Telegram"""
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

# Основная функция Netlify
def handler(event, context):
    """Основная функция для обработки запросов"""
    
    # Обработка CORS preflight запросов
    if event.get('httpMethod') == 'OPTIONS':
        return create_response(200, {"message": "OK"})
    
    # Парсинг URL
    path = event.get('path', '')
    method = event.get('httpMethod', 'GET')
    
    # Маршрутизация
    if path == '/api/test-telegram' and method == 'GET':
        return test_telegram(event, context)
    elif path == '/api/get-chat-id' and method == 'GET':
        return get_chat_id(event, context)
    elif path == '/api/send-order-to-telegram' and method == 'POST':
        return send_order_to_telegram(event, context)
    elif path == '/api/send-to-telegram' and method == 'POST':
        return send_to_telegram(event, context)
    else:
        return create_response(404, {"error": "Endpoint не найден", "path": path, "method": method}) 