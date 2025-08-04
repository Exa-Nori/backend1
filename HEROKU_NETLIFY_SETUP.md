# 🚀 Развертывание L'ÎLE DE RÊVE на Heroku + Netlify

## 📋 Обзор решения

- **Heroku** - Flask API для Telegram бота
- **Netlify** - статические файлы (HTML, CSS, JS)

## 🔧 Шаг 1: Развертывание API на Heroku

### 1.1 Подготовка
```bash
# Создайте аккаунт на Heroku.com
# Установите Heroku CLI
```

### 1.2 Создание приложения
```bash
cd heroku
heroku create your-app-name
```

### 1.3 Настройка переменных окружения
```bash
heroku config:set BOT_TOKEN=7585621279:AAFLcwzw-lrh5PCHvgGZqZ6lG-TIPlwXZZo
heroku config:set CHAT_ID=5682979333
```

### 1.4 Деплой
```bash
git init
git add .
git commit -m "Initial commit"
git push heroku main
```

### 1.5 Проверка
```bash
heroku open
# Должен показать: {"status": "ok", "message": "L'ÎLE DE RÊVE API работает"}
```

## 🌐 Шаг 2: Развертывание фронтенда на Netlify

### 2.1 Подготовка файлов
1. Скопируйте все файлы из папки `public/` в папку `netlify/`
2. Обновите `netlify/index.html` с URL вашего Heroku API

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
Замените все URL API на ваш Heroku URL:

```javascript
// В public/index.html, public/all-services.html и других
const API_BASE_URL = 'https://your-heroku-app.herokuapp.com';
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
curl https://your-heroku-app.herokuapp.com/
# Должен вернуть: {"status": "ok", "message": "L'ÎLE DE RÊVE API работает"}
```

### 4.2 Тест Telegram
```bash
curl https://your-heroku-app.herokuapp.com/api/test-telegram
# Должен отправить тестовое сообщение в Telegram
```

### 4.3 Тест фронтенда
1. Откройте ваш Netlify сайт
2. Заполните форму
3. Проверьте, что сообщения приходят в Telegram

## 🔧 Шаг 5: Настройка CORS (если нужно)

Если возникают ошибки CORS, добавьте в `heroku/app.py`:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['https://your-netlify-site.netlify.app'])
```

## 📱 Преимущества этого решения

✅ **Работает с мобильных операторов**  
✅ **Бесплатный хостинг** (Heroku + Netlify)  
✅ **Высокая доступность**  
✅ **Простота настройки**  
✅ **Масштабируемость**  

## 🚨 Устранение неполадок

### Проблема: Heroku не запускается
```bash
heroku logs --tail
# Проверьте логи на ошибки
```

### Проблема: API не отвечает
1. Проверьте переменные окружения: `heroku config`
2. Проверьте статус: `heroku ps`

### Проблема: CORS ошибки
1. Убедитесь, что `flask-cors` установлен
2. Проверьте настройки CORS в `app.py`

### Проблема: Telegram не работает
1. Проверьте `BOT_TOKEN` и `CHAT_ID`
2. Убедитесь, что бот активен
3. Проверьте права бота

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте логи: `heroku logs --tail`
2. Проверьте статус: `heroku ps`
3. Проверьте конфигурацию: `heroku config`

## 🎉 Готово!

Теперь ваш сайт работает на:
- **Фронтенд:** `https://your-site.netlify.app`
- **API:** `https://your-heroku-app.herokuapp.com`

Оба доступны с мобильных операторов! 📱 