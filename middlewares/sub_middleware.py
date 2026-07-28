from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
from config import CHANNEL_ID
from keyboards import sub_check_keyboard


class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: Message | CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        user = event.from_user
        if not user:
            return await handler(event, data)

        # Отладка в консоль: видим кто и что пишет
        print(f"[DEBUG] Проверка подписки для пользователя ID: {user.id}")

        # Пропускаем кнопку проверки подписки
        if isinstance(event, CallbackQuery) and event.data == "check_sub":
            return await handler(event, data)

        bot = data["bot"]

        try:
            member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user.id)
            print(f"[DEBUG] Статус пользователя в канале {CHANNEL_ID}: {member.status}")

            # Если не подписан
            if member.status not in ["creator", "administrator", "member"]:
                text = f"❌ Чтобы пользоваться ботом, подпишитесь на наш канал: {CHANNEL_ID}"
                if isinstance(event, Message):
                    await event.answer(text, reply_markup=sub_check_keyboard(CHANNEL_ID))
                elif isinstance(event, CallbackQuery):
                    await event.answer("❌ Сначала подпишитесь на канал!", show_alert=True)
                return  # Блокируем выполнение дальше

        except Exception as e:
            print(f"[CRITICAL MIDDLEWARE ERROR] Ошибка проверки подписки: {e}")
            if isinstance(event, Message):
                await event.answer("⚠️ Ошибка настройки бота: проверьте, добавлен ли бот администратором в канал!")
            return

        return await handler(event, data)