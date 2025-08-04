#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import requests

def handler(event, context):
    """Функция для отправки сообщения в Telegram"""
    
    # Конфигурация
    BOT_TOKEN = os.environ.get('BOT_TOKEN', '7585621279:AAFLcwzw-lrh5PCHvgGZqZ6lG-TIPlwXZZo')
    CHAT_ID = os.environ.get('CHAT_ID', '5682979333')
    
    # Обработка CORS preflight запросов
    if event.get('httpMethod') == 'OPTIONS':
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "OK"}),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS"
            }
        }
    
    # Только POST запросы
    if event.get('httpMethod') != 'POST':
        return {
            "statusCode": 405,
            "body": json.dumps({"error": "Метод не поддерживается"}),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            }
        }
    
    try:
        data = json.loads(event.get('body', '{}'))
        
        # Простая валидация
        if not data.get('name') or not data.get('message') or not data.get('phone'):
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Не все обязательные поля заполнены"}),
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                }
            }
        
        # Формирование сообщения
        email_text = f"\n📧 Email: {data.get('email', '')}" if data.get('email') else ""
        telegram_message = f"""📝 Новое сообщение с сайта L'ÎLE DE RÊVE

👤 Имя: {data.get('name', '')}{email_text}
📱 Телефон: {data.get('phone', '')}
💬 Сообщение: {data.get('message', '')}

---
Отправлено: {data.get('timestamp', 'не указано')}"""
        
        # Отправка в Telegram
        response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": telegram_message},
            timeout=30
        )
        response.raise_for_status()
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "success": True,
                "message": "Сообщение успешно отправлено!"
            }, ensure_ascii=False),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            }
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Ошибка при отправке сообщения: {str(e)}"}),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            }
        } 