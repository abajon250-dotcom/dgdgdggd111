import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram import Bot

from config import ADMIN_ID, NOTIFY_CHANNEL_ID
from states import UserStates, AdminStates
from keyboards import (
    type_inline, admin_sbp_buttons, user_sbp_amount_prompt,
    main_menu, admin_sbp_confirm_buttons, cancel_keyboard
)
from database import create_application, update_app, get_app, add_user

router = Router()
logger = logging.getLogger(__name__)

@router.message(F.text == "💳 Запросить СБП")
async def sbp_start(message: Message, state: FSMContext):
    if await state.get_state():
        await message.answer("Предыдущее действие отменено.", reply_markup=main_menu())
        await state.clear()
    await state.set_state(UserStates.sbp_type)
    await message.answer("Выберите тип:", reply_markup=type_inline())

@router.callback_query(F.data.startswith("type_"), UserStates.sbp_type)
async def sbp_type_chosen(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    type_choice = "АДЕНЬГИ" if callback.data == "type_adengi" else "МАНИМЕН"
    user_id = callback.from_user.id
    username = callback.from_user.username or "нет username"
    add_user(user_id, username)

    app_id = create_application(user_id, username, None, 'sbp', type_choice)
    await state.update_data(app_id=app_id)

    app_text = (
        f"💰 Запрос СБП (ID: {app_id}):\n"
        f"Тип: {type_choice}\n"
        f"Пользователь: @{username} (ID: {user_id})"
    )

    kb = admin_sbp_buttons(app_id, user_id)
    admin_msg = await bot.send_message(ADMIN_ID, app_text, reply_markup=kb)
    try:
        channel_msg = await bot.send_message(NOTIFY_CHANNEL_ID, app_text, reply_markup=kb)
        ch_id = channel_msg.message_id
    except Exception as e:
        logger.error(f"Ошибка отправки в канал: {e}")
        ch_id = None

    update_app(app_id, admin_message_id=admin_msg.message_id, channel_message_id=ch_id)

    await state.set_state(UserStates.sbp_waiting_admin)
    await callback.message.edit_text("✅ Данные отправлены администратору. Ожидайте.")
    await callback.message.answer("Меню:", reply_markup=main_menu())

@router.callback_query(F.data.startswith("sbp_req_"))
async def sbp_admin_requisites(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    parts = callback.data.split("_")
    app_id = int(parts[2])
    user_id = int(parts[3])

    app = get_app(app_id)
    if not app:
        await callback.message.answer("❌ Заявка не найдена.")
        return
    if app['status'] in ('completed', 'cancelled'):
        await callback.message.answer("❌ Заявка уже завершена или отменена.")
        return

    await state.set_state(AdminStates.waiting_sbp_requisites)
    await state.update_data(sbp_app_id=app_id, sbp_user_id=user_id)
    await callback.message.answer("Введите реквизиты СБП (текст):")

@router.message(AdminStates.waiting_sbp_requisites)
async def sbp_requisites_sent(message: Message, state: FSMContext, bot: Bot):
    requisites = message.text
    data = await state.get_data()
    app_id = data.get('sbp_app_id')
    user_id = data.get('sbp_user_id')
    if not app_id or not user_id:
        await message.answer("Ошибка.")
        await state.clear()
        return

    update_app(app_id, sbp_requisites=requisites, status='requisites_sent')

    await bot.send_message(
        user_id,
        f"💳 Вот ваши реквизиты СБП:\n\n{requisites}\n\nПосле перевода нажмите кнопку ниже.",
        reply_markup=user_sbp_amount_prompt(app_id)
    )

    app = get_app(app_id)
    if app and app.get('channel_message_id'):
        try:
            await bot.edit_message_text(
                chat_id=NOTIFY_CHANNEL_ID,
                message_id=app['channel_message_id'],
                text=f"💳 Реквизиты отправлены (заявка {app_id})"
            )
        except Exception:
            pass
    await bot.send_message(NOTIFY_CHANNEL_ID, f"💳 Реквизиты отправлены (заявка {app_id})")

    await state.clear()
    await message.answer("✅ Реквизиты отправлены пользователю.")

@router.callback_query(F.data.startswith("sbp_amount_"))
async def sbp_user_amount_request(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    app_id = int(callback.data.split("_")[2])
    await state.set_state(UserStates.sbp_waiting_amount)
    await state.update_data(sbp_app_id=app_id)
    await callback.message.edit_text("Введите сумму, которую вы перевели (число):")
    await callback.message.answer("Введите сумму:", reply_markup=cancel_keyboard())

@router.message(UserStates.sbp_waiting_amount)
async def sbp_user_amount_received(message: Message, state: FSMContext, bot: Bot):
    amount = message.text
    try:
        float(amount)
    except ValueError:
        await message.answer("❌ Введите число.", reply_markup=cancel_keyboard())
        return

    data = await state.get_data()
    app_id = data.get('sbp_app_id')
    if not app_id:
        await message.answer("Ошибка. Начните заново.", reply_markup=main_menu())
        await state.clear()
        return

    app = get_app(app_id)
    if not app or app['status'] != 'requisites_sent':
        await message.answer("❌ Заявка не в нужном статусе.")
        await state.clear()
        return

    update_app(app_id, sbp_amount=amount, status='amount_reported')

    user_id = app['user_id']
    confirm_kb = admin_sbp_confirm_buttons(app_id, user_id)
    await bot.send_message(
        ADMIN_ID,
        f"💰 Пользователь перевел сумму {amount} по заявке {app_id}.\nПодтвердите выплату.",
        reply_markup=confirm_kb
    )
    await bot.send_message(
        NOTIFY_CHANNEL_ID,
        f"💰 Пользователь перевел сумму {amount} по заявке {app_id}."
    )

    await state.clear()
    await message.answer("✅ Сумма отправлена администратору на проверку.", reply_markup=main_menu())

@router.callback_query(F.data.startswith("sbp_confirm_"))
async def sbp_admin_confirm(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    parts = callback.data.split("_")
    app_id = int(parts[2])
    user_id = int(parts[3])

    app = get_app(app_id)
    if not app or app['status'] != 'amount_reported':
        await callback.message.answer("❌ Заявка не в статусе ожидания подтверждения.")
        return

    update_app(app_id, status='completed')

    await bot.send_message(user_id, f"✅ СБП переведена на сумму: {app['sbp_amount']}")
    await bot.send_message(NOTIFY_CHANNEL_ID, f"✅ СБП выплачена (заявка {app_id}) на сумму {app['sbp_amount']}")

    if app.get('channel_message_id'):
        try:
            await bot.edit_message_text(
                chat_id=NOTIFY_CHANNEL_ID,
                message_id=app['channel_message_id'],
                text=f"✅ СБП выплачена (заявка {app_id}) на сумму {app['sbp_amount']}"
            )
        except Exception:
            pass

    storage_key = StorageKey(bot.id, user_id, user_id)
    await state.storage.set_state(key=storage_key, state=None)
    await state.storage.set_data(key=storage_key, data={})

    await callback.message.edit_text(f"✅ Выплата по заявке {app_id} подтверждена.")

@router.callback_query(F.data.startswith("sbp_cancel_confirm_"))
async def sbp_admin_cancel_confirm(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    parts = callback.data.split("_")
    app_id = int(parts[2])
    user_id = int(parts[3])
    await state.set_state(AdminStates.waiting_cancel_reason)
    await state.update_data(cancel_app_id=app_id, cancel_user_id=user_id)
    await callback.message.answer("Введите причину отмены:")

@router.callback_query(F.data.startswith("sbp_cancel_"))
async def sbp_admin_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    parts = callback.data.split("_")
    app_id = int(parts[2])
    user_id = int(parts[3])
    await state.set_state(AdminStates.waiting_cancel_reason)
    await state.update_data(cancel_app_id=app_id, cancel_user_id=user_id)
    await callback.message.answer("Введите причину отмены:")