import logging
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID
from database import add_user, get_user_banned

router = Router()
logger = logging.getLogger(__name__)


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


def get_main_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="📋 Мои заявки"), KeyboardButton(text="➕ Создать заявку")],
        [KeyboardButton(text="ℹ️ Информация"), KeyboardButton(text="📞 Поддержка")]
    ]
    if is_admin(user_id):
        keyboard.insert(0, [KeyboardButton(text="👑 Админ-панель")])
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите пункт меню..."
    )


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = message.from_user

    if get_user_banned(user.id):
        await message.answer("⛔ <b>Доступ ограничен.</b>\nВы заблокированы администратором бота.", parse_mode="HTML")
        return

    try:
        add_user(user.id, user.username or "no_username", user.full_name)
    except Exception as e:
        logger.error(f"Ошибка при добавлении пользователя в БД: {e}")

    greeting_text = (
        f"👋 Привет, <b>{user.first_name}</b>!\n\n"
        f"🚀 Добро пожаловать в бота.\n"
        f"Здесь ты можешь сдать свой номер под ММ, АД или запросить СБП и получить выплату моментом!\n\n"
        f"👇 <i>Воспользуйся меню ниже</i>"
    )

    await message.answer(
        text=greeting_text,
        reply_markup=get_main_keyboard(user.id),
        parse_mode="HTML"
    )


@router.message(F.text == "ℹ️ Информация")
async def info_handler(message: Message):
    if get_user_banned(message.from_user.id):
        return
    info_text = (
        "ℹ️ <b>О сервисе</b>\n\n"
        "⚡ Наш бот создан для максимально быстрой и безопасной обработки ваших запросов.\n"
        "🛡️ Все данные защищены, а вбиверы работает в автоматическом режиме 24/7.\n\n"
        "Если у вас возникли вопросы, обратитесь в поддержку."
    )
    await message.answer(info_text, parse_mode="HTML")


@router.message(F.text == "📞 Поддержка")
async def support_handler(message: Message):
    if get_user_banned(message.from_user.id):
        return
    support_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Написать администратору", url="https://t.me/YOUR_SUPPORT_USERNAME")]
    ])
    await message.answer(
        "🛠️ <b>Служба поддержки</b>\n\nЕсли у вас возникли проблемы или вопросы, нажмите кнопку ниже для связи с менеджером:",
        reply_markup=support_kb,
        parse_mode="HTML"
    )