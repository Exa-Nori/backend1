#!/usr/bin/env python3
"""
Скрипт для запуска Flask приложения
"""

import sys
import logging
from app import app, Config
import os

def main():
    """Основная функция запуска"""
    try:
        # Проверка конфигурации
        Config.validate()
        logging.info("Конфигурация проверена успешно")
        
        # Запуск приложения
        app.run(
            host='0.0.0.0',
            port=int(os.environ.get('PORT', 5000)),
            debug=Config.DEBUG
        )
        
    except ValueError as e:
        logging.error(f"Ошибка конфигурации: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Ошибка запуска приложения: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 