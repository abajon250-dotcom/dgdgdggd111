from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from config import ADMIN_ID, NOTIFY_CHANNEL_ID
from states import AdminStates
from database import get_app, update_app

router = Router()

@router.callback_query(F.data.startswith(("admin_req_sbp:", "admin_req_code:")))
async def admin_req(callback: CallbackQuery, bot: Bot):
    if callback.from_user.id != ADMIN_ID: return await callback.answer("❌ Запрещено!", show_alert=True)
    _, app_id, target_id = callback.data.split(":")
    update_app(int(app_id), status="Запрос данных")
    await callback.answer("✅ Отправлено пользователю!")
    await bot.send_message(int(target_id), f"💬 Администратор запросил данные по заявке #{app_id}! Отправьте их в чат.")

@router.callback_query(F.data.startswith("admin_done:"))
async def admin_done(callback: CallbackQuery, bot: Bot):
    if callback.from_user.id != ADMIN_ID: return await callback.answer("❌ Запрещено!", show_alert=True)
    _, app_id, target_id = callback.data.split(":")
    update_app(int(app_id), status="Завершено")
    await callback.answer("✅ Заявка закрыта!")
    await bot.send_message(int(target_id), f"✅ Заявка #{app_id} выполнена!")
    await callback.message.edit_text(f"✅ Заявка #{app_id} ЗАВЕРШЕНА")

@router.callback_query(F.data.startswith("admin_cancel:"))
async def admin_cancel(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID: return await callback.answer("❌ Запрещено!", show_alert=True)
    _, app_id, target_id = callback.data.split(":")
    await state.update_data(c_app=int(app_id), c_user=int(target_id), c_msg=callback.message.message_id)
    await state.set_state(AdminStates.waiting_cancel_reason)
    await callback.answer()
    await callback.message.answer(f"❌ Введите причину отмены для #{app_id}:")

@router.message(AdminStates.waiting_cancel_reason)
async def admin_reason(message: Message, state: FSMContext, bot: Bot):
    if message.from_user.id != ADMIN_ID: return
    reason, data = message.text.strip(), await state.get_data()
    update_app(data["c_app"], status=f"Отменено: {reason}")
    await state.clear()
    await bot.send_message(data["c_user"], f"❌ Ваша заявка #{data['c_app']} отменена.\nПричина: {reason}")
    await message.answer("✅ Отменено.")
    await bot.edit_message_text(chat_id=NOTIFY_CHANNEL_ID, message_id=data["c_msg"], text=f"❌ Заявка #{data['c_app']} ОТМЕНЕНА\nПричина: {reason}")