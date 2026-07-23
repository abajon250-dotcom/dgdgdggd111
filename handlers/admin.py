import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram import Bot

from config import ADMIN_ID
from database import (
    get_stats, get_apps, get_app, get_all_users, get_all_users_with_status,
    ban_user, unban_user, is_user_banned, reject_application, update_app
)
from keyboards import main_menu, admin_panel
from states import AdminStates

router = Router()
logger = logging.getLogger(__name__)

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

# --- Команда для бана пользователя ---
@router.message(Command("ban"))
async def ban_user_cmd(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Нет прав.")
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Использование: /ban <user_id> [причина]")
        return
    try:
        user_id = int(args[1])
        reason = " ".join(args[2:]) if len(args) > 2 else None
        if is_user_banned(user_id):
            await message.answer("Пользователь уже забанен.")
            return
        ban_user(user_id, reason)
        await message.answer(f"✅ Пользователь {user_id} забанен. Причина: {reason or 'Не указана'}")
    except ValueError:
        await message.answer("ID должен быть числом.")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

# --- Команда для разбана пользователя ---
@router.message(Command("unban"))
async def unban_user_cmd(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Нет прав.")
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Использование: /unban <user_id>")
        return
    try:
        user_id = int(args[1])
        if not is_user_banned(user_id):
            await message.answer("Пользователь не забанен.")
            return
        unban_user(user_id)
        await message.answer(f"✅ Пользователь {user_id} разбанен.")
    except ValueError:
        await message.answer("ID должен быть числом.")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

# --- Команда для просмотра списка пользователей с банами ---
@router.message(Command("users"))
async def list_users_cmd(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Нет прав.")
        return
    users = get_all_users_with_status()
    if not users:
        await message.answer("Нет пользователей.")
        return
    text = "📋 **Список пользователей:**\n"
    for u in users:
        status = "⛔ Забанен" if u['banned'] else "✅ Активен"
        reason = f" (причина: {u['ban_reason']})" if u['ban_reason'] else ""
        text += f"ID: {u['user_id']} @{u['username'] or 'нет'} — {status}{reason}\n"
    await message.answer(text)

# --- Админ-панель (расширена) ---
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
    text += "\nДля деталей: /view <ID>\nДля отказа: /reject <ID> <причина>"
    await callback.message.edit_text(text, reply_markup=admin_panel())

# --- Команда для отказа в заявке ---
@router.message(Command("reject"))
async def reject_app_cmd(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Нет прав.")
        return
    args = message.text.split()
    if len(args) < 3:
        await message.answer("Использование: /reject <app_id> <причина>")
        return
    try:
        app_id = int(args[1])
        reason = " ".join(args[2:])
        app = get_app(app_id)
        if not app:
            await message.answer("Заявка не найдена.")
            return
        if app['status'] in ('completed', 'cancelled', 'rejected'):
            await message.answer(f"Заявка уже имеет статус {app['status']}.")
            return
        reject_application(app_id, reason)
        # Уведомляем пользователя
        user_id = app['user_id']
        bot = message.bot
        await bot.send_message(
            user_id,
            f"🚫 Ваша заявка #{app_id} отклонена.\nПричина: {reason}"
        )
        # Обновляем сообщение в канале (если есть)
        if app.get('channel_message_id'):
            try:
                await bot.edit_message_text(
                    chat_id=app.get('channel_id', NOTIFY_CHANNEL_ID),  # нужно передать NOTIFY_CHANNEL_ID из config
                    message_id=app['channel_message_id'],
                    text=f"🚫 Заявка #{app_id} отклонена. Причина: {reason}"
                )
            except Exception as e:
                logger.warning(f"Не удалось обновить канал: {e}")
        await message.answer(f"✅ Заявка {app_id} отклонена. Причина: {reason}")
    except ValueError:
        await message.answer("ID должен быть числом.")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

# Остальные функции (view, broadcast, admin_close) без изменений (из предыдущего финального ответа)
