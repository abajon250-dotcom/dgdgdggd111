import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram import Bot

from config import ADMIN_ID
from database import get_stats, get_apps, get_app, get_all_users, ban_user, unban_user
from keyboards import main_menu
from states import AdminStates

router = Router()
logger = logging.getLogger(__name__)


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


def admin_panel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📋 Заявки", callback_data="admin_list_0"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")
        ],
        [
            InlineKeyboardButton(text="🔨 Управление пользователями", callback_data="admin_users_menu"),
        ],
        [
            InlineKeyboardButton(text="📨 Сделать рассылку", callback_data="admin_broadcast")
        ],
        [
            InlineKeyboardButton(text="❌ Закрыть панель", callback_data="admin_close")
        ]
    ])


@router.message(Command("admin"))
async def admin_panel_cmd(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Нет прав.")
        return
    stats = get_stats()
    text = (
        "👑 **Панель администратора**\n\n"
        f"📌 Всего заявок: <b>{stats.get('total', 0)}</b>\n"
        f"⏳ В ожидании: <b>{stats.get('waiting', 0)}</b>\n"
        f"✅ Завершено: <b>{stats.get('completed', 0)}</b>\n"
        f"❌ Отменено: <b>{stats.get('cancelled', 0)}</b>\n"
        f"📱 Сдать номер: <b>{stats.get('sdat', 0)}</b>\n"
        f"💰 СБП: <b>{stats.get('sbp', 0)}</b>"
    )
    await message.answer(text, reply_markup=admin_panel_keyboard(), parse_mode="HTML")


@router.callback_query(F.data == "admin_stats")
async def admin_stats_cb(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет прав", show_alert=True)
        return
    await callback.answer()
    stats = get_stats()
    users_count = len(get_all_users())
    text = (
        "📊 **Расширенная статистика**\n\n"
        f"👥 Всего пользователей в базе: <b>{users_count}</b>\n"
        f"📌 Всего заявок: <b>{stats.get('total', 0)}</b>\n"
        f" ├ ⏳ В ожидании: <b>{stats.get('waiting', 0)}</b>\n"
        f" ├ ✅ Завершено: <b>{stats.get('completed', 0)}</b>\n"
        f" └ ❌ Отменено: <b>{stats.get('cancelled', 0)}</b>\n\n"
        f"📱 Направления:\n"
        f" ├ Сдать номер: <b>{stats.get('sdat', 0)}</b>\n"
        f" └ СБП: <b>{stats.get('sbp', 0)}</b>"
    )
    back_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="« Назад в меню", callback_data="admin_back")]
    ])
    await callback.message.edit_text(text, reply_markup=back_kb, parse_mode="HTML")


@router.callback_query(F.data == "admin_back")
async def admin_back_cb(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет прав", show_alert=True)
        return
    await callback.answer()
    stats = get_stats()
    text = (
        "👑 **Панель администратора**\n\n"
        f"📌 Всего заявок: <b>{stats.get('total', 0)}</b>\n"
        f"⏳ В ожидании: <b>{stats.get('waiting', 0)}</b>\n"
        f"✅ Завершено: <b>{stats.get('completed', 0)}</b>\n"
        f"❌ Отменено: <b>{stats.get('cancelled', 0)}</b>\n"
        f"📱 Сдать номер: <b>{stats.get('sdat', 0)}</b>\n"
        f"💰 СБП: <b>{stats.get('sbp', 0)}</b>"
    )
    await callback.message.edit_text(text, reply_markup=admin_panel_keyboard(), parse_mode="HTML")


# --- Меню управления пользователями (Бан / Разбан) ---

@router.callback_query(F.data == "admin_users_menu")
async def admin_users_menu_cb(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет прав", show_alert=True)
        return
    await callback.answer()

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔨 Заблокировать пользователя", callback_data="admin_ban_start")],
        [InlineKeyboardButton(text="🔓 Разблокировать пользователя", callback_data="admin_unban_start")],
        [InlineKeyboardButton(text="« Назад в меню", callback_data="admin_back")]
    ])
    await callback.message.edit_text(
        "👥 **Управление пользователями**\n\nВыберите действие:",
        reply_markup=kb,
        parse_mode="HTML"
    )


@router.callback_query(F.data == "admin_ban_start")
async def admin_ban_start_cb(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет прав", show_alert=True)
        return
    await callback.answer()
    await state.set_state(AdminStates.waiting_ban_id)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_users_menu")]
    ])
    await callback.message.edit_text(
        "🔨 Введите <b>Telegram ID</b> пользователя для блокировки:",
        reply_markup=kb,
        parse_mode="HTML"
    )


@router.message(AdminStates.waiting_ban_id)
async def process_ban_user(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    try:
        target_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ ID должен быть числом. Введите корректный ID:")
        return

    ban_user(target_id)
    await state.clear()

    await message.answer(f"✅ Пользователь с ID <code>{target_id}</code> успешно заблокирован.", parse_mode="HTML")

    stats = get_stats()
    text = (
        "👑 **Панель администратора**\n\n"
        f"📌 Всего заявок: <b>{stats.get('total', 0)}</b>\n"
        f"⏳ В ожидании: <b>{stats.get('waiting', 0)}</b>\n"
        f"✅ Завершено: <b>{stats.get('completed', 0)}</b>\n"
        f"❌ Отменено: <b>{stats.get('cancelled', 0)}</b>\n"
        f"📱 Сдать номер: <b>{stats.get('sdat', 0)}</b>\n"
        f"💰 СБП: <b>{stats.get('sbp', 0)}</b>"
    )
    await message.answer(text, reply_markup=admin_panel_keyboard(), parse_mode="HTML")


@router.callback_query(F.data == "admin_unban_start")
async def admin_unban_start_cb(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет прав", show_alert=True)
        return
    await callback.answer()
    await state.set_state(AdminStates.waiting_unban_id)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_users_menu")]
    ])
    await callback.message.edit_text(
        "🔓 Введите <b>Telegram ID</b> пользователя для разблокировки:",
        reply_markup=kb,
        parse_mode="HTML"
    )


@router.message(AdminStates.waiting_unban_id)
async def process_unban_user(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    try:
        target_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ ID должен быть числом. Введите корректный ID:")
        return

    unban_user(target_id)
    await state.clear()

    await message.answer(f"✅ Пользователь с ID <code>{target_id}</code> разблокирован.", parse_mode="HTML")

    stats = get_stats()
    text = (
        "👑 **Панель администратора**\n\n"
        f"📌 Всего заявок: <b>{stats.get('total', 0)}</b>\n"
        f"⏳ В ожидании: <b>{stats.get('waiting', 0)}</b>\n"
        f"✅ Завершено: <b>{stats.get('completed', 0)}</b>\n"
        f"❌ Отменено: <b>{stats.get('cancelled', 0)}</b>\n"
        f"📱 Сдать номер: <b>{stats.get('sdat', 0)}</b>\n"
        f"💰 СБП: <b>{stats.get('sbp', 0)}</b>"
    )
    await message.answer(text, reply_markup=admin_panel_keyboard(), parse_mode="HTML")


# --- Список заявок с пагинацией ---

@router.callback_query(F.data.startswith("admin_list_"))
async def admin_list_cb(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет прав", show_alert=True)
        return
    await callback.answer()

    offset = int(callback.data.split("_")[2])
    limit = 8

    apps = get_apps(limit=limit, offset=offset)

    if not apps and offset == 0:
        await callback.message.edit_text("📭 Заявок нет.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="« Назад", callback_data="admin_back")]
        ]))
        return

    text = f"📋 **Список заявок (стр. {offset // limit + 1}):**\n\n"

    keyboard_buttons = []
    for app in apps:
        emoji = {'waiting': '⏳', 'code_requested': '🔑', 'requisites_sent': '💳', 'amount_reported': '💰',
                 'completed': '✅', 'cancelled': '❌'}.get(app['status'], '❓')
        text += f"{emoji} <b>#{app['id']}</b> | {app['service_type']} | {app['type_choice']} | <code>{app['status']}</code>\n"
        keyboard_buttons.append(InlineKeyboardButton(text=f"📄 #{app['id']}", callback_data=f"admin_view_{app['id']}"))

    rows = [keyboard_buttons[i:i + 4] for i in range(0, len(keyboard_buttons), 4)]

    nav_buttons = []
    if offset > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"admin_list_{max(0, offset - limit)}"))
    nav_buttons.append(InlineKeyboardButton(text="🔄 Обновить", callback_data=f"admin_list_{offset}"))
    if len(apps) == limit:
        nav_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"admin_list_{offset + limit}"))

    rows.append(nav_buttons)
    rows.append([InlineKeyboardButton(text="« В меню админ-панели", callback_data="admin_back")])

    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")


@router.callback_query(F.data.startswith("admin_view_"))
async def admin_view_callback(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет прав", show_alert=True)
        return
    await callback.answer()

    app_id = int(callback.data.split("_")[2])
    app = get_app(app_id)
    if not app:
        await callback.answer("❌ Заявка не найдена.", show_alert=True)
        return

    text = (
        f"📄 **Заявка #{app['id']}**\n"
        f"👤 Пользователь: @{app['username']} (ID: <code>{app['user_id']}</code>)\n"
        f"📱 Услуга: <b>{app['service_type']}</b>\n"
        f"🔘 Тип: <b>{app['type_choice']}</b>\n"
        f"📞 Телефон: <code>{app['phone'] or '—'}</code>\n"
        f"📊 Статус: <code>{app['status']}</code>\n"
        f"🕐 Создана: {app['created_at']}\n"
    )
    if app['code']:
        text += f"🔑 Код: <b>{app['code']}</b>\n"
    if app['sbp_amount']:
        text += f"💰 Сумма СБП: <b>{app['sbp_amount']}</b>\n"
    if app['sbp_requisites']:
        text += f"💳 Реквизиты: <code>{app['sbp_requisites']}</code>\n"
    if app['cancel_reason']:
        text += f"❌ Причина отмены: <i>{app['cancel_reason']}</i>"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="« К списку заявок", callback_data="admin_list_0")]
    ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@router.message(Command("view"))
async def view_app_cmd(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Нет прав.")
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("⚠️ Укажите ID: /view 123")
        return
    try:
        app_id = int(args[1])
    except ValueError:
        await message.answer("❌ ID должно быть числом.")
        return

    app = get_app(app_id)
    if not app:
        await message.answer("❌ Заявка не найдена.")
        return

    text = (
        f"📄 **Заявка #{app['id']}**\n"
        f"👤 Пользователь: @{app['username']} (ID: <code>{app['user_id']}</code>)\n"
        f"📱 Услуга: <b>{app['service_type']}</b>\n"
        f"🔘 Тип: <b>{app['type_choice']}</b>\n"
        f"📞 Телефон: <code>{app['phone'] or '—'}</code>\n"
        f"📊 Статус: <code>{app['status']}</code>\n"
        f"🕐 Создана: {app['created_at']}\n"
    )
    if app['code']:
        text += f"🔑 Код: <b>{app['code']}</b>\n"
    if app['sbp_amount']:
        text += f"💰 Сумма СБП: <b>{app['sbp_amount']}</b>\n"
    if app['sbp_requisites']:
        text += f"💳 Реквизиты: <code>{app['sbp_requisites']}</code>\n"
    if app['cancel_reason']:
        text += f"❌ Причина отмены: <i>{app['cancel_reason']}</i>"

    await message.answer(text, parse_mode="HTML")


# --- Рассылка ---

@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет прав", show_alert=True)
        return
    await callback.answer()
    await state.set_state(AdminStates.waiting_broadcast)

    cancel_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить рассылку", callback_data="admin_back")]
    ])
    await callback.message.edit_text(
        "📨 **Массовая рассылка**\n\nВведите текст сообщения для отправки всем пользователям:",
        reply_markup=cancel_kb,
        parse_mode="HTML"
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
        await message.answer("📭 Нет пользователей для рассылки.")
        await state.clear()
        return

    sent = 0
    blocked = 0
    for uid in users:
        try:
            await bot.send_message(uid, text)
            sent += 1
        except Exception:
            blocked += 1

    await message.answer(
        f"✅ **Рассылка завершена!**\n\n"
        f"📬 Доставлено: <b>{sent}</b>\n"
        f"🚫 Заблокировали бота: <b>{blocked}</b>\n"
        f"👥 Всего в базе: <b>{len(users)}</b>",
        parse_mode="HTML"
    )
    await state.clear()

    stats = get_stats()
    stats_text = (
        "👑 **Панель администратора**\n\n"
        f"📌 Всего заявок: <b>{stats.get('total', 0)}</b>\n"
        f"⏳ В ожидании: <b>{stats.get('waiting', 0)}</b>\n"
        f"✅ Завершено: <b>{stats.get('completed', 0)}</b>\n"
        f"❌ Отменено: <b>{stats.get('cancelled', 0)}</b>\n"
        f"📱 Сдать номер: <b>{stats.get('sdat', 0)}</b>\n"
        f"💰 СБП: <b>{stats.get('sbp', 0)}</b>"
    )
    await message.answer(stats_text, reply_markup=admin_panel_keyboard(), parse_mode="HTML")


@router.callback_query(F.data == "admin_close")
async def admin_close(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет прав", show_alert=True)
        return
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer("🔒 Панель закрыта.", reply_markup=main_menu())