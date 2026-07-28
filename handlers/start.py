from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from keyboards import main_menu, main_service_menu

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, bot: Bot):
    await message.answer(f"👋 Привет, {message.from_user.first_name}!\nДобро пожаловать в сервисный бот.", reply_markup=main_menu())

@router.callback_query(F.data == "check_sub")
async def verify_sub(callback: CallbackQuery, bot: Bot):
    await callback.message.delete()
    await callback.message.answer("✅ Подписка проверена! Главное меню:", reply_markup=main_menu())

@router.message(F.text == "➕ Создать заявку")
async def create_app(message: Message):
    await message.answer("📂 Выберите категорию заявки:", reply_markup=main_service_menu())

@router.callback_query(F.data == "back_to_main_menu")
async def back_menu(callback: CallbackQuery):
    await callback.message.edit_text("📂 Выберите категорию заявки:", reply_markup=main_service_menu())