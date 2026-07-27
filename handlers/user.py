import logging
import re
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from config import NOTIFY_CHANNEL_ID
from states import UserStates
from keyboards import sbp_type_inline, numbers_type_inline, admin_sdat_buttons, admin_sbp_buttons, main_menu
from database import create_application, update_app

router = Router()
logger = logging.getLogger(__name__)


# --- КАТЕГОРИЯ: СБП ---
@router.callback_query(F.data == "category_sbp")
async def process_sbp_category(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "💳 Выберите сервис для СБП:",
        reply_markup=sbp_type_inline()
    )


@router.callback_query(F.data.in_(["service_sbp_adengi", "service_sbp_manimen"]))
async def process_sbp_service_choice(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    service_name = "АДЕНЬГИ" if "adengi" in callback.data else "МАНИМЕН"

    await state.update_data(service_type=f"{service_name} (СБП)", category="СБП")
    await state.set_state(UserStates.waiting_for_phone)  # Используем общее состояние ожидания ввода

    await callback.message.edit_text(
        f"💳 Вы выбрали: <b>{service_name} (СБП)</b>\n\nВведите номер телефона, привязанный к СБП:",
        parse_mode="HTML"
    )


# --- КАТЕГОРИЯ: НОМЕРА (СДАТЬ НОМЕР) ---
@router.callback_query(F.data == "category_numbers")
async def process_numbers_category(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "📱 Выберите сервис для сдачи номера:",
        reply_markup=numbers_type_inline()
    )


@router.callback_query(F.data.in_(["service_num_adengi", "service_num_manimen"]))
async def process_numbers_service_choice(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    service_name = "АДЕНЬГИ" if "adengi" in callback.data else "МАНИМЕН"

    await state.update_data(service_type=f"{service_name} (Номер)", category="Номера")
    await state.set_state(UserStates.waiting_for_phone)

    await callback.message.edit_text(
        f"📱 Вы выбрали: <b>{service_name} (Сдать номер)</b>\n\nВведите номер телефона:",
        parse_mode="HTML"
    )


# --- ПРОВЕРКА НОМЕРА И СОЗДАНИЕ ЗАЯВКИ ---
@router.message(UserStates.waiting_for_phone)
async def process_phone_validation(message: Message, state: FSMContext, bot: Bot):
    phone = message.text.strip()

    # Простейшая проверка номера на валидность (проверяем наличие цифр, длину от 10 до 12 символов)
    # Очищаем всё, кроме цифр и плюса
    cleaned_phone = re.sub(r'[^\d+]', '', phone)

    if len(cleaned_phone) < 10 or len(cleaned_phone) > 13:
        await message.answer(
            "❌ <b>Неверный формат номера!</b>\nПожалуйста, введите корректный номер телефона (например: <code>+79991234567</code> или <code>89991234567</code>):",
            parse_mode="HTML"
        )
        return

    data = await state.get_data()
    service_type = data.get("service_type", "СБП")
    category = data.get("category", "СБП")

    user_id = message.from_user.id
    username = message.from_user.username or "отсутствует"

    # Создаем заявку в базе данных
    app_id = create_application(
        user_id=user_id,
        username=username,
        service_type=service_type,
        phone=phone
    )

    # Формируем текст для канала
    if category == "СБП":
        text_for_channel = (
            f"📥 <b>Новая заявка СБП (ID: {app_id}):</b>\n"
            f"Сервис: {service_type}\n"
            f"Реквизиты/Телефон: <code>{phone}</code>\n"
            f"Пользователь: @{username} (ID: {user_id})\n"
            f"Статус: ⏳ Ожидание выплаты"
        )
        kb = admin_sbp_buttons(app_id, user_id)
    else:
        text_for_channel = (
            f"📥 <b>Новая заявка на номер (ID: {app_id}):</b>\n"
            f"Сервис: {service_type}\n"
            f"Телефон: <code>{phone}</code>\n"
            f"Пользователь: @{username} (ID: {user_id})\n"
            f"Статус: ⏳ Ожидание запроса кода"
        )
        kb = admin_sdat_buttons(app_id, user_id)

    try:
        sent_msg = await bot.send_message(
            chat_id=NOTIFY_CHANNEL_ID,
            text=text_for_channel,
            reply_markup=kb,
            parse_mode="HTML"
        )
        update_app(app_id, channel_message_id=sent_msg.message_id)
    except Exception as e:
        logger.error(f"Не удалось отправить заявку в канал: {e}")

    await state.clear()
    await message.answer(
        f"✅ <b>Заявка #{app_id} успешно создана!</b>\nОжидайте ответа администратора.",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )