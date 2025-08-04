#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import requests
from typing import Dict, Any

# Конфигурация
BOT_TOKEN = os.environ.get('BOT_TOKEN', '7585621279:AAFLcwzw-lrh5PCHvgGZqZ6lG-TIPlwXZZo')
CHAT_ID = os.environ.get('CHAT_ID', '5682979333')
TELEGRAM_API_TIMEOUT = 30

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
    """Функция для тестирования Telegram API"""
    
    # Обработка CORS preflight запросов
    if event.get('httpMethod') == 'OPTIONS':
        return create_response(200, {"message": "OK"})
    
    # Только GET запросы
    if event.get('httpMethod') != 'GET':
        return create_response(405, {"error": "Метод не поддерживается"})
    
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