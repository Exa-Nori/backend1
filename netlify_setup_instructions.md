# 🚀 Развертывание на Netlify

## 📋 Что было создано:

### 1. **`netlify.toml`** - конфигурация Netlify
- Настройки сборки
- Перенаправления для API
- Конфигурация функций

### 2. **`netlify/functions/app.py`** - серверная функция
- Адаптированная версия Flask приложения
- Все API endpoints работают
- Поддержка CORS
- Обработка ошибок

### 3. **Обновленный `requirements.txt`**
- Только необходимые зависимости для Netlify

## 🔧 Как развернуть:

### **Шаг 1: Подготовка файлов**
1. Убедитесь, что все файлы загружены в репозиторий:
   - `netlify.toml`
   - `netlify/functions/app.py`
   - `requirements.txt`
   - `public/` (статические файлы)

### **Шаг 2: Подключение к Netlify**
1. Зайдите на [netlify.com](https://netlify.com)
2. Нажмите "New site from Git"
3. Выберите ваш репозиторий
4. Настройки сборки:
   - **Build command**: `pip install -r requirements.txt`
   - **Publish directory**: `public`
   - **Python version**: 3.9

### **Шаг 3: Настройка переменных окружения**
В настройках сайта Netlify добавьте:
- `BOT_TOKEN` = ваш токен Telegram бота
- `CHAT_ID` = ваш chat ID

### **Шаг 4: Деплой**
1. Нажмите "Deploy site"
2. Дождитесь завершения сборки
3. Проверьте работу API

## 🔗 API Endpoints:

Все API endpoints работают так же, как на Vercel:

- `GET /api/test-telegram` - тест Telegram API
- `GET /api/get-chat-id` - получение chat ID
- `POST /api/send-order-to-telegram` - отправка заказа
- `POST /api/send-to-telegram` - отправка сообщения

## ✅ Преимущества Netlify:

1. **Бесплатный хостинг** - до 125K запросов в месяц
2. **Автоматический деплой** - при push в Git
3. **CDN** - быстрая загрузка по всему миру
4. **SSL сертификат** - автоматически
5. **Функции** - serverless Python

## 🐛 Отладка:

### **Проверка логов:**
1. В панели Netlify перейдите в "Functions"
2. Нажмите на функцию `app`
3. Посмотрите логи выполнения

### **Локальное тестирование:**
```bash
# Установите Netlify CLI
npm install -g netlify-cli

# Запустите локально
netlify dev
```

## 📝 Отличия от Vercel:

1. **Структура**: Netlify использует функции в папке `netlify/functions/`
2. **Конфигурация**: `netlify.toml` вместо `vercel.json`
3. **API**: Функции возвращают объекты вместо Flask responses
4. **CORS**: Автоматически настроен для всех доменов

## 🎯 Готово!

После деплоя ваш сайт будет работать на Netlify с полной функциональностью Telegram API! 