import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
# Импортируем роутеры из папки handlers
from handlers import start, cancel, sdat_nomer, zapros_sbp, admin


async def main():
    # Инициализация бота с поддержкой HTML по умолчанию
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # РЕГИСТРАЦИЯ РОУТЕРОВ (Если какого-то нет здесь — кнопки из него работать не будут!)
    dp.include_router(start.router)
    dp.include_router(cancel.router)
    dp.include_router(sdat_nomer.router)
    dp.include_router(zapros_sbp.router)
    dp.include_router(admin.router)

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    # Запуск поллинга
    logger = logging.getLogger(__name__)
    logger.info("Бот успешно запущен и готов к работе!")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен!")