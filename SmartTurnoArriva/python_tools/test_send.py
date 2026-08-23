import asyncio
from telegram import Bot

async def main():
    bot = Bot(token="8924812869:AAHOuXz5EY4Xtt_02X_lVP33J6jFQuN0ZGQ")
    try:
        await bot.send_message(chat_id="-1003972358311", text="test")
    except Exception as e:
        print(f"ERROR: {e}")

asyncio.run(main())
