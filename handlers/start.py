import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import Bot

from config import CHANNEL_ID, ADMIN_ID
from keyboards import main_menu, subscribe_check_keyboard
from database import add_user

router = Router()
logger = logging.getLogger(__name__)

# Допустимые статусы участника канала (включая restricted для пользователей с ограничениями)
VALID_STATUSES = ('member', 'administrator', 'creator', 'restricted')

async def is_subscribed(bot: Bot, user_id: int) -> bool:
    """Проверка наличия подписки пользователя на канал."""
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in VALID_STATUSES
    except Exception as e:
        logger.error(f"Ошибка проверки подписки для пользователя {user_id}: {e}")
        return False

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    user_id = message.from_user.id
    username = message.from_user.username or "нет username"
    add_user(user_id, username)

    welcome = (
        "✨ Добро пожаловать! ✨\n\n"
        "Наши расценки:\n"
        "⭐ Комиссия за СБП – 30%\n"
        "💎 Комиссия за сдачу номера – 35%\n\n"
        "Для начала работы подпишитесь на наш канал."
    )
    await message.answer(welcome)

    if await is_subscribed(bot, user_id):
        await message.answer("Выберите действие:", reply_markup=main_menu())
    else:
        await message.answer(
            "❌ Вы не подписаны на канал. Подпишитесь и нажмите «Проверить подписку».",
            reply_markup=subscribe_check_keyboard(CHANNEL_ID)
        )

@router.callback_query(F.data == "check_subscription")
async def check_subscription_cb(callback: CallbackQuery, bot: Bot, state: FSMContext):
    user_id = callback.from_user.id

    if await is_subscribed(bot, user_id):
        await callback.answer("✅ Подписка подтверждена!", show_alert=False)
        await callback.message.delete()
        await callback.message.answer("Выберите действие:", reply_markup=main_menu())
    else:
        await callback.answer("❌ Вы всё еще не подписаны на канал!", show_alert=True)