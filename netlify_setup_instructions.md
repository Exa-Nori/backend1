# 🚀 Развертывание на Netlify

## 📋 Что было создано:

### 1. **`netlify.toml`** - конфигурация Netlify
- Настройки сборки
- Перенаправления для API с `force = true`
- Конфигурация функций

### 2. **`netlify/functions/app.py`** - серверная функция
- Упрощенная версия без внешних зависимостей
- Все API endpoints работают
- Поддержка CORS
- Обработка ошибок

### 3. **`netlify/functions/requirements.txt`** - зависимости для функций
- Только необходимые пакеты

## 🔧 Как развернуть:

### **Шаг 1: Подготовка файлов**
1. Убедитесь, что все файлы загружены в репозиторий:
   - `netlify.toml`
   - `netlify/functions/app.py`
   - `netlify/functions/requirements.txt`
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
В настройках сайта Netlify (Site settings → Environment variables) добавьте:
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

### **Тестирование:**
```bash
# Запустите тестовый скрипт
python test_netlify_function.py
```

### **Локальное тестирование:**
```bash
# Установите Netlify CLI
npm install -g netlify-cli

# Запустите локально
netlify dev
```

## 🔧 Исправления для 404 ошибки:

### **Проблема**: API endpoints возвращают 404
### **Решение**: 
1. Добавлен `force = true` в redirects
2. Упрощена функция без внешних зависимостей
3. Правильная структура папок

### **Проверка структуры:**
```
your-project/
├── netlify.toml
├── requirements.txt
├── public/
│   ├── index.html
│   └── ...
└── netlify/
    └── functions/
        ├── app.py
        └── requirements.txt
```

## 📝 Отличия от Vercel:

1. **Структура**: Netlify использует функции в папке `netlify/functions/`
2. **Конфигурация**: `netlify.toml` вместо `vercel.json`
3. **API**: Функции возвращают объекты вместо Flask responses
4. **CORS**: Автоматически настроен для всех доменов
5. **Переменные окружения**: Через `os.environ.get()`

## 🎯 Готово!

После деплоя ваш сайт будет работать на Netlify с полной функциональностью Telegram API!

### **Проверка работы:**
1. Откройте ваш сайт на Netlify
2. Проверьте API: `https://your-site.netlify.app/api/test-telegram`
3. Отправьте тестовое сообщение через форму на сайте 