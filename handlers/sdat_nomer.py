from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from config import NOTIFY_CHANNEL_ID
from keyboards import numbers_type_inline, admin_sdat_buttons, main_menu

router = Router()


# Клик по кнопке "Номера" в главном меню
@router.callback_query(F.data == "category_numbers")
async def process_numbers_category(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "📱 Выберите сервис для сдачи номера:",
        reply_markup=numbers_type_inline()
    )


# Выбор Аденьги или Манимен для Номеров
@router.callback_query(F.data.in_(["service_num_adengi", "service_num_manimen"]))
async def process_numbers_service_choice(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    service_name = "АДЕНЬГИ" if "adengi" in callback.data else "МАНИМЕН"

    await state.update_data(service_type=service_name, category="Номера")
    await callback.message.edit_text(
        f"📱 Вы выбрали: <b>{service_name} (Сдать номер)</b>\n\nВведите номер телефона:",
        parse_mode="HTML"
    )