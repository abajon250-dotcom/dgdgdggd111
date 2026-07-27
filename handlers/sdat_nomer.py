import logging
import re
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from config import NOTIFY_CHANNEL_ID
from states import UserStates
from keyboards import numbers_type_inline, admin_sdat_buttons, main_menu
from database import create_application, update_app

router = Router()
logger = logging.getLogger(__name__)


# Открытие подменю Номеров
@router.callback_query(F.data == "category_numbers")
async def process_numbers_category(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "📱 Выберите сервис для сдачи номера:",
        reply_markup=numbers_type_inline()
    )


# Выбор конкретного сервиса для номера
@router.callback_query(F.data.in_(["service_num_adengi", "service_num_manimen"]))
async def process_numbers_choice(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    service_name = "АДЕНЬГИ" if "adengi" in callback.data else "МАНИМЕН"

    await state.update_data(service_type=f"{service_name} (Номер)")
    await state.set_state(UserStates.waiting_for_phone)

    await callback.message.edit_text(
        f"📱 Вы выбрали: <b>{service_name} (Сдать номер)</b>\n\nВведите номер телефона (11 цифр, начиная с +7 или 8):",
        parse_mode="HTML"
    )


# Жесткая проверка номера и создание заявки
@router.message(UserStates.waiting_for_phone)
async def process_phone_validation(message: Message, state: FSMContext, bot: Bot):
    phone = message.text.strip()
    digits_only = re.sub(r'\D', '', phone)

    # Строгая проверка: ровно 11 цифр, начинается на 7 или 8
    if not (len(digits_only) == 11 and (digits_only.startswith('7') or digits_only.startswith('8'))):
        await message.answer(
            "❌ <b>Неверный номер!</b>\nТребуется корректный российский номер телефона (11 цифр, например: <code>+79991234567</code> или <code>89991234567</code>).\n\nПопробуйте еще раз:",
            parse_mode="HTML"
        )
        return

    data = await state.get_data()
    service_type = data.get("service_type", "Номер")

    user_id = message.from_user.id
    username = message.from_user.username or "отсутствует"

    app_id = create_application(
        user_id=user_id,
        username=username,
        service_type=service_type,
        phone=phone
    )

    text_for_group = (
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
            text=text_for_group,
            reply_markup=kb,
            parse_mode="HTML"
        )
        update_app(app_id, channel_message_id=sent_msg.message_id)
    except Exception as e:
        logger.error(f"Не удалось отправить заявку в группу: {e}")

    await state.clear()
    await message.answer(
        f"✅ <b>Заявка #{app_id} успешно создана!</b>\nОжидайте ответа администратора.",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )