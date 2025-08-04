# 🚀 Развертывание L'ÎLE DE RÊVE на Railway + Netlify

## 📋 Обзор решения

- **Railway** - Flask API для Telegram бота (доступен в России)
- **Netlify** - статические файлы (HTML, CSS, JS)

## 🔧 Шаг 1: Развертывание API на Railway

### 1.1 Подготовка
```bash
# Создайте аккаунт на Railway.app
# Подключите GitHub аккаунт
```

### 1.2 Создание проекта
1. Зайдите на [railway.app](https://railway.app)
2. Нажмите "New Project"
3. Выберите "Deploy from GitHub repo"
4. Выберите ваш репозиторий
5. Выберите папку `railway/`

### 1.3 Настройка переменных окружения
В Railway Dashboard:
1. Перейдите в "Variables"
2. Добавьте:
   - `BOT_TOKEN` = `7585621279:AAFLcwzw-lrh5PCHvgGZqZ6lG-TIPlwXZZo`
   - `CHAT_ID` = `5682979333`

### 1.4 Автоматический деплой
Railway автоматически развернет приложение при push в GitHub!

### 1.5 Проверка
```bash
# Получите URL из Railway Dashboard
curl https://your-app.railway.app/
# Должен показать: {"status": "ok", "message": "L'ÎLE DE RÊVE API работает на Railway"}
```

## 🌐 Шаг 2: Развертывание фронтенда на Netlify

### 2.1 Подготовка файлов
1. Скопируйте все файлы из папки `public/` в папку `netlify/`
2. Обновите `netlify/index.html` с URL вашего Railway API

### 2.2 Деплой на Netlify
1. Зайдите на [netlify.com](https://netlify.com)
2. Создайте новый сайт
3. Загрузите папку `netlify/` как источник
4. Настройте:
   - **Build command:** (оставьте пустым)
   - **Publish directory:** `netlify`

### 2.3 Настройка домена
- Получите URL вида: `https://your-site.netlify.app`
- Обновите URL API в `index.html`

## 🔗 Шаг 3: Обновление фронтенда

### 3.1 Обновите API URL в HTML файлах
Замените все URL API на ваш Railway URL:

```javascript
// В public/index.html, public/all-services.html и других
const API_BASE_URL = 'https://your-app.railway.app';
```

### 3.2 Обновите fetch запросы
```javascript
// Пример обновления
fetch(`${API_BASE_URL}/api/send-to-telegram`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
})
```

## 🧪 Шаг 4: Тестирование

### 4.1 Тест API
```bash
curl https://your-app.railway.app/
# Должен вернуть: {"status": "ok", "message": "L'ÎLE DE RÊVE API работает на Railway"}
```

### 4.2 Тест Telegram
```bash
curl https://your-app.railway.app/api/test-telegram
# Должен отправить тестовое сообщение в Telegram
```

### 4.3 Тест фронтенда
1. Откройте ваш Netlify сайт
2. Заполните форму
3. Проверьте, что сообщения приходят в Telegram

## 🔧 Шаг 5: Настройка CORS (если нужно)

Если возникают ошибки CORS, добавьте в `railway/app.py`:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['https://your-netlify-site.netlify.app'])
```

## 📱 Преимущества этого решения

✅ **Работает с российских операторов**  
✅ **Railway доступен в России**  
✅ **Бесплатный хостинг** (Railway + Netlify)  
✅ **Высокая доступность**  
✅ **Простота настройки**  
✅ **Автоматический деплой**  

## 🚨 Устранение неполадок

### Проблема: Railway не запускается
1. Проверьте логи в Railway Dashboard
2. Убедитесь, что все файлы в папке `railway/`

### Проблема: API не отвечает
1. Проверьте переменные окружения в Railway Dashboard
2. Проверьте статус деплоя

### Проблема: CORS ошибки
1. Убедитесь, что `flask-cors` установлен
2. Проверьте настройки CORS в `app.py`

### Проблема: Telegram не работает
1. Проверьте `BOT_TOKEN` и `CHAT_ID` в Railway
2. Убедитесь, что бот активен
3. Проверьте права бота

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте логи в Railway Dashboard
2. Проверьте переменные окружения
3. Проверьте статус деплоя

## 🎉 Готово!

Теперь ваш сайт работает на:
- **Фронтенд:** `https://your-site.netlify.app`
- **API:** `https://your-app.railway.app`

Оба доступны с российских операторов! 📱🇷🇺

## 🔄 Альтернативы Railway

Если Railway не подходит, попробуйте:

### Render.com
```bash
# Аналогично Railway, но с другими настройками
```

### PythonAnywhere
```bash
# Специально для Python приложений
```

### Fly.io
```bash
# Быстрый деплой, доступен в России
``` 