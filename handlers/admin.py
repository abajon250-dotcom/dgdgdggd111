import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import Bot

from config import ADMIN_ID
from database import (
    get_stats, get_apps, get_app, get_all_users,
    ban_user, unban_user, is_user_banned
)
from keyboards import main_menu, admin_panel, admin_users_menu
from states import AdminStates

router = Router()
logger = logging.getLogger(__name__)

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

@router.message(Command("admin"))
async def admin_panel_cmd(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Нет прав.")
        return
    stats = get_stats()
    text = (
        "📊 **Админ-панель**\n\n"
        f"📌 Всего заявок: {stats['total']}\n"
        f"⏳ В ожидании: {stats['waiting']}\n"
        f"✅ Завершено: {stats['completed']}\n"
        f"❌ Отменено: {stats['cancelled']}\n"
        f"🚫 Отклонено: {stats['rejected']}\n"
        f"📱 Сдать номер: {stats['sdat']}\n"
        f"💰 СБП: {stats['sbp']}"
    )
    await message.answer(text, reply_markup=admin_panel())

@router.callback_query(F.data == "admin_stats")
async def admin_stats_cb(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет прав", show_alert=True)
        return
    await callback.answer()
    stats = get_stats()
    text = (
        "📊 **Статистика**\n\n"
        f"📌 Всего заявок: {stats['total']}\n"
        f"⏳ В ожидании: {stats['waiting']}\n"
        f"✅ Завершено: {stats['completed']}\n"
        f"❌ Отменено: {stats['cancelled']}\n"
        f"🚫 Отклонено: {stats['rejected']}\n"
        f"📱 Сдать номер: {stats['sdat']}\n"
        f"💰 СБП: {stats['sbp']}"
    )
    await callback.message.edit_text(text, reply_markup=admin_panel())

@router.callback_query(F.data == "admin_list")
async def admin_list_cb(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет прав", show_alert=True)
        return
    await callback.answer()
    apps = get_apps(15)
    if not apps:
        await callback.message.edit_text("📭 Заявок нет.", reply_markup=admin_panel())
        return
    text = "📋 **Последние заявки:**\n\n"
    for app in apps:
        emoji = {
            'waiting':'⏳',
            'code_requested':'🔑',
            'requisites_sent':'💳',
            'amount_reported':'💰',
            'completed':'✅',
            'cancelled':'❌',
            'rejected':'🚫'
        }.get(app['status'], '❓')
        text += f"{emoji} #{app['id']} | {app['service_type']} | {app['type_choice']} | {app['status']}\n"
    text += "\nДля деталей: /view <ID>"
    await callback.message.edit_text(text, reply_markup=admin_panel())

@router.message(Command("view"))
async def view_app_cmd(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Нет прав.")
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Укажите ID: /view 123")
        return
    try:
        app_id = int(args[1])
    except ValueError:
        await message.answer("ID должно быть числом.")
        return
    app = get_app(app_id)
    if not app:
        await message.answer("Заявка не найдена.")
        return
    text = (
        f"📄 **Заявка #{app['id']}**\n"
        f"👤 @{app['username']} (ID: {app['user_id']})\n"
        f"📱 Тип: {app['service_type']}\n"
        f"🔘 Выбор: {app['type_choice']}\n"
        f"📞 Телефон: {app['phone'] or '—'}\n"
        f"📊 Статус: {app['status']}\n"
        f"🕐 Создана: {app['created_at']}\n"
    )
    if app['code']:
        text += f"🔑 Код: {app['code']}\n"
    if app['sbp_amount']:
        text += f"💰 Сумма СБП: {app['sbp_amount']}\n"
    if app['sbp_requisites']:
        text += f"💳 Реквизиты: {app['sbp_requisites']}\n"
    if app['cancel_reason']:
        text += f"❌ Причина: {app['cancel_reason']}"
    await message.answer(text)

# ---------- Управление пользователями ----------

@router.callback_query(F.data == "admin_users")
async def admin_users_menu(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет прав", show_alert=True)
        return
    await callback.answer()
    await callback.message.edit_text(
        "👥 **Управление пользователями**\nВыберите действие:",
        reply_markup=admin_users_menu()
    )

@router.callback_query(F.data == "admin_ban")
async def admin_ban_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет прав", show_alert=True)
        return
    await callback.answer()
    await state.set_state(AdminStates.waiting_ban_user)
    await callback.message.edit_text(
        "Введите ID пользователя для бана (число):\nДля отмены нажмите /cancel"
    )

@router.message(AdminStates.waiting_ban_user)
async def admin_ban_user(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Нет прав.")
        await state.clear()
        return
    try:
        user_id = int(message.text)
    except ValueError:
        await message.answer("❌ Введите число.")
        return
    if is_user_banned(user_id):
        await message.answer("⚠️ Пользователь уже забанен.")
    else:
        ban_user(user_id)
        await message.answer(f"✅ Пользователь с ID {user_id} забанен.")
    await state.clear()
    # Показать меню управления пользователями
    await message.answer(
        "👥 **Управление пользователями**\nВыберите действие:",
        reply_markup=admin_users_menu()
    )

@router.callback_query(F.data == "admin_unban")
async def admin_unban_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет прав", show_alert=True)
        return
    await callback.answer()
    await state.set_state(AdminStates.waiting_unban_user)
    await callback.message.edit_text(
        "Введите ID пользователя для разбана (число):\nДля отмены нажмите /cancel"
    )

@router.message(AdminStates.waiting_unban_user)
async def admin_unban_user(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Нет прав.")
        await state.clear()
        return
    try:
        user_id = int(message.text)
    except ValueError:
        await message.answer("❌ Введите число.")
        return
    if not is_user_banned(user_id):
        await message.answer("⚠️ Пользователь не забанен.")
    else:
        unban_user(user_id)
        await message.answer(f"✅ Пользователь с ID {user_id} разбанен.")
    await state.clear()
    await message.answer(
        "👥 **Управление пользователями**\nВыберите действие:",
        reply_markup=admin_users_menu()
    )

@router.callback_query(F.data == "admin_back")
async def admin_back(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет прав", show_alert=True)
        return
    await callback.answer()
    stats = get_stats()
    text = (
        "📊 **Админ-панель**\n\n"
        f"📌 Всего заявок: {stats['total']}\n"
        f"⏳ В ожидании: {stats['waiting']}\n"
        f"✅ Завершено: {stats['completed']}\n"
        f"❌ Отменено: {stats['cancelled']}\n"
        f"🚫 Отклонено: {stats['rejected']}\n"
        f"📱 Сдать номер: {stats['sdat']}\n"
        f"💰 СБП: {stats['sbp']}"
    )
    await callback.message.edit_text(text, reply_markup=admin_panel())

# ---------- Рассылка ----------

@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет прав", show_alert=True)
        return
    await callback.answer()
    await state.set_state(AdminStates.waiting_broadcast)
    await callback.message.edit_text(
        "📨 Введите текст для рассылки (всем пользователям):\nДля отмены нажмите /cancel",
        reply_markup=None
    )

@router.message(AdminStates.waiting_broadcast)
async def broadcast_send(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Нет прав.")
        await state.clear()
        return
    text = message.text
    users = get_all_users()
    if not users:
        await message.answer("Нет пользователей для рассылки.")
        await state.clear()
        return
    sent = 0
    for uid in users:
        try:
            await bot.send_message(uid, text)
            sent += 1
        except Exception:
            pass
    await message.answer(f"✅ Рассылка выполнена. Отправлено {sent} из {len(users)} пользователей.")
    await state.clear()
    stats = get_stats()
    stats_text = (
        "📊 **Админ-панель**\n\n"
        f"📌 Всего заявок: {stats['total']}\n"
        f"⏳ В ожидании: {stats['waiting']}\n"
        f"✅ Завершено: {stats['completed']}\n"
        f"❌ Отменено: {stats['cancelled']}\n"
        f"🚫 Отклонено: {stats['rejected']}\n"
        f"📱 Сдать номер: {stats['sdat']}\n"
        f"💰 СБП: {stats['sbp']}"
    )
    await message.answer(stats_text, reply_markup=admin_panel())

@router.callback_query(F.data == "admin_close")
async def admin_close(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет прав", show_alert=True)
        return
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer("Панель закрыта.", reply_markup=main_menu())