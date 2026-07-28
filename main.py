import asyncio, logging, sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config import BOT_TOKEN
from database import init_db
from handlers import start, sdat_nomer, zapros_sbp, admin, user_menu
from middlewares.sub_middleware import SubscriptionMiddleware


async def main():
    init_db()
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.message.middleware(SubscriptionMiddleware())
    dp.callback_query.middleware(SubscriptionMiddleware())

    for r in [start.router, zapros_sbp.router, sdat_nomer.router, admin.router, user_menu.router]:
        dp.include_router(r)

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    print("Бот полностью запущен и готов к работе!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())