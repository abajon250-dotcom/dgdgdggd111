from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from config import ADMIN_ID, NOTIFY_CHANNEL_ID
from states import AdminStates
from database import update_app

router = Router()


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📋 Инструкция админа", callback_data="admin_help")],
        ]
    )
    await message.answer("👑 **Панель администратора**\n\nУправляйте заявками прямо из уведомлений в канале.",
                         reply_markup=keyboard)


@router.callback_query(F.data == "admin_help")
async def admin_help(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return await callback.answer("❌ Доступ запрещен", show_alert=True)
    await callback.answer()
    await callback.message.answer(
        "📌 **Управление:**\n"
        "• Кнопка СБП в канале просит вас ввести реквизиты, после чего они отправятся клиенту.\n"
        "• Кнопка Номера запрашивает код у юзера."
    )


@router.callback_query(F.data.startswith("admin_req_sbp:"))
async def admin_req_sbp_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return await callback.answer("❌ Запрещено!", show_alert=True)

    _, app_id, target_id = callback.data.split(":")
    await state.update_data(sbp_app_id=int(app_id), sbp_target_user=int(target_id),
                            sbp_msg_id=callback.message.message_id)
    await state.set_state(AdminStates.waiting_sbp_details)

    await callback.answer()
    await callback.message.answer(f"💳 Введите реквизиты для отправки пользователю по заявке #{app_id}:")


@router.message(AdminStates.waiting_sbp_details)
async def send_sbp_details_to_user(message: Message, state: FSMContext, bot: Bot):
    if message.from_user.id != ADMIN_ID:
        return

    details = message.text.strip()
    data = await state.get_data()
    app_id = data.get("sbp_app_id")
    target_user = data.get("sbp_target_user")
    channel_msg_id = data.get("sbp_msg_id")

    await state.clear()
    update_app(app_id, status="Реквизиты отправлены")

    try:
        await bot.send_message(
            target_user,
            f"💳 **Получены реквизиты по заявке #{app_id}**:\n\n<code>{details}</code>\n\nПроизведите оплату по данным реквизитам.",
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка отправки пользователю: {e}")
        return

    await message.answer(f"✅ Реквизиты успешно отправлены пользователю по заявке #{app_id}!")

    try:
        await bot.edit_message_text(
            chat_id=NOTIFY_CHANNEL_ID,
            message_id=channel_msg_id,
            text=f"📥 <b>Заявка СБП #{app_id}</b>\nСтатус: 💳 Реквизиты отправлены администратором",
            parse_mode="HTML"
        )
    except Exception:
        pass


@router.callback_query(F.data.startswith("admin_req_code:"))
async def admin_req_code(callback: CallbackQuery, bot: Bot):
    if callback.from_user.id != ADMIN_ID:
        return await callback.answer("❌ Запрещено!", show_alert=True)
    _, app_id, target_id = callback.data.split(":")
    update_app(int(app_id), status="Запрос кода")
    await callback.answer("✅ Запрос отправлен!")
    await bot.send_message(int(target_id),
                           f"💬 Администратор запросил код по заявке #{app_id}! Отправьте его ответным сообщением.")


@router.callback_query(F.data.startswith("admin_done:"))
async def admin_done(callback: CallbackQuery, bot: Bot):
    if callback.from_user.id != ADMIN_ID:
        return await callback.answer("❌ Запрещено!", show_alert=True)
    _, app_id, target_id = callback.data.split(":")
    update_app(int(app_id), status="Завершено")
    await callback.answer("✅ Заявка закрыта!")
    await bot.send_message(int(target_id), f"✅ Ваша заявка #{app_id} успешно выполнена!")

    try:
        await callback.message.edit_text(f"{callback.message.text}\n\n<b>[✅ ЗАВЕРШЕНО]</b>", parse_mode="HTML")
    except Exception:
        pass


@router.callback_query(F.data.startswith("admin_cancel:"))
async def admin_cancel(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return await callback.answer("❌ Запрещено!", show_alert=True)
    _, app_id, target_id = callback.data.split(":")
    await state.update_data(c_app=int(app_id), c_user=int(target_id), c_msg=callback.message.message_id)
    await state.set_state(AdminStates.waiting_cancel_reason)
    await callback.answer()
    await callback.message.answer(f"❌ Введите причину отмены для заявки #{app_id}:")


@router.message(AdminStates.waiting_cancel_reason)
async def admin_reason(message: Message, state: FSMContext, bot: Bot):
    if message.from_user.id != ADMIN_ID:
        return
    reason = message.text.strip()
    data = await state.get_data()
    update_app(data["c_app"], status=f"Отменено: {reason}")
    await state.clear()

    await bot.send_message(data["c_user"], f"❌ Ваша заявка #{data['c_app']} отменена.\nПричина: {reason}")
    await message.answer("✅ Заявка отменена.")

    try:
        await bot.edit_message_text(
            chat_id=NOTIFY_CHANNEL_ID,
            message_id=data["c_msg"],
            text=f"❌ Заявка #{data['c_app']} ОТМЕНЕНА\nПричина: {reason}",
            parse_mode="HTML"
        )
    except Exception:
        pass