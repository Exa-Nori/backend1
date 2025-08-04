#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests

def test_netlify_function():
    """Тест Netlify функции"""
    
    # URL вашего сайта на Netlify (замените на ваш)
    base_url = "https://your-site-name.netlify.app"
    
    # Тест 1: Проверка доступности функции
    print("🔍 Тест 1: Проверка доступности функции")
    try:
        response = requests.get(f"{base_url}/.netlify/functions/app")
        print(f"Статус: {response.status_code}")
        print(f"Ответ: {response.text[:200]}...")
    except Exception as e:
        print(f"Ошибка: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Тест 2: Тест Telegram API
    print("🔍 Тест 2: Тест Telegram API")
    try:
        response = requests.get(f"{base_url}/api/test-telegram")
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Успех: {data.get('message', 'Нет сообщения')}")
        else:
            print(f"Ошибка: {response.text}")
    except Exception as e:
        print(f"Ошибка: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Тест 3: Отправка сообщения
    print("🔍 Тест 3: Отправка сообщения")
    test_data = {
        "name": "Тест",
        "phone": "+79991112233",
        "message": "Тестовое сообщение с сайта",
        "email": "test@example.com",
        "timestamp": "2024-01-01 12:00:00"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/send-to-telegram",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Успех: {data.get('message', 'Нет сообщения')}")
        else:
            print(f"Ошибка: {response.text}")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    print("🚀 Тестирование Netlify функции")
    print("="*50)
    test_netlify_function() 