import logging
import sqlite3
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from config import NOTIFY_CHANNEL_ID
from states import AdminStates, UserStates
from keyboards import admin_sdat_buttons, admin_sbp_buttons, user_code_prompt, main_menu
from database import update_app, get_app, get_connection

router = Router()
logger = logging.getLogger(__name__)


# 1. Запрос кода у пользователя (кнопка в группе)
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

    storage_key = StorageKey(bot.id, user_id, user_id)
    await state.storage.set_state(key=storage_key, state=UserStates.sdat_code_prompt)
    await state.storage.set_data(key=storage_key, data={'app_id': app_id})

    # Обновляем клавиатуру в группе, показывая количество попыток
    kb = admin_sdat_buttons(app_id, user_id)
    try:
        await callback.message.edit_reply_markup(reply_markup=kb)
    except Exception:
        pass


# 2. Кнопка «Завершить» в группе
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

    # Редактируем сообщение в группе
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


# 3. Кнопка «Отменить заявку» в группе — запускает процесс ввода причины
@router.callback_query(F.data.startswith("sdat_cancel_"))
async def sdat_admin_cancel_click(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    parts = callback.data.split("_")
    app_id = int(parts[2])
    user_id = int(parts[3])

    # Сохраняем ID заявки и пользователя в FSM администратора, который нажал кнопку
    await state.set_state(AdminStates.waiting_cancel_reason)
    await state.update_data(cancel_app_id=app_id, cancel_user_id=user_id)

    # Отправляем сообщение админу (лучше в личку или в ответ в группе)
    await callback.message.answer(
        f"❌ Введите причину отмены для заявки #{app_id} (отправьте следующим сообщением в чат):"
    )


# 4. Обработка введенной причины отмены от администратора в группе
@router.message(AdminStates.waiting_cancel_reason, F.chat.id == NOTIFY_CHANNEL_ID)
async def process_cancel_reason_group(message: Message, state: FSMContext, bot: Bot):
    reason = message.text.strip()
    data = await state.get_data()
    app_id = data.get("cancel_app_id")
    user_id = data.get("cancel_user_id")

    if app_id:
        update_app(app_id, status='cancelled', cancel_reason=reason)
        app = get_app(app_id)

        cancel_text = f"❌ <b>Заявка #{app_id} отменена администратором.</b>\nПричина: {reason}"

        # Уведомляем пользователя
        try:
            await bot.send_message(user_id, cancel_text, parse_mode="HTML")
        except Exception:
            pass

        # Редактируем сообщение с заявкой в группе
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

    # Удаляем сообщение администратора с причиной для порядка в группе
    try:
        await message.delete()
    except Exception:
        pass