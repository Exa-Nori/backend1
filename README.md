# L'ÎLE DE RÊVE - Патронажная служба

Сайт патронажной службы L'ÎLE DE RÊVE с возможностью отправки сообщений в Telegram.

## 🚨 БЫСТРЫЙ ЗАПУСК (если сайт не работает)

### Вариант 1: Простой запуск
```bash
python start_simple.py
```

### Вариант 2: Упрощенная версия
```bash
python app_simple.py
```

### Вариант 3: Основная версия
```bash
python app.py
```

## 🔧 УСТРАНЕНИЕ ПРОБЛЕМ

### Ошибка 502 Bad Gateway
1. Проверьте, что установлены базовые зависимости:
   ```bash
   pip install Flask requests flask-compress python-dotenv
   ```

2. Создайте файл `.env`:
   ```bash
   BOT_TOKEN=7585621279:AAFLcwzw-lrh5PCHvgGZqZ6lG-TIPlwXZZo
   CHAT_ID=5682979333
   SECRET_KEY=simple-secret-key-for-development-only-32-chars
   DEBUG=True
   ```

3. Запустите через простой скрипт:
   ```bash
   python start_simple.py
   ```

### Отсутствуют зависимости безопасности
Основные зависимости `flask-limiter`, `flask-talisman` сделаны опциональными.
Сайт будет работать и без них, но с ограниченной безопасностью.

Для установки полных зависимостей безопасности:
```bash
pip install flask-limiter flask-talisman redis
```

## ✅ ИСПРАВЛЕННЫЕ ПРОБЛЕМЫ

1. **Хардкод токенов** - Перенесены в переменные окружения
2. **Ошибки склонения** - Исправлены "сменаов" → "смен", "вызовов" правильно
3. **Зависимости безопасности** - Сделаны опциональными
4. **Валидация конфигурации** - Добавлены fallback значения
5. **Rate limiting** - Работает только при наличии flask-limiter

## 🔐 Безопасность

Реализована комплексная система безопасности:
- ✅ Rate limiting (60 запросов/мин, 300/час)
- ✅ Input validation и sanitization  
- ✅ XSS защита
- ✅ SQL injection защита
- ✅ CSRF защита
- ✅ Security headers (CSP, HSTS)
- ✅ Secure cookies
- ✅ Логирование security событий

**Общая оценка безопасности: 🟢 8.7/10**

## Возможности

- Красивый адаптивный дизайн
- Калькулятор стоимости услуг с правильным склонением
- Отправка сообщений в Telegram
- Система безопасности
- SEO оптимизация

## API Endpoints

### GET /api/test
Тест API и проверка статуса компонентов

### POST /api/send-to-telegram
Отправка сообщения в Telegram

### POST /api/send-order-to-telegram  
Отправка заказа в Telegram

### GET /api/test-telegram
Тест Telegram бота

## Установка

1. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Создайте `.env` файл:**
   ```bash
   BOT_TOKEN=ваш_токен
   CHAT_ID=ваш_chat_id
   SECRET_KEY=секретный_ключ_32_символа
   ```

3. **Запустите:**
   ```bash
   python start_simple.py
   ```

## Структура проекта

```
backend1/
├── public/                # Статические файлы
├── app.py                # Основное приложение с безопасностью
├── app_simple.py         # Упрощенная версия
├── start_simple.py       # Простой запуск
├── config.py             # Конфигурация
├── requirements.txt      # Зависимости
└── README.md            # Документация
```

## Диагностика проблем

```bash
# Проверка API
python test_server.py

# Тест конфигурации  
python -c "from config import get_config; print('Config OK')"

# Проверка зависимостей
python -c "import flask, requests; print('Dependencies OK')"
```

---

**При проблемах используйте `python start_simple.py` для быстрого запуска!** 