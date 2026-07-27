import logging
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from config import NOTIFY_CHANNEL_ID
from states import UserStates
from keyboards import user_service_kb, admin_sdat_buttons, main_menu
from database import create_application, update_app

router = Router()
logger = logging.getLogger(__name__)


# Открытие меню выбора сервиса из главного меню
@router.callback_query(F.data == "service_menu")
async def open_service_menu(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "Выберите способ выплаты:",
        reply_markup=user_service_kb()
    )


# Обработчик выбора конкретного сервиса (СБП или Манимен)
@router.callback_query(F.data.in_(["service_sbp", "service_moneyman"]))
async def service_chosen(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    service_type = "СБП" if callback.data == "service_sbp" else "МАНИМЕН"

    await state.update_data(service_type=service_type)
    await state.set_state(UserStates.waiting_for_phone)

    await callback.message.edit_text(
        f"📱 Вы выбрали: <b>{service_type}</b>\n\nВведите номер телефона, привязанный к счету:",
        parse_mode="HTML"
    )


# Получение номера телефона и отправка заявки в канал администраторов
@router.message(UserStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext, bot: Bot):
    phone = message.text.strip()
    data = await state.get_data()
    service_type = data.get("service_type", "СБП")

    user_id = message.from_user.id
    username = message.from_user.username or "отсутствует"

    app_id = create_application(
        user_id=user_id,
        username=username,
        service_type=service_type,
        phone=phone
    )

    text_for_channel = (
        f"📥 <b>Новая заявка на выдачу (ID: {app_id}):</b>\n"
        f"Тип: {service_type}\n"
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