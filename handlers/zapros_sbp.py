from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from config import NOTIFY_CHANNEL_ID
from keyboards import sbp_type_inline, admin_sbp_buttons, main_menu

router = Router()


# Клик по кнопке "СБП" в главном меню
@router.callback_query(F.data == "category_sbp")
async def process_sbp_category(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "💳 Выберите сервис для СБП:",
        reply_markup=sbp_type_inline()
    )


# Выбор Аденьги или Манимен для СБП
@router.callback_query(F.data.in_(["service_sbp_adengi", "service_sbp_manimen"]))
async def process_sbp_service_choice(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    service_name = "АДЕНЬГИ" if "adengi" in callback.data else "МАНИМЕН"

    await state.update_data(service_type=service_name, category="СБП")
    await callback.message.edit_text(
        f"💳 Вы выбрали: <b>{service_name} (СБП)</b>\n\nВведите номер телефона или реквизиты:",
        parse_mode="HTML"
    )