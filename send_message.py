#pip install fastapi uvicorn httpx jinja2 python-multipart
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx  

app = FastAPI()

TELEGRAM_BOT_TOKEN = "токен_бота"  
TELEGRAM_CHAT_ID = "chat_id"  

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

async def send_to_telegram(message: str):
    """Отправляет сообщение в Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        return response.json()

@app.post("/send_message")
async def handle_form(
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...)
):
    try:
        telegram_msg = (
            f"<b>Новое сообщение с сайта L'ÎLE DE RÊVE</b>\n\n"
            f"<b>Имя:</b> {name}\n"
            f"<b>Email:</b> {email}\n"
            f"<b>Сообщение:</b>\n{message}"
        )
        
        result = await send_to_telegram(telegram_msg)
        
        return JSONResponse(
            content={"status": "success", "message": "Сообщение отправлено!"},
            status_code=200
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при отправке: {str(e)}"
        )

# тест 
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <h1>FastAPI + Telegram Bot</h1>
    <p>Сервер работает. Используйте POST /send_message для отправки данных.</p>
    """