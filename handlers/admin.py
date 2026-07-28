import asyncio
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from config import ADMIN_ID, NOTIFY_CHANNEL_ID
from states import AdminStates
from database import update_app, get_total_users, get_total_applications, get_all_users

router = Router()


def get_admin_main_keyboard():
    """Главная клавиатура админ-панели со вкладками"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 Статистика", callback_data="admin_tab_stats"),
                InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_tab_broadcast")
            ],
            [
                InlineKeyboardButton(text="❌ Закрыть", callback_data="admin_close")
            ]
        ]
    )


@router.message(F.text == "👑 Админ-панель")
async def admin_panel_button(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return

    await state.clear()
    text = "👑 **Панель администратора**\n\nВыберите интересующий вас раздел с помощью кнопок ниже:"
    await message.answer(text, reply_markup=get_admin_main_keyboard(), parse_mode="HTML")


# --- ВКЛАДКА: СТАТИСТИКА (Только для админа) ---
@router.callback_query(F.data == "admin_tab_stats")
async def admin_stats_tab(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return await callback.answer("❌ Доступ запрещен", show_alert=True)

    users_count = get_total_users()
    apps_count = get_total_applications()

    text = (
        f"📊 **Статистика бота**\n\n"
        f"👥 Всего пользователей в базе: <code>{users_count}</code>\n"
        f"📂 Всего создано заявок: <code>{apps_count}</code>\n"
        f"🟢 Статус системы: <b>Работает стабильно</b>"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="admin_tab_main")]
        ]
    )
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


# --- ВКЛАДКА: РАССЫЛКА (МЕНЮ) (Только для админа) ---
@router.callback_query(F.data == "admin_tab_broadcast")
async def admin_broadcast_tab(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return await callback.answer("❌ Доступ запрещен", show_alert=True)

    await state.set_state(AdminStates.waiting_broadcast_text)

    text = (
        f"📢 **Массовая рассылка**\n\n"
        f"Отправьте текст сообщения, которое хотите разослать всем пользователям бота.\n"
        f"Поддерживается форматирование **HTML** (`<b>текст</b>`, `<i>текст</i>`, ссылки и т.д.)."
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отменить рассылку", callback_data="admin_tab_main")]
        ]
    )
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


# --- ВОЗВРАТ В ГЛАВНОЕ МЕНЮ АДМИНКИ ---
@router.callback_query(F.data == "admin_tab_main")
async def admin_tab_main(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await state.clear()

    text = "👑 **Панель администратора**\n\nВыберите интересующий вас раздел с помощью кнопок ниже:"
    await callback.message.edit_text(text, reply_markup=get_admin_main_keyboard(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "admin_close")
async def admin_close(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()


# --- ИСПОЛНЕНИЕ РАССЫЛКИ (Только для админа) ---
@router.message(AdminStates.waiting_broadcast_text)
async def execute_broadcast(message: Message, state: FSMContext, bot: Bot):
    if message.from_user.id != ADMIN_ID:
        return

    text_to_broadcast = message.text
    await state.clear()

    users = get_all_users()
    status_msg = await message.answer(f"🚀 Начинаю рассылку для {len(users)} пользователей...")

    success = 0
    blocked = 0

    for uid in users:
        try:
            await bot.send_message(uid, text_to_broadcast, parse_mode="HTML")
            success += 1
            await asyncio.sleep(0.05)
        except Exception:
            blocked += 1

    await status_msg.edit_text(
        f"✅ **Рассылка завершена!**\n\n"
        f"🟢 Успешно доставлено: {success}\n"
        f"🔴 Заблокировали бота: {blocked}"
    )


# --- УПРАВЛЕНИЕ ЗАЯВКАМИ ИЗ ГРУППЫ (Доступно воркерам и админам) ---

@router.callback_query(F.data.startswith("admin_req_sbp:"))
async def admin_req_sbp_start(callback: CallbackQuery, state: FSMContext):
    _, app_id, target_id = callback.data.split(":")
    await state.update_data(sbp_app_id=int(app_id), sbp_target_user=int(target_id),
                            sbp_msg_id=callback.message.message_id)
    await state.set_state(AdminStates.waiting_sbp_details)

    await callback.answer()
    await callback.message.answer(f"💳 Введите реквизиты для отправки пользователю по заявке #{app_id}:")


@router.message(AdminStates.waiting_sbp_details)
async def send_sbp_details_to_user(message: Message, state: FSMContext, bot: Bot):
    details = message.text.strip()
    data = await state.get_data()
    app_id = data.get("sbp_app_id")
    target_user = data.get("sbp_target_user")
    channel_msg_id = data.get("sbp_msg_id")

    if not app_id:
        return  # Если состояние не относится к сбп-реквизитам

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
            text=f"📥 <b>Заявка СБП #{app_id}</b>\nСтатус: 💳 Реквизиты отправлены",
            parse_mode="HTML"
        )
    except Exception:
        pass


@router.callback_query(F.data.startswith("admin_req_code:"))
async def admin_req_code(callback: CallbackQuery, bot: Bot):
    _, app_id, target_id = callback.data.split(":")
    update_app(int(app_id), status="Запрос кода")
    await callback.answer("✅ Запрос отправлен!")
    await bot.send_message(int(target_id),
                           f"💬 Администратор запросил код по заявке #{app_id}! Отправьте его ответным сообщением.")


@router.callback_query(F.data.startswith("admin_done:"))
async def admin_done(callback: CallbackQuery, bot: Bot):
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
    _, app_id, target_id = callback.data.split(":")
    await state.update_data(c_app=int(app_id), c_user=int(target_id), c_msg=callback.message.message_id)
    await state.set_state(AdminStates.waiting_cancel_reason)
    await callback.answer()
    await callback.message.answer(f"❌ Введите причину отмены для заявки #{app_id}:")


@router.message(AdminStates.waiting_cancel_reason)
async def admin_reason(message: Message, state: FSMContext, bot: Bot):
    reason = message.text.strip()
    data = await state.get_data()

    if not data.get("c_app"):
        return

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