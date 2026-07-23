import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import Bot

from config import CHANNEL_ID, ADMIN_ID
from keyboards import main_menu, subscribe_check_keyboard
from database import add_user, is_user_banned, get_ban_reason

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    user_id = message.from_user.id
    username = message.from_user.username or "нет username"
    add_user(user_id, username)

    # Проверка бана
    if is_user_banned(user_id):
        reason = get_ban_reason(user_id)
        await message.answer(
            f"⛔ Вы забанены.\nПричина: {reason or 'Не указана'}"
        )
        return

    welcome = (
        "✨ Добро пожаловать! ✨\n\n"
        "Наши расценки:\n"
        "⭐ Комиссия за СБП – 30%\n"
        "💎 Комиссия за сдачу номера – 35%\n\n"
        "Для начала работы подпишитесь на наш канал."
    )
    await message.answer(welcome)
    await check_subscription(message, bot, state)

async def check_subscription(message: Message, bot: Bot, state: FSMContext):
    user_id = message.from_user.id
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        if member.status in ('member', 'administrator', 'creator'):
            await message.answer("Выберите действие:", reply_markup=main_menu())
        else:
            await message.answer(
                "❌ Вы не подписаны на канал. Подпишитесь и нажмите «Проверить подписку».",
                reply_markup=subscribe_check_keyboard(CHANNEL_ID)
            )
    except Exception as e:
        logger.error(f"Ошибка проверки подписки: {e}")
        await message.answer("⚠️ Не удалось проверить подписку. Попробуйте позже.")

@router.callback_query(F.data == "check_subscription")
async def check_subscription_cb(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await callback.answer()
    # Повторно проверяем подписку
    await check_subscription(callback.message, bot, state)
    await callback.message.delete()  # удаляем сообщение с кнопкой проверки
