from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
from config import CHANNEL_USERNAME
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

        # Пропускаем команду /start и кнопку проверки подписки
        if isinstance(event, Message) and event.text and event.text.startswith("/start"):
            return await handler(event, data)
        if isinstance(event, CallbackQuery) and event.data == "check_sub":
            return await handler(event, data)

        bot = data["bot"]
        try:
            # Проверяем подписку именно на публичный канал
            member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user.id)
            if member.status not in ["creator", "administrator", "member"]:
                text = f"❌ Чтобы пользоваться ботом, подпишитесь на наш канал: {CHANNEL_USERNAME}"
                if isinstance(event, Message):
                    await event.answer(text, reply_markup=sub_check_keyboard(CHANNEL_USERNAME))
                elif isinstance(event, CallbackQuery):
                    await event.answer("❌ Сначала подпишитесь на канал!", show_alert=True)
                return
        except Exception as e:
            print(f"[Middleware Error] Не удалось проверить подписку на {CHANNEL_USERNAME}: {e}")

        return await handler(event, data)