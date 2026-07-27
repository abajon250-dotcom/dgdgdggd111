import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN

# Импортируем все ваши роутеры из папки handlers
from handlers import start, cancel, sdat_nomer, zapros_sbp, admin


async def main():
    # Инициализация бота с парс-модом по умолчанию (HTML)
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # --- ПОДКЛЮЧЕНИЕ ВСЕХ РОУТЕРОВ ---
    # Порядок важен: сначала обработчики команд/меню, потом конкретные категории
    dp.include_router(start.router)
    dp.include_router(cancel.router)
    dp.include_router(zapros_sbp.router)
    dp.include_router(sdat_nomer.router)
    dp.include_router(admin.router)

    # Запуск поллинга
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    print("Бот успешно запущен и готов к работе!")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен.")