from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from config import ADMIN_ID
from keyboards import main_menu, main_service_menu
from database import add_user

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, bot: Bot):
    add_user(message.from_user.id, message.from_user.username or "нет")
    is_admin = (message.from_user.id == ADMIN_ID)

    # ЕСЛИ ЭТО ГРУППА: отправляем приветствие без кнопок меню
    if message.chat.type != "private":
        await message.answer(f"👋 Привет, {message.from_user.first_name}!\nДобро пожаловать в бот.")
        return

    # ЕСЛИ ЭТО ЛИЧНЫЙ ЧАТ: отправляем с кнопками меню
    await message.answer(f"👋 Привет, {message.from_user.first_name}!\nДобро пожаловать в бот.",
                         reply_markup=main_menu(is_admin))

@router.callback_query(F.data == "check_sub")
async def verify_sub(callback: CallbackQuery, bot: Bot):
    is_admin = (callback.from_user.id == ADMIN_ID)
    await callback.message.answer("✅ Подписка проверена! Главное меню:", reply_markup=main_menu(is_admin))

@router.message(F.text == "➕ Создать заявку")
async def create_app(message: Message):
    await message.answer("📂 Выберите категорию заявки:", reply_markup=main_service_menu())

@router.callback_query(F.data == "back_to_main_menu")
async def back_menu(callback: CallbackQuery):
    await callback.message.edit_text("📂 Выберите категорию заявки:", reply_markup=main_service_menu())