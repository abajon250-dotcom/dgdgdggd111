import re
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from config import NOTIFY_CHANNEL_ID
from states import UserStates
from keyboards import numbers_type_inline, admin_buttons, main_menu
from database import create_application, update_app

router = Router()

@router.callback_query(F.data == "category_numbers")
async def num_cat(callback: CallbackQuery):
    await callback.message.edit_text("📱 Выберите сервис для сдачи номера:", reply_markup=numbers_type_inline())

@router.callback_query(F.data.in_(["service_num_adengi", "service_num_manimen"]))
async def num_choice(callback: CallbackQuery, state: FSMContext):
    service = "Аденьги (Номер)" if "adengi" in callback.data else "Манимен (Номер)"
    await state.update_data(service_type=service)
    await state.set_state(UserStates.waiting_for_phone)
    await callback.message.edit_text("📱 Введите номер телефона (11 цифр, с +7 или 8):")

@router.message(UserStates.waiting_for_phone)
async def num_save(message: Message, state: FSMContext, bot: Bot):
    phone = message.text.strip()
    if len(re.sub(r'\D', '', phone)) != 11:
        return await message.answer("❌ Неверный формат! Введите корректно 11 цифр номера:")

    data = await state.get_data()
    service = data.get("service_type", "Номер")
    uid, uname = message.from_user.id, message.from_user.username or "нет"

    app_id = create_application(uid, uname, "Номер", service, phone)
    msg = await bot.send_message(
        NOTIFY_CHANNEL_ID,
        f"📥 <b>Заявка Номер #{app_id}</b>\nСервис: {service}\nТелефон: <code>{phone}</code>\nОт: @{uname} (<code>{uid}</code>)\nСтатус: ⏳ Ожидание",
        reply_markup=admin_buttons(app_id, uid, False),
        parse_mode="HTML"
    )
    update_app(app_id, channel_message_id=msg.message_id)

    await state.clear()
    await message.answer(f"✅ Заявка #{app_id} создана!", reply_markup=main_menu())