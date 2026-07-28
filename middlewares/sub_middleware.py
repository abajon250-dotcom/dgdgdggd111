from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
from config import NOTIFY_CHANNEL_ID, CHANNEL_USERNAME
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

        if isinstance(event, Message) and event.text and event.text.startswith("/start"):
            return await handler(event, data)
        if isinstance(event, CallbackQuery) and event.data == "check_sub":
            return await handler(event, data)

        bot = data["bot"]
        try:
            member = await bot.get_chat_member(chat_id=NOTIFY_CHANNEL_ID, user_id=user.id)
            if member.status not in ["creator", "administrator", "member"]:
                text = "❌ Чтобы пользоваться ботом, подпишитесь на наш Telegram-канал!"
                if isinstance(event, Message):
                    await event.answer(text, reply_markup=sub_check_keyboard(CHANNEL_USERNAME))
                elif isinstance(event, CallbackQuery):
                    await event.answer("❌ Сначала подпишитесь на канал!", show_alert=True)
                return
        except Exception:
            pass

        return await handler(event, data)