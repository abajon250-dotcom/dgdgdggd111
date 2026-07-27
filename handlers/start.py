from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from config import NOTIFY_CHANNEL_ID, CHANNEL_USERNAME
from keyboards import main_menu, sub_check_keyboard, main_service_menu

router = Router()

async def check_sub(bot: Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=NOTIFY_CHANNEL_ID, user_id=user_id)
        if member.status in ["creator", "administrator", "member"]:
            return True
        return False
    except Exception:
        return True

@router.message(Command("start"))
async def cmd_start(message: Message, bot: Bot):
    if not await check_sub(bot, message.from_user.id):
        await message.answer(
            "❌ <b>Доступ ограничен!</b>\n\nПодпишитесь на канал, чтобы пользоваться ботом.",
            reply_markup=sub_check_keyboard(CHANNEL_USERNAME),
            parse_mode="HTML"
        )
        return

    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n🚀 Добро пожаловать в бота.",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "check_sub")
async def verify_subscription(callback: CallbackQuery, bot: Bot):
    if not await check_sub(bot, callback.from_user.id):
        await callback.answer("❌ Вы всё еще не подписаны!", show_alert=True)
        return

    await callback.message.delete()
    await callback.message.answer(
        "✅ <b>Подписка подтверждена!</b> Добро пожаловать.",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

@router.message(F.text == "➕ Создать заявку")
async def create_app_menu(message: Message, bot: Bot):
    if not await check_sub(bot, message.from_user.id):
        await message.answer("❌ Сначала подпишитесь на канал!", reply_markup=sub_check_keyboard(CHANNEL_USERNAME))
        return

    await message.answer(
        "📂 <b>Выберите категорию заявки:</b>",
        reply_markup=main_service_menu(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "back_to_main_menu")
async def back_to_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "📂 <b>Выберите категорию заявки:</b>",
        reply_markup=main_service_menu(),
        parse_mode="HTML"
    )