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

def handler(event, context):
    """Функция для получения chat ID"""
    
    # Обработка CORS preflight запросов
    if event.get('httpMethod') == 'OPTIONS':
        return create_response(200, {"message": "OK"})
    
    # Только GET запросы
    if event.get('httpMethod') != 'GET':
        return create_response(405, {"error": "Метод не поддерживается"})
    
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