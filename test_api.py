#!/usr/bin/env python3
"""
Тестирование API endpoints
"""

import requests
import json
import sys

BASE_URL = "http://localhost:5000"

def test_telegram_connection():
    """Тест соединения с Telegram"""
    print("🔧 Тестирование соединения с Telegram...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/test-telegram")
        data = response.json()
        
        if response.status_code == 200:
            print("✅ Соединение с Telegram работает!")
            print(f"   Бот: {data.get('bot_info', {}).get('username', 'N/A')}")
            print(f"   Chat ID: {data.get('chat_id', 'N/A')}")
        else:
            print(f"❌ Ошибка: {data.get('error', 'Неизвестная ошибка')}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Не удается подключиться к серверу. Убедитесь, что приложение запущено.")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def test_send_message():
    """Тест отправки сообщения из контактной формы"""
    print("\n📝 Тестирование отправки сообщения из контактной формы...")
    
    test_data = {
        "name": "Тестовый пользователь",
        "phone": "+79991112233",
        "email": "test@example.com",
        "message": "Это тестовое сообщение для проверки работы API.",
        "timestamp": "2024-01-01 12:00:00"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/send-to-telegram",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        data = response.json()
        
        if response.status_code == 200:
            print("✅ Сообщение успешно отправлено!")
        else:
            print(f"❌ Ошибка: {data.get('error', 'Неизвестная ошибка')}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Не удается подключиться к серверу.")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def test_send_order():
    """Тест отправки заказа"""
    print("\n🛒 Тестирование отправки заказа...")
    
    test_order_data = {
        "serviceTitle": "Услуги сиделки (дневное время)",
        "servicePrice": "2500 ₽",
        "duration": "7",
        "date": "2024-02-01",
        "name": "Иван Петров",
        "phone": "+79991112233",
        "email": "ivan@example.com",
        "comments": "Требуется опыт работы с пожилыми людьми. Предпочтительно женщина 40-55 лет.",
        "timestamp": "2024-01-15 14:30:00"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/send-order-to-telegram",
            json=test_order_data,
            headers={"Content-Type": "application/json"}
        )
        data = response.json()
        
        if response.status_code == 200:
            print("✅ Заказ успешно отправлен!")
            print(f"   Услуга: {test_order_data['serviceTitle']}")
            print(f"   Длительность: {test_order_data['duration']} дней")
            print(f"   Общая стоимость: {int(test_order_data['servicePrice'].replace(' ₽', '')) * int(test_order_data['duration']):,} ₽")
        else:
            print(f"❌ Ошибка: {data.get('error', 'Неизвестная ошибка')}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Не удается подключиться к серверу.")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def test_get_chat_id():
    """Тест получения chat ID"""
    print("\n🆔 Тестирование получения chat ID...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/get-chat-id")
        data = response.json()
        
        if response.status_code == 200:
            print("✅ Chat ID получены успешно!")
            print(f"   Текущий Chat ID: {data.get('current_chat_id', 'N/A')}")
            print(f"   Доступных чатов: {len(data.get('available_chats', []))}")
        else:
            print(f"❌ Ошибка: {data.get('error', 'Неизвестная ошибка')}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Не удается подключиться к серверу.")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестов API...\n")
    
    # Тест соединения с Telegram
    test_telegram_connection()
    
    # Тест получения chat ID
    test_get_chat_id()
    
    # Тест отправки заказа (новая функция)
    test_send_order()
    
    # Тест отправки сообщения из контактной формы
    test_send_message()
    
    print("\n✨ Тестирование завершено!")

if __name__ == '__main__':
    main() 