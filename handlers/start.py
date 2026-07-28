from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from config import NOTIFY_CHANNEL_ID, CHANNEL_USERNAME
from keyboards import main_menu, sub_check_keyboard, main_service_menu

router = Router()

async def check_sub(bot: Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=NOTIFY_CHANNEL_ID, user_id=user_id)
        return member.status in ["creator", "administrator", "member"]
    except Exception:
        return True

@router.message(Command("start"))
async def cmd_start(message: Message, bot: Bot):
    if not await check_sub(bot, message.from_user.id):
        return await message.answer("❌ Чтобы пользоваться ботом, подпишитесь на канал!", reply_markup=sub_check_keyboard(CHANNEL_USERNAME))
    await message.answer(f"👋 Привет, {message.from_user.first_name}!", reply_markup=main_menu())

@router.callback_query(F.data == "check_sub")
async def verify_sub(callback: CallbackQuery, bot: Bot):
    if not await check_sub(bot, callback.from_user.id):
        return await callback.answer("❌ Вы всё еще не подписаны на канал!", show_alert=True)
    await callback.message.delete()
    await callback.message.answer("✅ Подписка подтверждена!", reply_markup=main_menu())

@router.message(F.text == "➕ Создать заявку")
async def create_app(message: Message, bot: Bot):
    if not await check_sub(bot, message.from_user.id):
        return await message.answer("❌ Для создания заявки необходима подписка на канал!", reply_markup=sub_check_keyboard(CHANNEL_USERNAME))
    await message.answer("📂 Выберите категорию:", reply_markup=main_service_menu())

@router.callback_query(F.data == "back_to_main_menu")
async def back_menu(callback: CallbackQuery, bot: Bot):
    if not await check_sub(bot, callback.from_user.id):
        return await callback.message.edit_text("❌ Нужна подписка на канал!", reply_markup=sub_check_keyboard(CHANNEL_USERNAME))
    await callback.message.edit_text("📂 Выберите категорию:", reply_markup=main_service_menu())