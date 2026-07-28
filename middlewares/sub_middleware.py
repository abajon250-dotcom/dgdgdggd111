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

        bot = data["bot"]

        try:
            member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user.id)

            if member.status not in ["creator", "administrator", "member"]:
                if isinstance(event, CallbackQuery) and event.data == "check_sub":
                    await event.answer("❌ Вы всё еще не подписаны на канал!", show_alert=True)
                    return

                text = f"❌ Чтобы пользоваться ботом, вы должны быть подписаны на наш канал:\n👉 {CHANNEL_ID}"

                if isinstance(event, Message):
                    await event.answer(text, reply_markup=sub_check_keyboard(CHANNEL_ID))
                elif isinstance(event, CallbackQuery):
                    await event.answer("❌ Сначала подпишитесь на канал!", show_alert=True)

                return
            else:
                if isinstance(event, CallbackQuery) and event.data == "check_sub":
                    try:
                        await event.message.delete()
                    except Exception:
                        pass
                    await event.message.answer("✅ Спасибо за подписку! Главное меню:",
                                               reply_markup=data.get("main_menu_markup"))

        except Exception as e:
            print(f"[CRITICAL MIDDLEWARE ERROR] Ошибка проверки подписки: {e}")
            if isinstance(event, Message):
                await event.answer("⚠️ Ошибка проверки подписки. Убедитесь, что бот добавлен администратором в канал!")
            elif isinstance(event, CallbackQuery):
                await event.answer("⚠️ Ошибка проверки подписки.", show_alert=True)
            return

        return await handler(event, data)