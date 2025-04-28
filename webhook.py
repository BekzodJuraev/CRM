from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import logging

ngrok_url = 'https://mayakcrm.uz/telegram_webhook/'  # Replace with your NGROK URL


bot = Bot(token="8184436447:AAF3WD9vRZO5C3IiY3WBgZ9I2Oht45ZCt3c")
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)
dp.middleware.setup(LoggingMiddleware())
#daphne -p 8000 Statron.asgi:application



async def set_webhook(dispatcher):
    try:
        webhook_url = f"{ngrok_url}"
        await bot.set_webhook(webhook_url)
        logging.info(f"Webhook set to {webhook_url}")
    except Exception as e:
        logging.error(f"Failed to set webhook: {e}")

# Add other handlers here

if __name__ == '__main__':
    executor.start_webhook(
        dispatcher=dp,
        webhook_path='/telegram_webhook/',
        on_startup=set_webhook,
        skip_updates=True,
        host='0.0.0.0',
        port=7000,
    )
